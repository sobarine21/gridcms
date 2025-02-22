import streamlit as st
import google.generativeai as genai
import requests
import time
import random
import uuid
import json
import pandas as pd
import os
from gtts import gTTS
from io import BytesIO

# ---- Hide Streamlit Default Menu ----
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---- Helper Functions ----

def get_next_model_and_key():
    """Cycle through available Gemini models and corresponding API keys."""
    models_and_keys = [
        ('gemini-1.5-flash', st.secrets["API_KEY_GEMINI_1_5_FLASH"]),
        ('gemini-2.0-flash', st.secrets["API_KEY_GEMINI_2_0_FLASH"]),
        ('gemini-1.5-flash-8b', st.secrets["API_KEY_GEMINI_1_5_FLASH_8B"]),
        ('gemini-2.0-flash-exp', st.secrets["API_KEY_GEMINI_2_0_FLASH_EXP"]),
    ]
    return random.choice(models_and_keys)

def initialize_session():
    """Initializes session variables securely."""
    session_defaults = {
        "session_count": 0,
        "block_time": None,
        "user_hash": str(uuid.uuid4()),
        "generated_text": "",
        "regenerated_text": "",
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def check_session_limit():
    """Checks if the user has reached the session limit and manages block time."""
    if st.session_state.block_time:
        time_left = st.session_state.block_time - time.time()
        if time_left > 0:
            st.warning(f"Session limit reached. Try again in {int(time_left)} seconds.")
            st.stop()
        else:
            st.session_state.block_time = None
    
    if st.session_state.session_count >= 5:
        st.session_state.block_time = time.time() + 15 * 60  # Block for 15 minutes
        st.warning("Session limit reached. Please wait 15 minutes or upgrade to Pro.")
        st.stop()

def generate_content(prompt):
    """Generates content using Generative AI."""
    try:
        model, api_key = get_next_model_and_key()
        genai.configure(api_key=api_key)
        generative_model = genai.GenerativeModel(model)
        response = generative_model.generate_content(prompt)
        return response.text.strip() if response and response.text else "No valid response generated."
    except Exception as e:
        return f"Error generating content: {str(e)}"

def search_web(query):
    """Searches the web using Google Custom Search API and returns results."""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        search_engine_id = st.secrets["GOOGLE_SEARCH_ENGINE_ID"]
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": api_key, "cx": search_engine_id, "q": query}
        response = requests.get(search_url, params=params)
        return response.json().get("items", []) if response.status_code == 200 else f"Search API Error: {response.status_code}"
    except Exception as e:
        return f"Request failed: {str(e)}"

def display_search_results(search_results):
    """Displays search results in a structured format."""
    if isinstance(search_results, str):
        st.warning(search_results)
        return
    if search_results:
        st.warning("Similar content found on the web:")
        for result in search_results[:5]:  # Show top 5 results
            with st.expander(result.get('title', 'No Title')):
                st.write(f"**Source:** [{result.get('link', 'Unknown')}]({result.get('link', '#')})")
                st.write(f"**Snippet:** {result.get('snippet', 'No snippet available.')}")
                st.write("---")
    else:
        st.success("No similar content found online. Your content seems original!")

def regenerate_content(original_content):
    """Generates rewritten content to ensure originality."""
    try:
        model, api_key = get_next_model_and_key()
        genai.configure(api_key=api_key)
        generative_model = genai.GenerativeModel(model)
        prompt = f"Rewrite the following content to make it original:\n\n{original_content}"
        response = generative_model.generate_content(prompt)
        return response.text.strip() if response and response.text else "Regeneration failed."
    except Exception as e:
        return f"Error regenerating content: {str(e)}"

def export_text_to_file(text, file_format):
    """Exports the generated text to a file."""
    if file_format == "txt":
        st.download_button(label="Download as Text", data=text, file_name="generated_text.txt", mime="text/plain")
    elif file_format == "csv":
        df = pd.DataFrame([{"Generated Text": text}])
        csv = df.to_csv(index=False)
        st.download_button(label="Download as CSV", data=csv, file_name="generated_text.csv", mime="text/csv")
    elif file_format == "json":
        json_data = json.dumps({"Generated Text": text})
        st.download_button(label="Download as JSON", data=json_data, file_name="generated_text.json", mime="application/json")
    elif file_format == "md":
        st.download_button(label="Download as Markdown", data=text, file_name="generated_text.md", mime="text/markdown")

def text_to_speech(text):
    """Converts text to speech using gTTS and returns the audio data."""
    tts = gTTS(text=text, lang='en')
    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

# ---- New Feature Functions ----

def generate_poem(theme):
    prompt = f"Write a poem about {theme}"
    return generate_content(prompt)

def generate_code_snippet(description):
    prompt = f"Generate a code snippet for {description}"
    return generate_content(prompt)

def generate_song_lyrics(theme):
    prompt = f"Write song lyrics about {theme}"
    return generate_content(prompt)

def generate_business_plan(business_idea):
    prompt = f"Create a business plan for the following idea: {business_idea}"
    return generate_content(prompt)

def generate_book_summary(title, author):
    prompt = f"Summarize the book titled '{title}' by {author}"
    return generate_content(prompt)

def generate_marketing_strategy(business_goals):
    prompt = f"Create a marketing strategy to achieve the following business goals: {business_goals}"
    return generate_content(prompt)

def generate_home_decor_ideas(theme):
    prompt = f"Suggest home decor ideas based on the following theme: {theme}"
    return generate_content(prompt)

def generate_event_plan(event_type):
    prompt = f"Create an event plan for the following type of event: {event_type}"
    return generate_content(prompt)

def generate_speech(topic):
    prompt = f"Create a speech on the following topic: {topic}"
    return generate_content(prompt)

def generate_product_description(features):
    prompt = f"Create a product description based on the following features: {features}"
    return generate_content(prompt)

def generate_slogan(brand):
    prompt = f"Create a catchy slogan for the following brand or product: {brand}"
    return generate_content(prompt)

def generate_art_description(art_piece):
    prompt = f"Create a description for the following piece of art: {art_piece}"
    return generate_content(prompt)

def generate_horoscope(zodiac_sign):
    prompt = f"Provide a horoscope for the following zodiac sign: {zodiac_sign}"
    return generate_content(prompt)

def generate_love_letter(feelings):
    prompt = f"Write a love letter based on the following feelings: {feelings}"
    return generate_content(prompt)

def generate_apology_letter(situation):
    prompt = f"Write an apology letter for the following situation: {situation}"
    return generate_content(prompt)

def generate_resume(user_input):
    prompt = f"Create a resume based on the following input: {user_input}"
    return generate_content(prompt)

def generate_cover_letter(job_application):
    prompt = f"Create a cover letter for the following job application: {job_application}"
    return generate_content(prompt)

def generate_bucket_list(preferences):
    prompt = f"Create a bucket list based on the following preferences: {preferences}"
    return generate_content(prompt)

def generate_daily_affirmations(user_input):
    prompt = f"Provide daily affirmations based on the following input: {user_input}"
    return generate_content(prompt)

def generate_fitness_challenge(goals):
    prompt = f"Create a fitness challenge to achieve the following goals: {goals}"
    return generate_content(prompt)

def generate_cleaning_schedule(home):
    prompt = f"Create a cleaning schedule for the following home details: {home}"
    return generate_content(prompt)

def generate_diy_project(materials):
    prompt = f"Suggest DIY projects based on the following materials: {materials}"
    return generate_content(prompt)

def generate_parenting_advice(child_age):
    prompt = f"Provide parenting advice for a child of the following age: {child_age}"
    return generate_content(prompt)

def generate_gardening_tips(plant_type):
    prompt = f"Suggest gardening tips for the following type of plant: {plant_type}"
    return generate_content(prompt)

def generate_pet_care_guide(pet_type):
    prompt = f"Provide a pet care guide for the following type of pet: {pet_type}"
    return generate_content(prompt)

def generate_photography_tips(user_input):
    prompt = f"Suggest photography tips based on the following input: {user_input}"
    return generate_content(prompt)

def generate_language_learning_plan(target_language):
    prompt = f"Create a language learning plan for the following target language: {target_language}"
    return generate_content(prompt)

def generate_stress_management_tips(user_input):
    prompt = f"Suggest stress management tips based on the following input: {user_input}"
    return generate_content(prompt)

def generate_sleep_schedule(user_needs):
    prompt = f"Create a sleep schedule based on the following needs: {user_needs}"
    return generate_content(prompt)

def generate_career_advice(user_goals):
    prompt = f"Provide career advice based on the following goals: {user_goals}"
    return generate_content(prompt)

def generate_social_media_content(platform):
    prompt = f"Suggest social media content ideas based on the following platform: {platform}"
    return generate_content(prompt)

def generate_dating_profile(user_input):
    prompt = f"Create a dating profile based on the following input: {user_input}"
    return generate_content(prompt)

def generate_playlist(mood):
    prompt = f"Provide a music playlist based on the following mood: {mood}"
    return generate_content(prompt)

def generate_movie_recommendations(user_preferences):
    prompt = f"Suggest movies based on the following preferences: {user_preferences}"
    return generate_content(prompt)

def generate_book_recommendations(user_input):
    prompt = f"Provide book recommendations based on the following input: {user_input}"
    return generate_content(prompt)

def generate_game_ideas(user_preferences):
    prompt = f"Suggest game ideas based on the following preferences: {user_preferences}"
    return generate_content(prompt)

def generate_science_experiment(materials):
    prompt = f"Suggest science experiments based on the following materials: {materials}"
    return generate_content(prompt)

def generate_magic_trick(skill_level):
    prompt = f"Suggest magic tricks based on the following skill level: {skill_level}"
    return generate_content(prompt)

def generate_travel_packing_list(destination, duration):
    prompt = f"Provide a packing list for a trip to {destination} for a duration of {duration}"
    return generate_content(prompt)

# ---- Main Streamlit App ----

# Initialize session tracking
initialize_session()

# App Title and Description
st.title("AI-Powered Ghostwriter")
st.write("Generate high-quality content and check for originality using Generative AI and Google Search.")

# Prompt Input Field
prompt = st.text_area("Enter your prompt:", placeholder="Write a blog about AI trends in 2025.")

# Session management to check for block time and session limits
check_session_limit()

# Generate Content Button
if st.button("Generate Response"):
    if not prompt.strip():
        st.warning("Please enter a valid prompt.")
    else:
        generated_text = generate_content(prompt)
        st.session_state.session_count += 1
        st.session_state.generated_text = generated_text  # Store for potential regeneration
        st.subheader("Generated Content:")
        st.markdown(generated_text)
        st.subheader("Searching for Similar Content Online:")
        search_results = search_web(generated_text)
        display_search_results(search_results)
        st.subheader("Export Generated Content:")
        for format in ["txt", "csv", "json", "md"]:
            export_text_to_file(generated_text, format)

# Generate Podcast Button
if st.session_state.get('generated_text'):
    if st.button("Generate Podcast"):
        st.subheader("Download as Podcast:")
        audio_data = text_to_speech(st.session_state.generated_text)
        st.audio(audio_data, format='audio/wav')
        st.download_button(label="Download Podcast", data=audio_data, file_name="generated_content.wav", mime="audio/wav")

# Regenerate Content Button
if st.session_state.get('generated_text'):
    if st.button("Regenerate Content"):
        regenerated_text = regenerate_content(st.session_state.generated_text)
        st.session_state.regenerated_text = regenerated_text  # Store for potential podcast generation
        st.subheader("Regenerated Content:")
        st.markdown(regenerated_text)
        st.subheader("Export Regenerated Content:")
        for format in ["txt", "csv", "json", "md"]:
            export_text_to_file(regenerated_text, format)

# Generate Podcast for Regenerated Content
if st.session_state.get('regenerated_text'):
    if st.button("Generate Podcast for Regenerated Content"):
        st.subheader("Download as Podcast:")
        audio_data = text_to_speech(st.session_state.regenerated_text)
        st.audio(audio_data, format='audio/wav')
        st.download_button(label="Download Podcast", data=audio_data, file_name="regenerated_content.wav", mime="audio/wav")

# ---- New Feature Sections ----

st.subheader("Generate Poem")
poem_theme = st.text_input("Enter a theme for the poem:")
if st.button("Generate Poem"):
    poem = generate_poem(poem_theme)
    st.markdown(poem)
    export_text_to_file(poem, "md")
    if st.button("Generate Podcast for Poem"):
        audio_data = text_to_speech(poem)
        st.audio(audio_data, format='audio/wav')
        st.download_button(label="Download Podcast", data=audio_data, file_name="poem.wav", mime="audio/wav")

st.subheader("Generate Code Snippet")
code_description = st.text_input("Enter a description for the code snippet:")
if st.button("Generate Code Snippet"):
    code_snippet = generate_code_snippet(code_description)
    st.markdown(f"```python\n{code_snippet}\n```")
    export_text_to_file(code_snippet, "md")
    if st.button("Generate Podcast for Code Snippet"):
        audio_data = text_to_speech(code_snippet)
        st.audio(audio_data, format='audio/wav')
        st.download_button(label="Download Podcast", data=audio_data, file_name="code_snippet.wav", mime="audio/wav")

st.subheader("Generate Song Lyrics")
song_theme = st.text_input("Enter a theme for the song lyrics:")
if st.button("Generate Song Lyrics"):
    lyrics = generate_song_lyrics(song_theme)
    st.markdown(lyrics)
    export_text_to_file(lyrics, "md")
    if st.button("Generate Podcast for Song Lyrics"):
        audio_data = text_to_speech(lyrics)
        st.audio(audio_data, format='audio/wav')
        st.download_button(label="Download Podcast", data=audio_data, file_name="song_lyrics.wav", mime="audio/wav")

st.subheader("Generate Business Plan")
business_idea = st.text_input("Enter your business idea:")
if st.button("Generate Business Plan"):
    business_plan = generate_business_plan(business_idea)
    st.markdown(business_plan)
    export_text_to_file(business_plan, "md")
    if st.button("Generate Podcast for Business Plan"):
        audio_data = text_to_speech(business_plan)
        st.audio(audio_data, format='audio/wav')
        st.download_button(label="Download Podcast", data=audio_data, file_name="business_plan.wav", mime="audio/wav")

st.subheader("Generate Book Summary")
book_title = st.text_input("Enter the book title:")
book_author = st.text_input("Enter the book author:")
if st.button("Generate Book Summary"):
    book_summary = generate_book_summary(book_title, book_author)
    st.markdown(book_summary)
    export_text_to_file(book_summary, "md")
    if st.button("Generate Podcast for Book Summary"):
        audio_data = text_to_speech(book_summary)
        st.audio(audio_data, format='audio/wav')
        st.download_button(label="Download Podcast", data=audio_data, file_name="book_summary.wav", mime="audio/wav")

st.subheader("Generate Marketing Strategy")
business_goals = st.text_input("Enter your business goals:")
if st.button("Generate Marketing Strategy"):
    marketing_strategy = generate_marketing_strategy(business_goals)
    st.markdown(marketing_strategy)
    export_text_to_file(marketing_strategy, "md")
    if st.button("Generate Podcast for Marketing Strategy"):
        audio_data = text_to_speech(marketing_strategy)
        st.audio(audio_data, format='audio/wav')
        st.download_button(label="Download Podcast", data=audio_data, file_name="marketing_strategy.wav", mime="audio/wav")
