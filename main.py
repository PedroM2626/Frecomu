#!/usr/bin/env python3
"""
Main entry point for Replit deployment.
This file is required by Replit to run the application.
"""

import os
from app import app, socketio, db

def main():
    """Main function to run the Flask-SocketIO application."""
    # Set environment variables for Replit
    os.environ.setdefault('FLASK_ENV', 'production')
    
    # Initialize database if it doesn't exist
    with app.app_context():
        db.create_all()
    
    # Get port from environment (Replit sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Run the application
    socketio.run(
        app,
        debug=False,
        host=host,
        port=port,
        allow_unsafe_werkzeug=True
    )

if __name__ == "__main__":
    main()