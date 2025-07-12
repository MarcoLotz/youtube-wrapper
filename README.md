# YouTube Caption Summarizer

A Streamlit application that downloads YouTube video captions and generates AI-powered summaries using OpenAI's GPT-4.

## Features

- 🔐 **Secure Authentication**: Login with username "Marco" and password "P@oComOvo13"
- 📺 **YouTube Integration**: Extract captions from any YouTube video with available subtitles
- 🤖 **AI-Powered Summaries**: Generate comprehensive summaries using GPT-4
- 📱 **Modern UI**: Clean, responsive interface with video embedding
- 💾 **Download Support**: Save summaries as text files
- 🔒 **API Key Security**: Secure handling of OpenAI API keys

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd youtube-wrapper
   ```

2. **Set up virtual environment and install dependencies**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```
   
   **Alternative: Use the provided script**
   ```bash
   python run_venv.py
   ```

3. **Set up your API keys**
   - Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Get your YouTube Data API v3 key from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create a `.env` file in the project root:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     YOUTUBE_API_KEY=your_youtube_api_key_here
     ```

## Usage

1. **Run the application**
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate  # On macOS/Linux
   # venv\Scripts\activate   # On Windows
   
   # Run the application
   streamlit run app.py
   ```
   
   **Or use the provided script:**
   ```bash
   python run_venv.py
   ```

2. **Access the application**
   - Open your browser and go to `http://localhost:8501`
   - Login with:
     - Username: `Marco`
     - Password: `P@oComOvo13`

3. **Generate summaries**
   - Paste a YouTube video URL
   - Enter your YouTube Data API key (if not in .env file)
   - Enter your OpenAI API key (if not in .env file)
   - Select your preferred caption language
   - Click "Generate Summary"
   - View and download the AI-generated summary

## Supported YouTube URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## Requirements

- Python 3.7+
- OpenAI API key
- YouTube Data API v3 key
- Internet connection for YouTube and OpenAI API access

## Dependencies

- `streamlit`: Web application framework
- `youtube-transcript-api`: YouTube caption extraction (fallback)
- `google-api-python-client`: YouTube Data API v3 integration
- `openai`: OpenAI API integration
- `streamlit-authenticator`: User authentication
- `python-dotenv`: Environment variable management

## Security Notes

- The application uses secure password hashing
- API keys are handled securely and not stored in plain text
- Session management with cookie-based authentication

## Troubleshooting

- **"No captions available"**: The video must have subtitles/captions enabled
- **API key errors**: Ensure your OpenAI API key is valid and has sufficient credits
- **Authentication issues**: Use the exact credentials provided (Marco/P@oComOvo13)

## License

This project is for educational and personal use.
