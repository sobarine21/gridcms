import streamlit as st
import google.generativeai as genai
import requests
import time
import random
import uuid
import json
import pandas as pd
from meta_threads_sdk import ThreadsAPI  # Meta Threads SDK import

st.markdown("""
    <style>#MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}</style>
""", unsafe_allow_html=True)

# Initialize Meta Threads API SDK
app_id = st.secrets["THREADS_APP_ID"]
app_secret = st.secrets["ACCESS_TOKEN"]
threads_api = ThreadsAPI(app_id, app_secret)

def get_next_model_and_key():
    models_and_keys = [
        ('gemini-1.5-flash', st.secrets["API_KEY_GEMINI_1_5_FLASH"]),
        ('gemini-2.0-flash', st.secrets["API_KEY_GEMINI_2_0_FLASH"]),
        ('gemini-1.5-flash-8b', st.secrets["API_KEY_GEMINI_1_5_FLASH_8B"]),
        ('gemini-2.0-flash-exp', st.secrets["API_KEY_GEMINI_2_0_FLASH_EXP"]),
    ]
    return random.choice(models_and_keys)

def initialize_session():
    defaults = {
        "session_count": 0,
        "block_time": None,
        "user_hash": str(uuid.uuid4()),
        "generated_text": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def check_session_limit():
    if st.session_state.block_time:
        time_left = st.session_state.block_time - time.time()
        if time_left > 0:
            st.warning(f"Session limit reached. Try again in {int(time_left)} seconds.")
            st.stop()
        else:
            st.session_state.block_time = None
    if st.session_state.session_count >= 5:
        st.session_state.block_time = time.time() + 15 * 60
        st.warning("Session limit reached. Please wait 15 minutes or upgrade to Pro.")
        st.stop()

def generate_content(prompt):
    try:
        model, api_key = get_next_model_and_key()
        genai.configure(api_key=api_key)
        generative_model = genai.GenerativeModel(model)
        response = generative_model.generate_content(prompt)
        return response.text.strip() if response and response.text else "No valid response generated."
    except Exception as e:
        return f"Error: {str(e)}"

def search_web(query):
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        search_engine_id = st.secrets["GOOGLE_SEARCH_ENGINE_ID"]
        response = requests.get("https://www.googleapis.com/customsearch/v1", params={"key": api_key, "cx": search_engine_id, "q": query})
        return response.json().get("items", []) if response.status_code == 200 else f"Search API Error: {response.status_code}"
    except Exception as e:
        return f"Request failed: {str(e)}"

def display_search_results(search_results):
    if isinstance(search_results, str):
        st.warning(search_results)
        return
    if search_results:
        st.warning("Similar content found on the web:")
        for result in search_results[:5]:
            with st.expander(result.get('title', 'No Title')):
                st.write(f"**Source:** [{result.get('link', 'Unknown')}]({result.get('link', '#')})")
                st.write(f"**Snippet:** {result.get('snippet', 'No snippet available.')}")
                st.write("---")
    else:
        st.success("No similar content found online.")

def regenerate_content(original_content):
    try:
        model, api_key = get_next_model_and_key()
        genai.configure(api_key=api_key)
        generative_model = genai.GenerativeModel(model)
        response = generative_model.generate_content(f"Rewrite the following content:\n\n{original_content}")
        return response.text.strip() if response and response.text else "Regeneration failed."
    except Exception as e:
        return f"Error: {str(e)}"

def export_text_to_file(text, file_format):
    if file_format == "txt":
        st.download_button("Download as Text", text, "generated_text.txt", "text/plain")
    elif file_format == "csv":
        df = pd.DataFrame([{"Generated Text": text}])
        st.download_button("Download as CSV", df.to_csv(index=False), "generated_text.csv", "text/csv")
    elif file_format == "json":
        st.download_button("Download as JSON", json.dumps({"Generated Text": text}), "generated_text.json", "application/json")

# Function to post content to Meta Threads
def post_to_threads(content):
    try:
        response = threads_api.create_thread(content)
        thread_id = response.json()['id']
        st.success(f'Posted to Threads: {thread_id}')
    except Exception as e:
        st.error(f'Error posting to Threads: {str(e)}')

initialize_session()

st.title("AI-Powered Ghostwriter")
st.write("Generate high-quality content and check for originality using Generative AI and Google Search.")

prompt = st.text_area("Enter your prompt:", placeholder="Write a blog about AI trends in 2025.")

check_session_limit()

if st.button("Generate Response"):
    if not prompt.strip():
        st.warning("Please enter a valid prompt.")
    else:
        generated_text = generate_content(prompt)
        st.session_state.session_count += 1
        st.session_state.generated_text = generated_text
        st.subheader("Generated Content:")
        st.markdown(generated_text)
        st.subheader("Searching for Similar Content Online:")
        search_results = search_web(generated_text)
        display_search_results(search_results)
        st.subheader("Export Generated Content:")
        for format in ["txt", "csv", "json"]:
            export_text_to_file(generated_text, format)

if st.session_state.get('generated_text') and st.button("Regenerate Content"):
    regenerated_text = regenerate_content(st.session_state.generated_text)
    st.subheader("Regenerated Content:")
    st.markdown(regenerated_text)
    st.subheader("Export Regenerated Content:")
    for format in ["txt", "csv", "json"]:
        export_text_to_file(regenerated_text, format)

if st.session_state.get('generated_text') and st.button("Post to Threads"):
    content = st.session_state.generated_text
    post_to_threads(content)
