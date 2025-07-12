import streamlit as st
import streamlit_authenticator as stauth
from youtube_transcript_api import YouTubeTranscriptApi
import openai
from dotenv import load_dotenv
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="YouTube Caption Summarizer",
    page_icon="📺",
    layout="wide"
)

# Authentication configuration
def setup_authentication():
    """Setup authentication with the specified credentials"""
    config = {
        'credentials': {
            'usernames': {
                'Marco': {
                    'email': 'marco@example.com',
                    'name': 'Marco',
                    'password': stauth.Hasher(['P@oComOvo13']).generate()[0]
                }
            }
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'youtube_summarizer_key',
            'name': 'youtube_summarizer_cookie'
        }
    }
    return config

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_captions(video_id, youtube_api_key=None, preferred_language=None):
    """Download captions for a YouTube video using YouTube Data API v3 or fallback to youtube-transcript-api"""
    
    # If no YouTube API key provided, use fallback method
    if not youtube_api_key:
        st.info("ℹ️ Using fallback method (youtube-transcript-api) - for better results, add YouTube Data API key")
        return get_video_captions_fallback(video_id, preferred_language)
    
    try:
        # Build YouTube API service
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        
        # First, get available caption tracks
        captions_response = youtube.captions().list(
            part='snippet',
            videoId=video_id
        ).execute()
        
        if not captions_response.get('items'):
            st.error("❌ No captions found for this video.")
            return None
        
        # Display available captions
        st.info("ℹ️ Available captions:")
        available_captions = []
        for caption in captions_response['items']:
            lang = caption['snippet']['language']
            is_auto = caption['snippet'].get('trackKind') == 'ASR'
            caption_type = "Auto-generated" if is_auto else "Manual"
            caption_id = caption['id']
            available_captions.append({
                'id': caption_id,
                'language': lang,
                'is_auto': is_auto,
                'type': caption_type
            })
            st.write(f"• {lang} - {caption_type}")
        
        # Find the best caption to use
        caption_to_use = None
        
        # If preferred language is specified, try to find it
        if preferred_language:
            for caption in available_captions:
                if caption['language'] == preferred_language:
                    caption_to_use = caption
                    break
        
        # If no preferred language or not found, try English variants
        if not caption_to_use:
            for lang in ['en', 'en-US', 'en-GB']:
                for caption in available_captions:
                    if caption['language'] == lang:
                        caption_to_use = caption
                        break
                if caption_to_use:
                    break
        
        # If still no caption found, use the first available
        if not caption_to_use and available_captions:
            caption_to_use = available_captions[0]
        
        if not caption_to_use:
            st.error("❌ No suitable captions found.")
            return None
        
        st.success(f"✅ Using captions: {caption_to_use['language']} ({caption_to_use['type']})")
        
        # Download the caption content
        caption_response = youtube.captions().download(
            id=caption_to_use['id'],
            tfmt='srt'  # SubRip format
        ).execute()
        
        # Parse the SRT content
        srt_content = caption_response.decode('utf-8')
        captions = []
        
        # Simple SRT parser
        lines = srt_content.strip().split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.isdigit():  # Subtitle number
                i += 1  # Skip timestamp line
                i += 1  # Move to text
                text_lines = []
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i].strip())
                    i += 1
                if text_lines:
                    captions.append(' '.join(text_lines))
            i += 1
        
        return ' '.join(captions)
        
    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        reason = error_details.get('reason', 'Unknown error')
        
        if reason == 'quotaExceeded':
            st.error("❌ YouTube API quota exceeded. Please try again later or use a different API key.")
        elif reason == 'forbidden':
            st.error("❌ Access denied. The video might be private or restricted.")
        elif reason == 'notFound':
            st.error("❌ Video not found or captions not available.")
        else:
            st.error(f"❌ YouTube API error: {reason}")
        
        return None
        
    except Exception as e:
        st.error(f"❌ Error downloading captions: {str(e)}")
        return None

