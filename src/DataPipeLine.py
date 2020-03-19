from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import bs4
import time


class CrossTablesDownloader:
    """ 
    Connects to MongoDB and gets the scrabble collections
  
    Parameters: 
    none
  
    Returns: 
    none
  
    """
    def __init__(self):
        client = MongoClient("mongodb://localhost:27017/")
        self._scrabble_db = client[ "scrabble" ]
        self._pages_collection = self._scrabble_db[ "pages_collection" ]
        self._fgames_collection = self._scrabble_db[ "fgames_collection"]


    def get_player_name_and_id(self,link):
        """ 
        Extended description of function. 
    
        Parameters: 
        arg1 (int): Description of arg1 
    
        Returns: 
        int: Description of return value 
    
        """
        return link.text, link['href'].split("p=")[1]



    def get_non_linked_player_names(self, player_names):
        """ 
        If the players aren't hyperlinked, get just the player names

        Splits the string on ' vs. '
    
        Parameters: 
        player_names: a string of the player's names
    
        Returns: 
        p1_name, p2_name: two strings of each player's name
    
        """       
        players_split = player_names.split(" vs. ")
        if (len(players_split)==1):
            p1_name = ""
            p2_name = ""
        else:
            p1_name = players_split[0]
            p2_name = players_split[1].rstrip()
        return p1_name, p2_name

 
    def handle_single_linked_player(self, players, p1_name, p1_id):
        """ 
        Get's player names and ids if only one is hyperlinked
    
        returns both player's names.
        Looks to see which player is hyperlinked and gets that id as well.
    
        Parameters: 
        player_names: A string of the players (one is hyperlinked)
        
        Returns: 
        p1_name, p1_id, p2_name, p2_id

        """
        player_split = players.text.split(' vs. ')
        if player_split[0]==p1_name:
            p2_name = player_split[1].split("\n")[0].rstrip()
            p2_id=""
        elif player_split[1]==p1_name:
            p2_name = p1_name
            p2_id = p1_id
            p1_name = player_split[0]
        else:
            print ("XXXXXXXXXXXXXXERRORXXXXXXXXXXXXXXX")
        return p1_name, p1_id, p2_name, p2_id

    def get_linked_player_names(self, player_links, players):
        p1_name, p1_id = self.get_player_name_and_id(player_links[0])    
        if len(player_links)==1:
            p1_name, p1_id, p2_name, p2_id = self.handle_single_linked_player(players, p1_name, p1_id)
        else:     
            p2_name, p2_id = self.get_player_name_and_id(player_links[1])
        return p1_name, p1_id, p2_name, p2_id

    def get_game_info(self, game):
        """ 
        Gets high level game info from the beautiful soup object of a game (e.g. player names, lexicon)
        returns game id, lexicon, player 1 id, player 1 name, player 2 id, player 2 name
        
        Parameters: 
        game(beautiful soup object): A single row of game data from the list of game pages 
        
        Returns: 
        str, str, str, str, str, str: gameid, lexicon, p1_id, p1_name, P2_id, p2_name

        """
        p1_id = p2_id = "-1"
        p1_name = p2_name = ""
        gameid = game.find('a')['href'].split("u=")[1]
        lexicon = game.find_all('td', "tdc nobr")[1].text
        players = game.next_element.next_element.next_element.next_element.next_element
        if (lexicon):
            players = players.next_element 
        else:
            lexicon = "     "
        player_links = players.find_all('a')
        if player_links:
            p1_name, p1_id, p2_name, p2_id = self.get_linked_player_names(player_links, players)
        else:
            p1_name, p2_name = self.get_non_linked_player_names(players.next_element)
        
        return gameid, lexicon, p1_id, p1_name, p2_id, p2_name



    def add_game_to_collection(self, gameid, lexicon, p1_id, p1_name, p2_id, p2_name):
        """ 
        Downloads a full game page from the pages collecion and inserts it into fgames collection in mongodb.

        Parameters: 
        gameid (str): The cross tables id of the game
        lexicon (str):  The dictionary used for the game
        p1_id (str): The id of the 1st player
        p1_name (str): The name of the 1st player
        p2_id (str): The id of the 2nd player
        p2_name (str): The name of the 2nd player
        
        Returns: 
        bool: if the game was successfully 
        """
        if (self._fgames_collection.find({'game_num': gameid}).count() != 0):
            return False
        else:
            with open("download.log", "w+") as logf:
                print ("     GameID: {:}   Lexicon: {:}   P1:({:},{:}) P2:({:},{:})".format(gameid, lexicon, p1_name, p1_id, p2_name, p2_id))
                    
                try:
                        url = "https://www.cross-tables.com/annotated.php?u=" + gameid
                        r = requests.get(url, headers={"User-Agent": "XY"})
                        if (r.status_code==200):
                            self._fgames_collection.insert_one({"game_num": gameid, "lexicon": lexicon, "p1_name": p1_name, "p1_id": p1_id, "p2_name": p2_name, "p2_id": p2_id, "content": r.text})
                        else:
                            print ("error", gameid)
                        time.sleep(1)

                except Exception as e:     
                    logf.write("Failed to download {0}\n".format(gameid))
        return True

    def get_list_of_games_page(self, page_index=1):
        """ 
        Downloads raw game pages from cross-tables.  Parses those pages and stores them as mongo database.

        Parameters: page_index:  The index of the page to start downloading from.
        
        Returns: 
        request: The result of the requests.get of the entire list of pages.
        """
        url = "https://www.cross-tables.com/annolistself.php?offset=" + str(page_index)
        r = requests.get(url, headers={"User-Agent": "XY"})
        print(page_index, r.status_code)
        if (r.status_code==200):
            pass
#                new_pages_collection.insert_one({"page_num": i, "content": r.text})
        else:
            print ("error", page_index)
            return None
        return r
    
    def download_games(self):
        """ 
        Downloads raw game pages from cross-tables.  Parses those pages and stores them as mongo database.

        Parameters: None
        
        Returns: None
        """
        c = 0
        all_games_found = False
        page_index = 1
        while not all_games_found:
            r = self.get_list_of_games_page(page_index)

            print(c)
            c+=1
            soup = BeautifulSoup(r.content, 'html.parser')
            for i in range (1, 101):
                game = soup.find(id="row"+str(i))
                if not game:
                    return

                gameid, lexicon, p1_id, p1_name, p2_id, p2_name = self.get_game_info(game)              
                if not self.add_game_to_collection(gameid, lexicon, p1_id, p1_name, p2_id, p2_name):
                    return;   
            page_index +=1

                             
                    
if __name__ == "__main__":
    ctd = CrossTablesDownloader()
    ctd.download_games()
