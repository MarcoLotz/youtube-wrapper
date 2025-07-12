#!/usr/bin/env python3
"""
Virtual Environment Manager for YouTube Caption Summarizer
"""

import subprocess
import sys
import os
import platform

def check_venv():
    """Check if virtual environment exists"""
    return os.path.exists('venv')

def create_venv():
    """Create virtual environment"""
    print("🔧 Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("✅ Virtual environment created!")

def install_dependencies():
    """Install dependencies in virtual environment"""
    print("📦 Installing dependencies...")
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
    print("✅ Dependencies installed!")

def run_app():
    """Run the Streamlit application"""
    print("🚀 Starting YouTube Caption Summarizer...")
    print("📱 Open your browser to: http://localhost:8501")
    print("🔐 Login with: Marco / P@oComOvo13")
    print("\n" + "=" * 50)
    
    if platform.system() == "Windows":
        streamlit_cmd = "venv\\Scripts\\streamlit"
    else:
        streamlit_cmd = "venv/bin/streamlit"
    
    try:
        subprocess.run([streamlit_cmd, "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting application: {e}")

def main():
    print("🎬 YouTube Caption Summarizer - Virtual Environment Manager")
    print("=" * 60)
    
    # Check if virtual environment exists
    if not check_venv():
        print("❌ Virtual environment not found.")
        create_venv()
        install_dependencies()
    else:
        print("✅ Virtual environment found!")
    
    # Run the application
    run_app()

if __name__ == "__main__":
    main() 