def generate_summary_with_gpt4(captions, api_key):
    """Generate summary using OpenAI GPT-4"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Split captions if too long (GPT-4 has token limits)
        max_chunk_size = 8000  # Conservative limit
        if len(captions) > max_chunk_size:
            chunks = [captions[i:i+max_chunk_size] for i in range(0, len(captions), max_chunk_size)]
        else:
            chunks = [captions]
        
        summaries = []
        for i, chunk in enumerate(chunks):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates concise, well-structured summaries of YouTube video content based on captions. Focus on the main points, key insights, and important details."
                    },
                    {
                        "role": "user",
                        "content": f"Please create a comprehensive summary of this YouTube video based on its captions. Organize the summary with clear sections and bullet points where appropriate:\n\n{chunk}"
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            summaries.append(response.choices[0].message.content)
        
        return '\n\n'.join(summaries)
    
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def main():
    # Setup authentication
    config = setup_authentication()
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    # Authentication
    name, authentication_status, username = authenticator.login('Login', 'main')
    
    if authentication_status == False:
        st.error('Username/password is incorrect')
        return
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        return
    
    # Main application
    if authentication_status:
        st.title("🎬 YouTube Caption Summarizer")
        st.markdown("Download YouTube video captions and generate AI-powered summaries using GPT-4")
        
        # Sidebar for logout
        with st.sidebar:
            st.write(f"Welcome, {name}!")
            authenticator.logout('Logout', 'sidebar')
            
            st.markdown("---")
            st.markdown("### Instructions")
            st.markdown("""
            1. Paste a YouTube video URL
            2. Enter your OpenAI API key
            3. Click 'Generate Summary'
            4. View the AI-generated summary
            """)
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        # Initialize API keys
        youtube_api_key = ""
        openai_api_key = ""
        
        # Get API keys first (in col2)
        with col2:
            st.subheader("🔑 API Configuration")
            youtube_api_key = st.text_input(
                "YouTube Data API Key",
                type="password",
                help="Enter your YouTube Data API v3 key to access captions"
            )
            
            openai_api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key to use GPT-4"
            )
            
            if not youtube_api_key:
                st.warning("⚠️ Please enter your YouTube Data API key to access captions")
            if not openai_api_key:
                st.warning("⚠️ Please enter your OpenAI API key to generate summaries")
        
        with col1:
            st.subheader("📺 Video Information")
            youtube_url = st.text_input(
                "YouTube Video URL",
                placeholder="https://www.youtube.com/watch?v=...",
                help="Paste the full YouTube video URL here"
            )
            
            if youtube_url:
                video_id = extract_video_id(youtube_url)
                if video_id:
                    st.success(f"✅ Video ID extracted: {video_id}")
                    
                    # Display video embed
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                    st.components.v1.iframe(embed_url, height=315)
                    
                    # Show available captions if YouTube API key is provided
                    if youtube_api_key:
                        try:
                            youtube = build('youtube', 'v3', developerKey=youtube_api_key)
                            captions_response = youtube.captions().list(
                                part='snippet',
                                videoId=video_id
                            ).execute()
                            
                            if captions_response.get('items'):
                                st.info("ℹ️ Available captions for this video:")
                                available_captions = []
                                
                                for caption in captions_response['items']:
                                    lang = caption['snippet']['language']
                                    is_auto = caption['snippet'].get('trackKind') == 'ASR'
                                    caption_type = "Auto-generated" if is_auto else "Manual"
                                    available_captions.append({
                                        'id': caption['id'],
                                        'language': lang,
                                        'is_auto': is_auto,
                                        'type': caption_type
                                    })
                                    st.write(f"• {lang} - {caption_type}")
                                
                                # Language selection dropdown
                                if available_captions:
                                    st.subheader("🌐 Language Selection")
                                    language_options = [f"{caption['language']} ({caption['type']})" for caption in available_captions]
                                    
                                    selected_language = st.selectbox(
                                        "Choose caption language:",
                                        options=language_options,
                                        index=0,
                                        help="Select which language captions to use for the summary"
                                    )
                                    
                                    # Get the language code from selection
                                    selected_index = language_options.index(selected_language)
                                    selected_lang_code = available_captions[selected_index]['language']
                                    st.session_state.selected_lang_code = selected_lang_code
                                else:
                                    st.warning("⚠️ No captions found for this video")
                                    selected_lang_code = None
                                    st.session_state.selected_lang_code = None
                            else:
                                st.warning("⚠️ No captions found for this video")
                                selected_lang_code = None
                                st.session_state.selected_lang_code = None
                        except Exception as e:
                            st.warning("⚠️ Could not check available captions")
                            selected_lang_code = None
                            st.session_state.selected_lang_code = None
                    else:
                        st.info("ℹ️ Enter YouTube API key to see available captions")
                        selected_lang_code = None
                        st.session_state.selected_lang_code = None
                else:
                    st.error("❌ Could not extract video ID from URL. Please check the URL format.")
        
        # Generate summary button
        if st.button("🚀 Generate Summary", type="primary", disabled=not (youtube_url and youtube_api_key and openai_api_key)):
            if youtube_url and youtube_api_key and openai_api_key:
                with st.spinner("Downloading captions..."):
                    video_id = extract_video_id(youtube_url)
                    if video_id:
                        # Get the selected language from the session state or use None
                        selected_lang_code = st.session_state.get('selected_lang_code', None)
                        captions = get_video_captions(video_id, youtube_api_key, selected_lang_code)
                        
                        if captions:
                            st.success("✅ Captions downloaded successfully!")
                            
                            # Display captions
                            with st.expander("📝 View Captions", expanded=False):
                                st.text_area("Full Captions", captions, height=200)
                            
                            # Generate summary
                            with st.spinner("Generating summary with GPT-4..."):
                                summary = generate_summary_with_gpt4(captions, openai_api_key)
                                
                                if summary:
                                    st.success("✅ Summary generated successfully!")
                                    
                                    # Display summary
                                    st.subheader("📋 AI-Generated Summary")
                                    st.markdown(summary)
                                    
                                    # Download option
                                    st.download_button(
                                        label="📥 Download Summary",
                                        data=summary,
                                        file_name=f"youtube_summary_{video_id}.txt",
                                        mime="text/plain"
                                    )
                                else:
                                    st.error("❌ Failed to generate summary. Please check your API key and try again.")
                        else:
                            st.error("❌ Failed to download captions. The video might not have captions available.")
                    else:
                        st.error("❌ Invalid YouTube URL")

if __name__ == "__main__":
    main() 