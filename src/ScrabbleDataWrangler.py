import psycopg2 as pg2
from pymongo import MongoClient
from bs4 import BeautifulSoup
import bs4

class TurnCreator:
    def __init__(self):
  
        c = MongoClient("mongodb://localhost:27017/")

        scrabble_db = c[ "scrabble" ]
        self.fgames_collection = scrabble_db["fgames_collection"]    

    def fill_turn_table(self):
       conn = pg2.connect(user='postgres',  dbname='scrabble', host='localhost', port='5432', password='')
       for g in self.fgames_collection.find():  #{'game_num': {'$lt':'27366'}}):
        #    if (int(g['game_num']) > 15900):
        #        continue
        #    print (g['game_num'])
            soup = BeautifulSoup(g['content'], 'html.parser')
            head = soup.find('head').text
            array_split = head.split('Array')
        #    print ("----------------------------------------------------")
            if int(g['game_num']) % 100 == 0:
                print(g['game_num'])
            for a in array_split[2:-3]:
        #        print(a)
        #        print ('-----------')
                item_split = a.split(',')
                move_num = int(item_split[0][2:])
                move = item_split[1].replace('\x00', '')[2:-1]
                row = int(item_split[2])
                col = int(item_split[3])
                is_vertical = int(item_split[4])
                score = int(item_split[5])
                rack = item_split[6].replace('\x00', '')[2:-1]
                is_player2 = bool(item_split[7].replace('\x00', '').strip())
                p1_score = int(item_split[8])
                p2_score = int(item_split[9])
                comment = ",".join(item_split[10:]).split(']')[0][3:].replace('\x00', '')   #[3:-7]
        #        print(move_num, move, row, col, unknown1, score, rack, unknown2, p1_score, p2_score, comment)
                with conn.cursor() as cursor:
                # Create a new record
                    sql = "INSERT INTO turn2 (gamenum, movenum, move, row, col, is_vertical, score, rack, is_player2, p1_score, p2_score, comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (g['game_num'], move_num, move, row, col, is_vertical, score, rack[:20], is_player2, p1_score, p2_score, comment[:99]))
                
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            conn.commit()
            
 
tc = TurnCreator()
tc.fill_turn_table()