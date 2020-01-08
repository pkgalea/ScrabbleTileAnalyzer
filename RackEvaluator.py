import psycopg2 as pg2
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

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
        fig, axes = plt.subplots(1, 1, figsize=(20, 5))
        if not self._test_conditions:
            self._test_conditions = [self._control_conditions[0].get_opposite()]
        control, test = self.get_data()
        report = ""
        if (control.shape[0]):
            control_y_bar = round(np.mean(control["turn_score"]), 2)
            test_y_bar = round(np.mean(test["turn_score"]), 2)
            control_n = control.shape[0]
            test_n = test.shape[0]
            report += "mean scores with {:}: {:}, ({:})\n".format(self._control_conditions[0].get_label(), round(np.mean(control["turn_score"]), 2), 
                                                    control_n)
            report += "mean score with {:}: {:}, ({:})\n".format(self._test_conditions[0].get_label(), round(np.mean(test["turn_score"]), 2), 
                                                    test_n)


            report += "Score p-value: %3f" % stats.ttest_ind(control.turn_score, test.turn_score, equal_var=False).pvalue
        control_std_err = np.std(control["turn_score"])/len(n)
        test_std_err = np.std(test["turn_score"])/len()
    #    m = Matcher(control, test, yvar="turn_score", exclude=["rack"])
    #   print(control.shape, test.shape)
    #    print (np.mean(control['rating']))
    #    print (np.mean(test['rating']))
        axes.hist(control["turn_score"], bins=300, density=True, alpha = .5, color='blue', edgecolor='black', linewidth=1.2, label=self._control_conditions[0].get_label())
        axes.hist(test["turn_score"], bins=300, density=True, alpha=.5, edgecolor='black', linewidth=1.2, label=self._test_conditions[0].get_label(), color="green")
        axes.axvline(control_y_bar, color="blue")
        axes.axvline(test_y_bar, color="green")
        axes.legend()
        axes.set_xlim(left=-10, right=150)
     #   axes.set_ylim(bottom=0, top =.1)
     #   print(" ")
        return axes, report  

if __name__ == "__main__":
    re = RackEvaluator([TileCondition('A', 1, "<")])
    re.evaluate()
        