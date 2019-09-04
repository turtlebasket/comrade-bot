import sqlite3
connection = sqlite3.connect('storage.db')

c = connection.cursor()

c.execute


"""
import json
import bot

class server_obj:
    ID = 0

    MUTE_VOTE_TIME = 30
    MIN_MUTE_VOTERS = 4 # should be 3
    MUTE_TIME = 600 # 10 mins

    KICK_VOTE_TIME = 300
    MIN_KICK_VOTERS = 6

    BAN_VOTE_TIME = 1200
    MIN_BAN_VOTERS = 8

    def __init__(self, id: int):
        self.ID = id

def new_server_json(id: int):
    json.dump(server_obj(id), "server_data/{}.json".format(str(id)))

def update_attribute(server: int, attrib: str, value):
    try:
        with open('server_data/{}.json'.format(str(server)), 'r+') as target:
            json_file = json.load(target)
        json_file["{}".format(attrib)] = value
        json_file.close()
    except FileNotFoundError:
        new_server_json(id)

def load_attribute():
"""