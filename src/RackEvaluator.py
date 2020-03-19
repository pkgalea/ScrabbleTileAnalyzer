import psycopg2 as pg2
import pandas as pd

import numpy as np
from scipy import stats
import math



class TileCondition:
    '''
        Simple class that represents a condition for a rack.  
        Examples:
            "More than 2 A's"
            "Exactly One Q"
            "No T's"
    '''

    def __init__(self, letter, count, compare):
        '''
            The Constructor for the TileCondition Class

            Parameters:
                letter(str): The letter to be evaluated  (e.g "Q")
                count(int): The numerical condition  (e.g. 2)
                compare(str): The compare condition (e.g "==")
        '''
        self._letter = letter
        self._count = count
        self._compare = compare


    def get_lambda(self):
        """ 
        Returns the appropriate lambda function for this condition
    
        Parameters: 
        None
        
        Returns: 
        (lambda): lambda function that represents this condition

        """
        if (self._compare=="=="):
            return lambda x: x.count(self._letter)== self._count
        if (self._compare==">="):
            return lambda x: x.count(self._letter) >= self._count
        if (self._compare=="<="):
            return lambda x: x.count(self._letter) <= self._count
        if (self._compare=="!="):
            return lambda x: x.count(self._letter) != self._count        

         
    def get_label(self):
        """ 
        Returns a nicely formatted description string for this condition
  
        Parameters: 
        None
    
        Returns: 
        (str): a nicely formatted description string for this condition
        """   
        if (self._compare=="=="):
            return "Exactly {:} {:}'s".format(self._count, self._letter)
        if (self._compare=="<="):
            return "{:} or less {:}'s".format(self._count, self._letter)
        if (self._compare==">="):
            return "{:} or more {:}'s".format(self._count, self._letter)
        if (self._compare=="!="):
            return "Does not have {:} {:}'s".format(self._count, self._letter)
    



class RackEvaluator:
    '''
        Class to conduct the statistical test for the difference in means between samples of two racks.  With the given condition 

        Attributes:


    '''
    def __init__(self, control_conditions, test_conditions=None):
        ''' 
            Constructor for the RackEvaluator Class
            Parameters: 
                control_conditions (TileCondition):  Condition for the Control Class
                test_condidtions (TileCondition): Conditions for the test Class
                control_y (Series): The scores for the control group
                test_y (Series): The scores for the test group
                control_label(str): The label for the control group
                test_label(str): The label for the test group
                control_n(int): The sample size for the control group
                test_n(int): The sample size for the test group
                ci_lower(float): Lower Bound of the confidence interval
                ci_upper(float): Upper Bound of the confidence interval
                mean_diff(float): The difference of means between the test and control groups
                p_value(float): The p value of the z test.
        '''
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
        """ 
        Hits PSql to get the Data to be analyzed, divided in control and test groups (as pandas dataframes)
    
        Parameters: 
        None
        
        Returns: 
        (Pandas DataFrame, Pandas Dataframe): Control Group, Test Group
        
        """ 
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

    def calculate_confidence_interval(self, control, test):
        """ 
        Calculates the confidence interval for the effect on the next turn score of having the test rack as opposed to the control rack
    
        Parameters: 
        control(Pandas Dataframe): The control group
        test (Pandas Datafame): The test group
        
        Returns: None
        
        """
        control_var = np.var(control["turn_score"])
        test_var = np.var(test["turn_score"])
        df=self.control_n + self.test_n - 2
        pooled_std_dev = math.sqrt( ((self.control_n-1)*control_var + (self.test_n-1)*test_var)/df)
        std_err = pooled_std_dev * math.sqrt(1/self.control_n + 1/self.test_n)
 
        MoE = stats.norm.ppf(0.975) * std_err 
        self.ci_lower = self.mean_diff - MoE
        self.ci_upper = self.mean_diff + MoE


    def evaluate(self):
        """ 
        gets the data from sql and cacluates the mean, pvalue and confidence interval for the statistical test
    
        Parameters: None
        Returns: 
        (bool): True if there was enough data to run the test
        (str): Report if there was a problem
        
        """
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
        self.p_value = stats.ttest_ind(control.turn_score, test.turn_score, equal_var=False).pvalue
        self.mean_diff = self.test_y_bar - self.control_y_bar
        self.calculate_confidence_interval(control, test)
        return True  

if __name__ == "__main__":
    re = RackEvaluator([TileCondition('A', 1, "<")], [TileCondition('A', 1, "<")])
    re.evaluate()
        