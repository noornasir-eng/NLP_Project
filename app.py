import streamlit as st
import grpc
import agent_pb2
import agent_pb2_grpc
import grpc
import agent_pb2
import agent_pb2_grpc

def send_request(input_text):
    channel = grpc.insecure_channel('localhost:50051')  # gRPC server address
    stub = agent_pb2_grpc.AgentServiceStub(channel)
    
    # Create a request object
    request = agent_pb2.Request(input_text=input_text)
    response = stub.ProcessRequest(request)
    
    return response.output_text

if __name__ == "__main__":
    input_text = "Your input text here"
    result = send_request(input_text)
    print(f"Response from gRPC backend: {result}")

# Create a channel and stub
channel = grpc.insecure_channel('localhost:50051')
stub = agent_pb2_grpc.AgentStub(channel)

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
    </style>
""", unsafe_allow_html=True)

# Page navigation control
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

def go_to(page_name):
    st.session_state.page = page_name

# Welcome Page
if st.session_state.page == 'welcome':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.markdown("""
        <h1>🌟 Welcome to TrendTales!</h1>
        <h2 style="color: #00ffe7;">✨ Ready to Create Magic?</h2>
        <p>Dive into a universe where <strong>your imagination</strong> takes the lead. 🚀</p>
        <p>Pick trending topics, craft characters, and generate magical stories.</p>
    """, unsafe_allow_html=True)
    if st.button("🚀 Start with Trending Topics"):
        go_to('trending')
    st.markdown('</div>', unsafe_allow_html=True)

# Trending Topics Page
elif st.session_state.page == 'trending':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.title("🔥 Trending Topics")
    topics = [
        "Aliens discover TikTok", "Time-traveling cat", "Lost city under the ocean",
        "AI takes over fairy tales", "Ghost in a smart home"
    ]
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
        if st.button("➡️ Proceed to Story Preferences"):
            st.session_state.selected_topic = selected
            go_to('preferences')
    elif user_input:
        st.error("Please enter a valid topic number or name.")
    st.markdown('</div>', unsafe_allow_html=True)

# Preferences Page
elif st.session_state.page == 'preferences':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.title("🎨 Customize Your Story")
    genre = st.selectbox("🎭 Choose a Genre", ["Adventure", "Fantasy", "Sci-Fi", "Horror", "Romance", "Comedy"])
    length = st.selectbox("📏 Story Length", ["Short", "Medium", "Long"])
    tone = st.selectbox("🎼 Tone (Optional)", ["None", "Funny", "Poetic", "Dark", "Inspiring"])
    characters = st.text_input("👤 Main Characters (comma-separated)", placeholder="e.g. Luna, Max, Dr. Quantum")
    
    if st.button("🪄 Generate Story"):
        try:
            response = stub.GenerateStory(agent_pb2.StoryRequest(
                topic=st.session_state.selected_topic,
                genre=genre,
                length=length,
                tone=tone,
                characters=characters
            ))
            st.session_state.generated_story = response.story
            go_to('story_display')
        except grpc.RpcError as e:
            st.error(f"Story generation failed: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# Display Story Page
elif st.session_state.page == 'story_display':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.title("📖 Your Generated Story")
    st.markdown(f'<div class="generated-story">{st.session_state.generated_story}</div>', unsafe_allow_html=True)
    translate = st.radio("Would you like to translate this story?", ("No", "Yes"))
    if translate == "Yes":
        lang = st.selectbox("Choose language for translation:", ["Urdu", "Spanish"])
        if st.button("🌐 Translate Story"):
            try:
                response = stub.TranslateStory(agent_pb2.TranslateRequest(
                    story=st.session_state.generated_story,
                    language=lang
                ))
                st.session_state.translated_story = response.translated_story
                go_to('translation_display')
            except grpc.RpcError as e:
                st.error(f"Translation failed: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# Translated Story Page
elif st.session_state.page == 'translation_display':
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.title("🌐 Translated Story")
    st.markdown(f'<div class="translated-story">{st.session_state.translated_story}</div>', unsafe_allow_html=True)
    if st.button("🔁 Back to Welcome"):
        st.session_state.page = 'welcome'
    st.markdown('</div>', unsafe_allow_html=True)
