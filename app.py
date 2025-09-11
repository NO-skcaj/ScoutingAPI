#!/usr/bin/env python3
from flask import Flask, request, jsonify
from markupsafe import escape

import sqlite3
import urllib.parse
import os
import threading

app = Flask(__name__)

secret_key = open('super_duper_secret_password.txt', 'r').read()

version = 0.3

scoutingData = {
  # General Data
  'eventKey': '',
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
  'aL1Miss':  0,
  
  'aBargeScore': 0,
  'aProcScore':  0,
  'aAlgaeMiss':  0,
  
  'aPickupFloor':   0,
  'aPickupStation': 0,
  'aPickupMiss':    0,
  
  # Teleop
  'telL4Score': 0,
  'telL4Miss':  0, 
  'telL3Score': 0,
  'telL3Miss':  0, 
  'telL2Score': 0,
  'telL2Miss':  0, 
  'telL1Score': 0,
  
  'telAlgaeScore': 0,
  'telAlgaeMiss':  0,
  
  'telPickupFloor':   0,
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
        self.con.row_factory = sqlite3.Row
        self.cursor = self.con.cursor()
    
    def _ensure_tables_exist(self):
        # Ensure the required tables exist in the database.
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
            comments          TEXT
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

    def get_scouting_data(self, where_conditions):
        # Build the WHERE clause
        query = "SELECT * FROM matchData"
        conditions = []
        
        # Add WHERE conditions if provided
        if where_conditions:
            conditions.append(where_conditions.replace("_", " ").strip())
        
        # Combine all conditions with AND
        if conditions:
            query += " WHERE " 
            for i in conditions:
                query += " AND ".join(i)
            
        # Execute the query
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_scouting_data(self, data):
        # Fixed SQL command with proper placeholders and commas
        addCommand = '''
            INSERT INTO matchData
            (
                eventKey,
                robotNum,
                matchNum,
                startPosition,
                submittedBy,

                aL4Score,
                aL4Miss,
                aL3Score,
                aL3Miss,
                aL2Score,
                aL2Miss,
                aL1Score,
                aL1Miss,
                aBargeScore,
                aProcScore,
                aAlgaeMiss,
                aPickupFloor,
                aPickupStation,
                aPickupMiss,

                telL4Score,
                telL4Miss,
                telL3Score,
                telL3Miss,
                telL2Score,
                telL2Miss,
                telL1Score,
                telAlgaeScore,
                telAlgaeMiss,
                telPickupFloor,
                telPickupStation,
                telPickupMiss,

                cageParkStatus,

                disabled,
                playingDefense,
                comments
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        try:
            # Parse the data string - URL decode first
            decoded_data = urllib.parse.unquote(data)
            # Split by comma but be careful with quoted strings
            values = self._parse_csv_values(decoded_data)
            
            self.cursor.execute(addCommand, values)
            self.con.commit()  # Fixed: use self.con instead of self.cursor
            return {"success": True, "message": "Data added successfully"}
        except sqlite3.Error as e:
            self.con.rollback()
            return {"success": False, "error": f"Database error: {str(e)}"}
        except Exception as e:
            self.con.rollback()
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    def _parse_csv_values(self, data_string):
        """Parse CSV values, handling quoted strings properly"""
        import csv
        import io
        
        # Use CSV reader to properly parse the comma-separated values
        reader = csv.reader(io.StringIO(data_string))
        values = next(reader)
        
        # Convert values to appropriate types
        processed_values = []
        for i, value in enumerate(values):
            if value.lower() in ('true', 'false'):
                processed_values.append(value.lower() == 'true')
            elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                processed_values.append(int(value))
            else:
                processed_values.append(value)
        
        return processed_values
            
    def __del__(self):
        if hasattr(self, 'con') and self.con is not None:
            self.close()

# Thread-local storage for database connections
local_db = threading.local()

def _get_db():
    if not hasattr(local_db, 'db'):
        local_db.db = Database()
    return local_db.db

@app.route("/root")
def root():
    if request.args.get("key", "").strip() != secret_key.strip():
        return f"verification failed!", 403
    return {"version": version}

@app.route("/get_scouting")
def get_scouting():
    if request.args.get("key", "").strip() != secret_key.strip():
        return f"verification failed!", 403
    
    try:
        results = get_db().get_scouting_data(where_conditions=request.args.get("where_conditions"))
        # Convert Row objects to dict for JSON serialization
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/add_scouting")
def add_scouting():
    if request.args.get("key", "").strip() != secret_key.strip():
        return f"verification failed!", 403
    
    data = request.args.get("data", "").strip()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    result = get_db().add_scouting_data(data)
    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route("/get_pit_scouting")
def get_pit_scouting():
    if request.args.get("key", "").strip() != secret_key.strip():
        return f"verification failed!", 403
    # Similar to get_scouting but for pit scouting data
    return {"message": "Pit scouting endpoint"}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)