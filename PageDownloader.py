from pymongo import MongoClient
import pprint

import pandas as pd

# Requests sends and recieves HTTP requests.
import requests

# Beautiful Soup parses HTML documents in python.
from bs4 import BeautifulSoup
import bs4

import time


c = MongoClient("mongodb://localhost:27017/")

scrabble_db = c[ "scrabble" ]
new_pages_collection = scrabble_db[ "new_pages_collection" ]



for i in range (1, 34000, 100):
    url = "https://www.cross-tables.com/annolistself.php?offset=" + str(i)
    r = requests.get(url, headers={"User-Agent": "XY"})
    print(i, r.status_code)
    time.sleep(1)
    r = requests.get(url, headers={"User-Agent": "XY"})
    if (r.status_code==200):
        new_pages_collection.insert_one({"page_num": i, "content": r.text})
    else:
        print ("error", i)

