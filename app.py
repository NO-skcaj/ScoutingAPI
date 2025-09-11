#!/usr/bin/env python3
from flask import Flask, request, jsonify
from markupsafe import escape

import sqlite3
import urllib.parse
import os
import threading

from database import *

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

# Thread-local storage for database connections
local_db = threading.local()

def get_db():
    if not hasattr(local_db, 'db'):
        local_db.db = Database()
    return local_db.db

@app.route("/root")
def root():
    if request.args.get("key", "").strip() != secret_key.strip():
        return f"verification failed!", 403
    return jsonify({"version": version})

@app.route("/get_scouting")
def get_scouting():
    if request.args.get("key", "").strip() != secret_key.strip():
        return jsonify({"success": False, "message": "verification failed!"}), 403
    
    try:
        results = get_db().get_scouting_data(request.args.get("where_conditions"))
        # Convert Row objects to dict for JSON serialization
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/add_scouting")
def add_scouting():
    if request.args.get("key", "").strip() != secret_key.strip():
        return f"verification failed!", 403
    
    data = request.args.get("data", "").strip()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
        
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