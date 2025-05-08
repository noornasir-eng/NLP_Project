from huggingface_hub import login
import os

# Make Hugging Face login optional - only login if token is provided via environment variable
HF_TOKEN = "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"
if HF_TOKEN:
    login(token=HF_TOKEN, write_permission=False)
    print("Logged in to Hugging Face with provided token")
else:
    print("No Hugging Face token provided, skipping login")

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Force CPU usage in Docker for compatibility
USE_CPU = os.environ.get("FORCE_CPU", "true").lower() == "true"
device = "cpu" if USE_CPU else ("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Model selection - now using a much lighter model for CPU usage
# Options for ultra-lightweight models:
# - "distilgpt2" (82M parameters)
# - "gpt2" (124M parameters)
# - "EleutherAI/pythia-70m" (70M parameters)
# - "facebook/opt-125m" (125M parameters)

model_name = "openai-community/gpt2"  # Very lightweight, only 82M parameters
print(f"Using ultra-lightweight {model_name} model")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
if tokenizer.pad_token is None:
    # DistilGPT2 doesn't have a pad token by default
    tokenizer.pad_token = tokenizer.eos_token

# Load model for CPU - no quantization needed for these small models
model = AutoModelForCausalLM.from_pretrained(model_name)
model = model.to(device)

# Load topics
try:
    df = pd.read_csv("/content/final_TRENDS.csv")
    topics = df["Processed Data"].dropna().unique()
except Exception as e:
    print(f"Error loading topics from CSV: {e}")
    # Fallback topics if the CSV file can't be loaded
    topics = [
        "vaibhav suryavanshi age", "canada elections",
        "indian premier league", "climate change", 
        "tech innovations", "space exploration",
        "artificial intelligence", "cryptocurrency trends",
        "global warming solutions", "new movie releases"
    ]

# Display options
print("📈 Trending Topics:")
for i, topic in enumerate(topics, 1):
    print(f"{i}. {topic}")

# Process input function for gRPC API
def process_input(topic, genre, length, tone, characters):
    """Function to process input and generate story for gRPC API"""
    
    # Convert length to int if it's a string (from gRPC)
    try:
        length_tokens = int(length)
    except ValueError:
        # Default lengths based on descriptive input
        length_map = {"Short": 300, "Medium": 500, "Long": 800}
        length_tokens = length_map.get(length, 500)
    
    # Handle tone
    tone_part = f"The tone of the story should be {tone}. " if tone else ""
    
    # Build prompt based on provided parameters
    if characters:
        prompt = (
            f"Write a [{genre}] story about the trending topic: {topic}. "
            f"{tone_part}"
            f"The story should include the characters: {characters}. "
            f"It should be highly creative, engaging, and complete with a clear beginning, middle, and end. "
            f"For [{genre}], make sure to include elements typical of the genre. "
            f"Make it approximately {length_tokens} words or tokens.\n\n"
            f"Story:"
        )
    else:
        prompt = (
            f"Write a [{genre}] story about the trending topic: {topic}. "
            f"{tone_part} "
            f"The story should be highly creative, engaging, and complete with a clear beginning, middle, and end. "
            f"For [{genre}], make sure to include elements typical of the genre. "
            f"Make it approximately {length_tokens} words or tokens.\n\n"
            f"Story:"
        )
    
    # Generate story - optimized for CPU
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    # Generate shorter responses for faster testing
    max_length = min(length_tokens, 300)  # Limit token length for faster generation
    
    # Store the input length to separate prompt from generated story later
    input_length = inputs.input_ids.size(1)
    
    output = model.generate(
        **inputs,
        max_new_tokens=max_length,
        do_sample=True,
        temperature=0.9,
        top_k=50,
        top_p=0.95,
        pad_token_id=tokenizer.eos_token_id,
        num_return_sequences=1
    )
    
    # Decode and return ONLY the generated story text, without the prompt
    full_text = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # Extract only the generated part by removing the prompt
    # First try to find where the story actually starts with the "Story:" marker
    if "Story:" in full_text:
        story = full_text.split("Story:", 1)[1].strip()
    else:
        # If that fails, use input length to separate
        story_tokens = output[0][input_length:]
        story = tokenizer.decode(story_tokens, skip_special_tokens=True)
    
    print(f"Generated story with {len(story)} characters")
    return story

def translate_story(story, language):
    """Function to translate a story for gRPC API"""
    translator = Translator()
    try:
        # Google Translator uses language codes, so map common names to codes if needed
        language_map = {
            "Spanish": "es",
            "French": "fr", 
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Japanese": "ja",
            "Chinese": "zh-cn",
            "Arabic": "ar",
            "Hindi": "hi",
            "Urdu": "ur"
        }
        
        # Get language code from map or use directly if it's already a code
        lang_code = language_map.get(language, language)
        
        # Translate the story
        translated = translator.translate(story, dest=lang_code)
        return translated.text
    except Exception as e:
        print(f"Translation error: {e}")
        return f"Translation failed: {str(e)}"

def get_trending_topics():
    """Return the list of trending topics for gRPC API"""
    return list(topics)

# Import these at the end to avoid circular imports
from googletrans import Translator, LANGUAGES




