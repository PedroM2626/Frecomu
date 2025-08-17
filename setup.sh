#!/bin/bash
# This script sets up the environment for the application

# Create uploads directory if it doesn't exist
mkdir -p $UPLOAD_FOLDER

# Set proper permissions
chmod -R 755 $UPLOAD_FOLDER

# Install Python dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py

echo "Setup completed successfully"
