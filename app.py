from flask import Flask, request
from markupsafe import escape

import sqlite3

import os


app = Flask(__name__)

secret_key = "big_skibidi_roaming_kys"

version = 0.1

scoutingData = {
  # General Data
  'eventKey': 'help',
  'robotNum': 0,
  'matchNum': 0,
  'startPosition': '', # char(1) r: right, m: middle, l: left
  'submittedBy': '',

  # Auto
  'aL4Score': 0,
  'aL4Miss':  0, 
  'aL3Score': 0,
  'aL3Miss':  0, 
  'aL2Score': 0,
  'aL2Miss':  0, 
  'aL1Score': 0,
  
  'aBargeScore': 0,
  'aProcScore':  0,
  'aAlgaeMiss':  0,
  
  'aPickupFloor':   0,
  'aPickupStation': 0,
  'aPickupMiss':    0,
  
  # Auto
  'telL4Score': 0,
  'telL4Miss':  0, 
  'telL3Score': 0,
  'telL3Miss':  0, 
  'telL2Score': 0,
  'telL2Miss':  0, 
  'telL1Score': 0,
  
  'telAlgaeScore': 0,
  'telAlgaeMiss':  0,
  
  'telPickupnFloor':   0,
  'telPickupStation': 0,
  'telPickupMiss':    0,

  # Endgame
  'cageParkStatus': '', # char(1) f: failed; p: parked; s: shallow; d: deep

  # Notes
  'disabled': False,
  'playingDefense': False,
  'comments': '' # varchar(250)
}

class database:

    def __init__(self):        
        self.filePath = "scouting.db"
        
        if not os.path.exists(self.filePath):
            self.con = sqlite3.connect('scouting.db')

            self.createCommand = '''
                CREATE TABLE matchData (
                    eventKey          CHAR(8),
                    robotNum          INT,
                    matchNum          INT,
                    startPosition     CHAR(1),
                    submittedBy       VARCHAR(250),
                    aL4Score          INT,
                    aL4Miss           INT,
                    aL3Score          INT,
                    aL3Miss           INT,
                    aL2Score          INT,
                    aL2Miss           INT,
                    aL1Score          INT,
                    aL1Miss           INT,
                    aBargeScore       INT,
                    aProcScore        INT,
                    aAlgaeMiss        INT,
                    aPickupFloor      INT,
                    aPickupStation    INT,
                    aPickupMiss       INT,
                    telL4Score        INT,
                    telL4Miss         INT,
                    telL3Score        INT,
                    telL3Miss         INT,
                    telL2Score        INT,
                    telL2Miss         INT,
                    telL1Score        INT,
                    telAlgaeScore     INT,
                    telAlgaeMiss      INT,
                    telPickupFloor    INT,
                    telPickupStation  INT,
                    telPickupMiss     INT,
                    cageParkStatus    CHAR(1),
                    disabled          TINYINT(1),
                    playingDefense    TINYINT(1),
                    comments          VARCHAR(250)
                );
            '''

            self.cursor = self.con.cursor()
            self.cursor.execute(self.createCommand)

            self.con.commit()
        else:
            self.con = sqlite3.connect(self.filePath)
            self.cursor = self.con.cursor()

    def getScoutingData(whereConditions = "null"):

        # WHERE conditions
        whereConditions = whereConditions.replace("_", " ")
        if whereConditions == "null":
            whereConditions = ""
        else:
            whereConditions = "WHERE " + whereConditions

        if (playingDefense = "null"):
            if (playingDefense != "1" and playingDefense != "0"):
                pass
            else:
                conditions = "WHERE playingDefense = " + playingDefense

        # Getting the data
        self.grabDataCommand = "SELECT * FROM matchData " + whereConditions
        return data = self.cursor.execute(grabDataCommand).fetchall()
            
    def __del__(self):
        self.con.close()

db = database()

db.__del__()

@app.route("/info")
def info():
    if (request.args.get("key") != secret_key):
        return "verification failed!"
    return f"{version}"

@app.route("/getScouting")
def getScouting():
    if (request.args.get("key") != secret_key):
        return "verification failed!"
    else:
        return str(scoutingData)

@app.route("/getPitScouting")
def getPitScouting():
    pass # same as Scouting
