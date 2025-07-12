#!/usr/bin/env python3
"""
Quick start script for YouTube Caption Summarizer
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'youtube_transcript_api',
        'openai',
        'streamlit_authenticator',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install dependencies with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠️  No .env file found.")
        print("📝 Create a .env file with your OpenAI API key:")
        print("   OPENAI_API_KEY=your_api_key_here")
        print("   Or enter it manually in the application.")
        return False
    
    print("✅ .env file found!")
    return True

def main():
    print("🎬 YouTube Caption Summarizer")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment file
    check_env_file()
    
    print("\n🚀 Starting the application...")
    print("📱 Open your browser to: http://localhost:8501")
    print("🔐 Login with: Marco / P@oComOvo13")
    print("\n" + "=" * 40)
    
    # Start Streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 