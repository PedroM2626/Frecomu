#!/usr/bin/env python3
"""
Test script for Frecomu Flask application
"""

import requests
import time
import sys

def test_app():
    """Test if the Flask app is running and responding."""
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test if the app is responding
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running and responding!")
            print(f"Status Code: {response.status_code}")
            return True
        else:
            print(f"❌ Flask app responded with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Is it running?")
        print("Make sure to run: python app.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. App might be slow to respond.")
        return False
    except Exception as e:
        print(f"❌ Error testing app: {e}")
        return False

if __name__ == "__main__":
    print("Testing Frecomu Flask Application...")
    print("=" * 40)
    
    success = test_app()
    
    if success:
        print("\n🎉 App is working correctly!")
        print("You can now open your browser and go to: http://127.0.0.1:5000")
    else:
        print("\n💥 App is not working correctly.")
        print("Check the error messages above and fix the issues.")
        sys.exit(1)
