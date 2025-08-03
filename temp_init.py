#!/usr/bin/env python3
import os
import sys
from app import app, db

try:
    with app.app_context():
        # Create the database tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if database file was created
        if os.path.exists('frecomu.db'):
            print("Database file 'frecomu.db' created successfully!")
        else:
            print("Database file not found in expected location")
            
except Exception as e:
    print(f"Error creating database: {e}")
    sys.exit(1)
