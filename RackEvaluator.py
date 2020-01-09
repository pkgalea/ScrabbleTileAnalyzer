import psycopg2 as pg2
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import math

plt.style.use('ggplot')


class TileCondition:
    def __init__(self, letter, count, compare):
        self._letter = letter
        self._count = count
        self._compare = compare
    def get_lambda(self):
        if (self._compare=="=="):
            return lambda x: x.count(self._letter)== self._count
        if (self._compare=="<"):
            return lambda x: x.count(self._letter) < self._count
        if (self._compare==">"):
            return lambda x: x.count(self._letter) > self._count
        if (self._compare==">="):
            return lambda x: x.count(self._letter) >= self._count
        if (self._compare=="<="):
            return lambda x: x.count(self._letter) <= self._count
        if (self._compare=="!="):
            return lambda x: x.count(self._letter) != self._count        
        
    def get_label(self):
        if (self._compare=="=="):
            return "Exactly {:} {:}'s".format(self._count, self._letter)
        if (self._compare=="<"):
            return "Less than {:} {:}'s".format(self._count, self._letter)
        if (self._compare==">"):
            return "More than {:} {:}'s".format(self._count, self._letter)
        if (self._compare=="<="):
            return "{:} or less {:}'s".format(self._count, self._letter)
        if (self._compare==">="):
            return "{:} or more {:}'s".format(self._count, self._letter)
        if (self._compare=="!="):
            return "Does not have {:} {:}'s".format(self._count, self._letter)
    
    def get_opposite(self):
        if (self._compare=="=="):
            cond = "!="
        if (self._compare=="<"):
            cond= ">="
        if (self._compare==">"):
            cond="<="
        if (self._compare=="<="):
            cond=">"
        if (self._compare==">="):
            cond= "<"
        if (self._compare=="!="):
            cond = "=="
        return TileCondition(self._letter, self._count, cond)




class RackEvaluator:
    def __init__(self, control_conditions, test_conditions=None):
        self._control_conditions = control_conditions
        self._test_conditions = test_conditions
        self.control_y = None
        self.test_y = None
        self.control_label = None
        self.test_label = None
        self.control_n = None
        self.test_n = None
        self.control_y_bar = None
        self.test_y_bar = None
        self.ci_lower = None
        self.ci_upper = None
        self.mean_diff = None
        self.p_value = None
    

    def get_data(self):
        conn = pg2.connect(user='postgres',  dbname='scrabble', host='localhost', port='5432', password='myPassword')


        sql = """SELECT  movenum, turn_score, p2_rating as rating, rack
        from FullView where gamenum in (SELECT gamenum from fullP2games) and NOT is_challenge and
        gamenum not in (select game_num from bad_games) and
        is_player2 = ' 1' and length(rack) = 7 """

        sql +=  """ UNION SELECT movenum, turn_score, p1_rating as rating, rack
        from FullView where gamenum in (SELECT gamenum from fullP1games) and NOT is_challenge and
        gamenum not in (select game_num from bad_games) and
        is_player2 = ' 0' and length(rack) = 7 ORDER BY movenum"""


        df_good_p2 = pd.read_sql(sql ,con=conn)
        control = df_good_p2[df_good_p2.rack.apply(self._control_conditions[0].get_lambda())]
        test = df_good_p2[df_good_p2.rack.apply(self._test_conditions[0].get_lambda())]
        conn.close()
        return control, test


    def evaluate(self):

        if not self._test_conditions:
            self._test_conditions = [self._control_conditions[0].get_opposite()]
        control, test = self.get_data()
        report = ""
        if not control.shape[0] or not test.shape[0]:
            report = "There is not enough data"
            return None, report
        self.control_y = control["turn_score"]
        self.test_y = test["turn_score"]

        self.control_label = self._control_conditions[0].get_label()
        self.test_label = self._test_conditions[0].get_label()

        self.control_y_bar = round(np.mean(control["turn_score"]), 2)
        self.test_y_bar = round(np.mean(test["turn_score"]), 2)
        self.control_n = control.shape[0]
        self.test_n = test.shape[0]
        report += "Results:\n"
#        report += "     mean scores with {:}: {:}, (n={:})\n".format(self._control_conditions[0].get_label(), round(self.control_y_bar), 2), self.control_n)
#        report += "     mean score with {:}: {:}, (n={:})\n".format(self._test_conditions[0].get_label(), round(self.test_y_bar), 2), 
#                                                self.test_n)

#        report += "Test for equality of means:\n"
        self.p_value = stats.ttest_ind(control.turn_score, test.turn_score, equal_var=False).pvalue
#        if self.p_value < 0.05:
#            report += "     We reject the hypothesis that the two distributions are equal."
#        else:
#            report += "     We do not have enough evidence to reject the hypothesis that the two distributions are equal."
#        report += "     (p-value: {:})\n\n".format(self.p_value) 
        control_var = np.var(control["turn_score"])
        test_var = np.var(test["turn_score"])
        self.mean_diff = self.test_y_bar - self.control_y_bar
        df=self.control_n + self.test_n - 2
        pooled_std_dev = math.sqrt( ((self.control_n-1)*control_var + (self.test_n-1)*test_var)/df)
        std_err = pooled_std_dev * math.sqrt(1/self.control_n + 1/self.test_n)
 
        MoE = stats.norm.ppf(0.975) * std_err 
        self.ci_lower = self.mean_diff - MoE
        self.ci_upper = self.mean_diff + MoE

        report += "Measure of effect:\n"
 #       report += "I can say with 95% confidence that a rack with {:} will score between [{:}, {:}] points than a rack with {:}".format(self.test_label, self.mean_diff - MoE, self.mean_diff + MoE, control_label)



        return True  

if __name__ == "__main__":
    re = RackEvaluator([TileCondition('A', 1, "<")])
    re.evaluate()
        