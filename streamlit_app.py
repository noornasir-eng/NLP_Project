import streamlit as st
import grpc
import agent_pb2
import agent_pb2_grpc
import time
import os
from googletrans import LANGUAGES
import base64
from gtts import gTTS
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config and custom styles
st.set_page_config(page_title="TrendTales", layout="centered", page_icon="📚")
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Outfit', sans-serif; }
        header[data-testid="stHeader"], #MainMenu, footer { display: none; }
        .stApp {
            background: radial-gradient(circle at 20% 30%, #1b2735 0%, #090a0f 100%);
            color: #f2f2f2;
        }
        .main-box {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(12px);
            border-radius: 20px;
            padding: 2rem;
            max-width: 850px;
            margin: 2rem auto;
        }
        h1, h2, h3 {
            color: #00ffe7;
            text-align: center;
        }
        .stButton > button {
            background: linear-gradient(135deg, #00c6ff, #0072ff);
            color: white; border-radius: 12px;
            font-weight: bold; padding: 0.7rem 1.7rem;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #0072ff, #00c6ff);
            transform: scale(1.05);
        }
        .generated-story, .translated-story {
            font-size: 19px; line-height: 1.7;
            color: #e6e6e6; background: rgba(255,255,255,0.06);
            border-radius: 10px; padding: 1rem;
            margin-top: 1rem;
        }
        .topic-list {
            max-height: 300px;
            overflow-y: auto;
            background: rgba(255,255,255,0.04);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            line-height: 1.8;
        }
        .loader {
            display: flex;
            justify-content: center;
            margin-top: 2rem;
        }
        .audio-player {
            margin-top: 20px;
            padding: 15px;
            background: rgba(0,198,255,0.1);
            border-radius: 10px;
            border: 1px solid rgba(0,198,255,0.3);
        }
    </style>
""", unsafe_allow_html=True)

# Function to generate audio from text
def generate_audio(text, lang='en'):
    """Generate audio from text using gTTS"""
    try:
        tts = gTTS(text=text, lang=lang)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        audio_base64 = base64.b64encode(audio_bytes.read()).decode()
        return audio_base64
    except Exception as e:
        st.error(f"Audio generation failed: {e}")
        return None

# Create a gRPC connection to the backend service
@st.cache_resource
def get_grpc_client():
    try:
        # Determine the backend address based on environment
        # In Docker, use the service name; in local dev, use localhost
        if os.environ.get("DOCKER_CONTAINER", "") == "true":
            backend_address = 'backend:50051'
        else:
            backend_address = 'localhost:50051'
            
        logger.info(f"Connecting to backend at: {backend_address}")
        st.info(f"Connecting to backend at: {backend_address}")
        channel = grpc.insecure_channel(backend_address)
        return agent_pb2_grpc.AgentStub(channel)
    except Exception as e:
        logger.error(f"Failed to connect to gRPC server: {str(e)}")
        st.error(f"Failed to connect to gRPC server: {e}")
        return None

# Initialize session states
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False
if 'story_generated' not in st.session_state:
    st.session_state.story_generated = False

def go_to(page_name):
    st.session_state.page = page_name

def generate_story_async(topic, genre, length, tone, characters):
    """Helper function to generate story and update session state"""
    try:
        st.session_state.is_generating = True
        
        stub = get_grpc_client()
        if not stub:
            st.error("Failed to connect to the backend service. Please try again.")
            st.session_state.is_generating = False
            return
        
        # Log request details for debugging
        logger.info(f"Sending story request: topic={topic}, genre={genre}, length={length}, tone={tone}, characters={characters}")
        
        # Create the gRPC request
        request = agent_pb2.StoryRequest(
            topic=topic,
            genre=genre,
            length=length,
            tone=tone if tone != "None" else "",
            characters=characters
        )
        
        # Make the gRPC call with timeout
        response = stub.GenerateStory(request, timeout=120.0)
        
        # Log success and response
        logger.info(f"Received story response of length: {len(response.story)}")
        if len(response.story) > 0:
            logger.info(f"Story preview: {response.story[:100]}...")
        else:
            logger.warning("Received empty story from backend")
        
        # Store story in session state
        st.session_state.generated_story = response.story
        st.session_state.story_generated = True
        st.session_state.is_generating = False
        
        # Navigate to the story display page
        go_to('story_display')
        
    except grpc.RpcError as rpc_error:
        error_code = rpc_error.code()
        error_details = rpc_error.details()
        logger.error(f"gRPC error: {error_code} - {error_details}")
        st.error(f"Story generation failed: {error_code} - {error_details}")
        st.session_state.is_generating = False
        
    except Exception as e:
        logger.error(f"Story generation error: {str(e)}")
        st.error(f"Story generation failed: {e}")
        st.session_state.is_generating = False

# Welcome Page
if st.session_state.page == 'welcome':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.markdown("""
        <h1>🌟 Welcome to TrendTales!</h1>
        <h2 style="color: #00ffe7;">✨ Turn Trending Topics into Creative Stories</h2>
        <p>Dive into a universe where <strong>trending topics transform</strong> into captivating stories. 🚀</p>
        <p>Pick a trending topic, select your genre, add characters, and let AI create magical tales for you.</p>
    """, unsafe_allow_html=True)
    if st.button("🚀 Explore Trending Topics"):
        go_to('trending')
    st.markdown('</div>', unsafe_allow_html=True)

# Trending Topics Page
elif st.session_state.page == 'trending':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.title("🔥 Trending Topics")
    
    # Get trending topics from backend
    stub = get_grpc_client()
    topics = []
    
    try:
        with st.spinner("Fetching trending topics..."):
            response = stub.GetTrendingTopics(agent_pb2.EmptyRequest())
            topics = list(response.topics)
    except Exception as e:
        st.error(f"Failed to fetch topics: {e}")
        # Fallback topics if backend is not available
        topics = [
            "vaibhav suryavanshi age", "canada elections",
            "indian premier league", "climate change", 
            "tech innovations", "space exploration"
        ]
    
    st.markdown("<p>Select a trending topic to create your story:</p>", unsafe_allow_html=True)
    st.markdown('<div class="topic-list">' + "<br>".join(f"{i+1}. {t}" for i, t in enumerate(topics)) + "</div>", unsafe_allow_html=True)
    
    user_input = st.text_input("Enter the number or name of the topic you want a story on:")
    selected = None
    
    if user_input:
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(topics):
                selected = topics[idx]
        else:
            user_input = user_input.strip().lower()
            for topic in topics:
                if user_input in topic.lower():
                    selected = topic
                    break
                    
    if selected:
        st.success(f"You selected: {selected}")
        if st.button("➡️ Customize Your Story"):
            st.session_state.selected_topic = selected
            go_to('preferences')
    elif user_input:
        st.error("Please enter a valid topic number or name.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Preferences Page
elif st.session_state.page == 'preferences':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.title("🎨 Customize Your Story")
    
    st.write(f"Selected Topic: **{st.session_state.selected_topic}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        genre = st.selectbox("🎭 Choose a Genre", ["Comedy", "Fantasy", "Sci-Fi", "Horror", "Romance", "Adventure"])
        tone = st.selectbox("🎼 Tone (Optional)", ["None", "Funny", "Poetic", "Dark", "Inspiring", "Mysterious"])
    
    with col2:
        length = st.selectbox("📏 Story Length", ["Short", "Medium", "Long"])
        characters = st.text_input("👤 Main Characters (comma-separated)", placeholder="e.g. Luna, Max, Dr. Quantum")
    
    # Generate story button
    if st.button("🪄 Generate Story") or st.session_state.is_generating:
        if st.session_state.is_generating:
            # Show spinner while generating
            with st.spinner("Crafting your story... This may take a few moments ✨"):
                # Artificial delay to ensure UI updates
                time.sleep(0.5) 
                
                # If story is now generated, display it
                if st.session_state.story_generated:
                    st.success("Story generated successfully!")
                    st.session_state.is_generating = False
                    go_to('story_display')
                    st.rerun()
        else:
            # Start the generation process
            st.session_state.is_generating = True
            st.session_state.story_generated = False
            
            with st.spinner("Crafting your story... This may take a few moments ✨"):
                # Generate story and handle state changes
                generate_story_async(
                    st.session_state.selected_topic,
                    genre,
                    length,
                    tone if tone != "None" else "",
                    characters
                )
            
            # If story was generated successfully, navigate to display
            if st.session_state.story_generated:
                st.success("Story generated successfully!")
                st.rerun()
                
    if st.button("⬅️ Back to Topic Selection"):
        go_to('trending')
        
    st.markdown('</div>', unsafe_allow_html=True)

# Display Story Page
elif st.session_state.page == 'story_display':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.title("📖 Your Generated Story")
    
    # Reset the generation flags when displaying story
    st.session_state.is_generating = False
    
    # Check if we have a story to display
    if 'generated_story' not in st.session_state or not st.session_state.generated_story:
        st.error("No story found. There might have been an issue with story generation.")
        if st.button("Try Again"):
            go_to('preferences')
        st.stop()
    
    # Display story with some basic formatting and line breaks for readability
    story_text = st.session_state.generated_story.replace("\n", "<br>")
    st.markdown(f'<div class="generated-story">{story_text}</div>', unsafe_allow_html=True)
    
    # Add audio playback option
    audio_col, translate_col = st.columns(2)
    
    with audio_col:
        if st.button("🔊 Listen to Story"):
            with st.spinner("Generating audio..."):
                # Generate audio for the original story
                audio_data = generate_audio(st.session_state.generated_story)
                if audio_data:
                    st.markdown(f"""
                        <div class="audio-player">
                            <p>📢 Story Audio:</p>
                            <audio controls autoplay>
                                <source src="data:audio/mp3;base64,{audio_data}" type="audio/mp3">
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                    """, unsafe_allow_html=True)
    
    with translate_col:
        translate = st.radio("Would you like to translate this story?", ("No", "Yes"))
    
    if translate == "Yes":
        # Create a clean list of language options
        languages = ["Spanish", "French", "German", "Italian", "Russian", "Japanese", "Chinese", "Arabic", "Hindi", "Urdu"]
        lang = st.selectbox("Choose language for translation:", languages)
        
        if st.button("🌐 Translate Story"):
            with st.spinner("Translating your story..."):
                try:
                    stub = get_grpc_client()
                    response = stub.TranslateStory(agent_pb2.TranslateRequest(
                        story=st.session_state.generated_story,
                        language=lang
                    ))
                    st.session_state.translated_story = response.translated_story
                    st.session_state.translation_language = lang
                    go_to('translation_display')
                except Exception as e:
                    st.error(f"Translation failed: {e}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Generate Another Story"):
            go_to('preferences')
    with col2:
        if st.button("🏠 Back to Home"):
            go_to('welcome')
            
    st.markdown('</div>', unsafe_allow_html=True)

# Translated Story Page
elif st.session_state.page == 'translation_display':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.title("🌐 Translated Story")
    
    st.markdown(f'<div class="translated-story">{st.session_state.translated_story}</div>', unsafe_allow_html=True)
    
    # Language code mapping for audio generation
    language_code_map = {
        "Spanish": "es", "French": "fr", "German": "de", 
        "Italian": "it", "Russian": "ru", "Japanese": "ja", 
        "Chinese": "zh-cn", "Arabic": "ar", "Hindi": "hi", "Urdu": "ur"
    }
    
    # Add audio playback for translated text
    if st.button("🔊 Listen to Translated Story"):
        with st.spinner("Generating audio..."):
            # Get the appropriate language code for audio
            lang_code = language_code_map.get(st.session_state.translation_language, "en")
            
            # Generate audio for the translated story
            audio_data = generate_audio(st.session_state.translated_story, lang=lang_code)
            if audio_data:
                st.markdown(f"""
                    <div class="audio-player">
                        <p>📢 Translated Audio:</p>
                        <audio controls autoplay>
                            <source src="data:audio/mp3;base64,{audio_data}" type="audio/mp3">
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Original Story"):
            go_to('story_display')
    with col2:
        if st.button("🏠 Back to Home"):
            go_to('welcome')
            
    st.markdown('</div>', unsafe_allow_html=True)