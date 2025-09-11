from markupsafe import escape

import sqlite3
import urllib.parse
import os

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

    def get_scouting_data(self, where_conditions):
        # Build the WHERE clause
        query = "SELECT * FROM matchData"
        conditions = []

        # Add WHERE conditions if provided
        if where_conditions:
            conditions.append(where_conditions.replace("_", " ").strip())
            query = "SELECT * FROM matchData WHERE " + where_conditions
            
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
            return {"success": False, "message": f"Database error: {str(e)}"}
        except Exception as e:
            self.con.rollback()
            return {"success": False, "message": f"Unexpected error: {str(e)}"}
    
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