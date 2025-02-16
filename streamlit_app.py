import streamlit as st
import google.generativeai as genai
import requests
import time
import random
import uuid
import json
import pandas as pd
import urllib.parse
from requests_oauthlib import OAuth2Session

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
        ('gemini-1.5-flash', st.secrets["API_KEYS"]["API_KEY_GEMINI_1_5_FLASH"]),
        ('gemini-2.0-flash', st.secrets["API_KEYS"]["API_KEY_GEMINI_2_0_FLASH"]),
        ('gemini-1.5-flash-8b', st.secrets["API_KEYS"]["API_KEY_GEMINI_1_5_FLASH_8B"]),
        ('gemini-2.0-flash-exp', st.secrets["API_KEYS"]["API_KEY_GEMINI_2_0_FLASH_EXP"]),
    ]
    return random.choice(models_and_keys)

def initialize_session():
    """Initializes session variables securely."""
    session_defaults = {
        "session_count": 0,
        "block_time": None,
        "user_hash": str(uuid.uuid4()),
        "generated_text": "",
        "oauth_token": None,
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
        api_key = st.secrets["GOOGLE"]["GOOGLE_API_KEY"]
        search_engine_id = st.secrets["GOOGLE"]["GOOGLE_SEARCH_ENGINE_ID"]
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

def threads_login():
    """Handles the OAuth2 login process for Threads."""
    client_id = st.secrets["THREADS"]["THREADS_APP_ID"]
    client_secret = st.secrets["THREADS"]["THREADS_APP_SECRET"]
    redirect_uri = "https://gridcms.streamlit.app/"
    authorization_base_url = "https://www.instagram.com/oauth/authorize"
    token_url = "https://graph.instagram.com/oauth/access_token"

    threads = OAuth2Session(client_id, redirect_uri=redirect_uri)
    authorization_url, state = threads.authorization_url(authorization_base_url)
    st.session_state.oauth_state = state

    st.markdown(f"[Click here to log in to Threads]({authorization_url})")

    code = st.text_input("Enter the authorization code after logging in:")
    if st.button("Submit Code"):
        try:
            token = threads.fetch_token(token_url, client_secret=client_secret, code=code)
            st.session_state.oauth_token = token
            st.success("Successfully logged in to Threads.")
        except Exception as e:
            st.error(f"Error logging in: {str(e)}")

def post_to_threads(content):
    """Posts the generated content to Threads."""
    if not st.session_state.oauth_token:
        st.warning("Please log in to Threads first.")
        return

    api_url = "https://graph.instagram.com/v13.0/me/media_publish"
    headers = {"Authorization": f"Bearer {st.session_state.oauth_token['access_token']}"}
    payload = {
        "access_token": st.session_state.oauth_token["access_token"],
        "image_url": "https://example.com/image.jpg",  # Replace with the actual URL of the generated image
        "caption": content
    }

    response = requests.post(api_url, data=payload, headers=headers)
    if response.status_code == 200:
        st.success("Content successfully posted to Threads.")
    else:
        st.error(f"Failed to post content: {response.status_code} - {response.json().get('error_message', 'Unknown error')}")

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

# Threads Login Button
if st.button("Log in to Threads"):
    threads_login()

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
        for format in ["txt", "csv", "json"]:
            export_text_to_file(generated_text, format)

# Regenerate Content Button
if st.session_state.get('generated_text'):
    if st.button("Regenerate Content"):
        regenerated_text = regenerate_content(st.session_state.generated_text)
        st.subheader("Regenerated Content:")
        st.markdown(regenerated_text)
        st.subheader("Export Regenerated Content:")
        for format in ["txt", "csv", "json"]:
            export_text_to_file(regenerated_text, format)

# Post to Threads Button
if st.session_state.get('generated_text'):
    if st.button("Post to Threads"):
        post_to_threads(st.session_state.generated_text)
