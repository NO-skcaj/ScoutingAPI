#!/usr/bin/env python3
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

class Database:
    def __init__(self):
        self.file_path = "scouting.db"
        self.con = None
        self.cursor = None
        self._connect()
        self._ensure_tables_exist()
    
    def _connect(self):
        """Establish a database connection."""
        self.con = sqlite3.connect(self.file_path)
        self.con.row_factory = sqlite3.Row  # Enable column access by name
        self.cursor = self.con.cursor()
    
    def _ensure_tables_exist(self):
        """Ensure the required tables exist in the database."""
        create_command = '''
        CREATE TABLE IF NOT EXISTS matchData (
            eventKey          CHAR(8),
            robotNum          INTEGER,
            matchNum          INTEGER,
            startPosition     CHAR(1),
            submittedBy       TEXT,
            aL4Score          INTEGER,
            aL4Miss           INTEGER,
            aL3Score          INTEGER,
            aL3Miss           INTEGER,
            aL2Score          INTEGER,
            aL2Miss           INTEGER,
            aL1Score          INTEGER,
            aL1Miss           INTEGER,
            aBargeScore       INTEGER,
            aProcScore        INTEGER,
            aAlgaeMiss        INTEGER,
            aPickupFloor      INTEGER,
            aPickupStation    INTEGER,
            aPickupMiss       INTEGER,
            telL4Score        INTEGER,
            telL4Miss         INTEGER,
            telL3Score        INTEGER,
            telL3Miss         INTEGER,
            telL2Score        INTEGER,
            telL2Miss         INTEGER,
            telL1Score        INTEGER,
            telAlgaeScore     INTEGER,
            telAlgaeMiss      INTEGER,
            telPickupFloor    INTEGER,
            telPickupStation  INTEGER,
            telPickupMiss     INTEGER,
            cageParkStatus    CHAR(1),
            disabled          BOOLEAN,
            playingDefense    BOOLEAN,
            comments          TEXT,
            PRIMARY KEY (eventKey, robotNum, matchNum)
        )
        '''
        self.cursor.execute(create_command)
        self.con.commit()
        
    def __enter__(self):
        return self
        
    def close(self):
        """Close the database connection."""
        if self.con:
            self.con.close()
            self.con = None
            self.cursor = None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def getScoutingData(self, where_conditions="null", playing_defense=None):
        # Build the WHERE clause
        query = "SELECT * FROM matchData"
        conditions = []
        
        # Add WHERE conditions if provided
        if where_conditions != "null":
            conditions.append(where_conditions.replace("_", " ").strip())
            
        # Add playingDefense condition if specified
        if playing_defense is not None:
            if playing_defense in (0, 1, "0", "1"):
                conditions.append(f"playingDefense = {int(playing_defense)}")
                
        # Combine all conditions with AND
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        # Execute the query
        self.cursor.execute(query)
        return self.cursor.fetchall()
            
    def __del__(self):
        if hasattr(self, 'con') and self.con is not None:
            self.close()

# Initialize database
with Database() as db:
    pass  # Database will be properly closed when the context exits

@app.route("/info")
def info():
    if request.args.get("key") != secret_key:
        return "verification failed!", 403
    return {"version": version}

@app.route("/getScouting")
def get_scouting():
    if request.args.get("key") != secret_key:
        return "verification failed!", 403
    
    try:
        where_conditions = request.args.get("where", "null")
        playing_defense = request.args.get("playing_defense")
        
        with Database() as db:
            results = db.getScoutingData(
                where_conditions=where_conditions,
                playing_defense=playing_defense
            )
            
        # Convert Row objects to dict for JSON serialization
        return [dict(row) for row in results]
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/getPitScouting")
def get_pit_scouting():
    if request.args.get("key") != secret_key:
        return "verification failed!", 403
    # Similar to get_scouting but for pit scouting data
    return {"message": "Pit scouting endpoint"}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
