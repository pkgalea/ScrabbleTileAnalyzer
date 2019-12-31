from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import bs4
import time

class CrossTablesDownloader:
    def __init__(self):
        
        client = MongoClient("mongodb://localhost:27017/")
        self._scrabble_db = client[ "scrabble" ]
        self._pages_collection = self._scrabble_db[ "pages_collection" ]
        self._games_collection = self._scrabble_db[ "games_collection" ]
        self._fgames_collection = self._scrabble_db[ "fgames_collection"]

    def get_player_name_and_id(self,link):
        return link.text, link['href'].split("p=")[1]

    def get_non_linked_player_names(self, player_names):
        players_split = player_names.split(" vs. ")
        if (len(players_split)==1):
            p1_name = ""
            p2_name = ""
        else:
            p1_name = players_split[0]
            p2_name = players_split[1].rstrip()
        return p1_name, p2_name

    def handle_single_linked_player(self, players, p1_name, p1_id):
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
        gameid = game.find('a')['href'].split("u=")[1]
        lexicon = game.find_all('td', "tdc nobr")[1].text
        players = game.next_element.next_element.next_element.next_element.next_element
        if (lexicon):
            players = players.next_element 
        else:
            lexicon = "     "
        player_links = players.find_all('a')
        return gameid, lexicon, players, player_links

    def download_games(self):
        c = 0
        i=1
#        games_collection = scrabble_db[ "games_collection" ]
        for p in self._pages_collection.find({'page_num': {"$gt": 0}}):  #({'page_num':15501}):
            print(c)
            c+=1
        #    print(p['content'])
            page_num = p['page_num']
            print (page_num)
            soup = BeautifulSoup(p['content'], 'html.parser')
            for i in range (1, 101):
                game = soup.find(id="row"+str(i))
                if not game:
                    return
                p1_id = p2_id = "-1"
                p1_name = p2_name = ""
                gameid, lexicon, players, player_links = self.get_game_info(game)

                if player_links:
                    p1_name, p1_id, p2_name, p2_id = self.get_linked_player_names(player_links, players)
                else:
                    p1_name, p2_name = self.get_non_linked_player_names(players.next_element)

                    
                # print ("     GameID: {:}   Lexicon: {:}   P1:({:},{:}) P2:({:},{:})".format(gameid, lexicon, p1_name, p1_id, p2_name, p2_id))
                # if (self._games_collection.find({'game_num': gameid}).count() == 0):
                #     gamefolder = str(int(gameid)//100)
                #     url = "https://www.cross-tables.com/annotated/selfgcg/" +str(gamefolder) + "/anno" + gameid + ".gcg"
                #     r = requests.get(url, headers={"User-Agent": "XY"})
                #     if (r.status_code==200):
                #         self._games_collection.insert_one({"game_num": gameid, "content": r.text})
                #     else:
                #         print ("error", i)
                #     time.sleep(3)

                with open("download.log", "w+") as logf:
                    print ("     GameID: {:}   Lexicon: {:}   P1:({:},{:}) P2:({:},{:})".format(gameid, lexicon, p1_name, p1_id, p2_name, p2_id))
                    if (self._fgames_collection.find({'game_num': gameid}).count() == 0):
    #                   gamefolder = str(int(gameid)//100)

                        try:
                            # code to process download here
                            url = "https://www.cross-tables.com/annotated.php?u=" + gameid
                            r = requests.get(url, headers={"User-Agent": "XY"})
                            if (r.status_code==200):
                                self._fgames_collection.insert_one({"game_num": gameid, "p1_name": p1_name, "p1_id": p1_id, "p2_name": p2_name, "p2_id": p2_id, "content": r.text})
                            else:
                                print ("error", i)
                            time.sleep(1)

                        except Exception as e:     # most generic exception you can catch
                            logf.write("Failed to download {0}: {1}\n".format(gameid, page_num))
                            # optional: delete local version of failed download
                    
                

ctd = CrossTablesDownloader()
ctd.download_games()