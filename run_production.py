#!/usr/bin/env python3
"""
Production runner for SIP Simulator
Uses Gunicorn WSGI server for production deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def create_directories():
    """Create necessary directories for production"""
    directories = ['logs', 'data', 'cache']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_environment():
    """Check if environment is properly configured"""
    required_vars = ['FLASK_ENV']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Consider creating a .env file based on env.example")
    
    # Set default production environment
    if not os.getenv('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'production'
        print("✓ Set FLASK_ENV=production")

def install_dependencies():
    """Install production dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def run_gunicorn():
    """Run the application using Gunicorn"""
    print("🚀 Starting SIP Simulator with Gunicorn...")
    
    # Gunicorn command
    cmd = [
        'gunicorn',
        '--config', 'gunicorn.conf.py',
        'backend.app_production:app'
    ]
    
    try:
        # Run Gunicorn
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Gunicorn: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down SIP Simulator...")
        sys.exit(0)

def main():
    """Main function"""
    print("🏭 SIP Simulator - Production Mode")
    print("=" * 40)
    
    # Setup
    create_directories()
    check_environment()
    install_dependencies()
    
    print("\n📊 Configuration:")
    print(f"   Environment: {os.getenv('FLASK_ENV', 'production')}")
    print(f"   Host: {os.getenv('APP_HOST', '0.0.0.0')}")
    print(f"   Port: {os.getenv('APP_PORT', '5000')}")
    print(f"   Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")
    
    print("\n🌐 Access URLs:")
    port = os.getenv('APP_PORT', '5000')
    print(f"   Frontend: http://localhost:{port}")
    print(f"   API: http://localhost:{port}/api/")
    print(f"   Health: http://localhost:{port}/health")
    
    print("\n" + "=" * 40)
    
    # Start server
    run_gunicorn()

if __name__ == '__main__':
    main() 