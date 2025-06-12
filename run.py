#!/usr/bin/env python3
"""
SIP Simulator Backend Server
Run this script to start the Flask API server
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == '__main__':
    from backend.app import app
    print("Starting SIP Simulator Backend...")
    print("API will be available at: http://localhost:5000")
    print("Frontend should be served separately (see README)")
    app.run(debug=True, host='0.0.0.0', port=5000) 