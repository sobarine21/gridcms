import streamlit as st
import google.generativeai as genai
import requests
import time
import os
import random
import uuid
import json
import pandas as pd  # Added for handling data export
import urllib.parse  # Added for URL encoding in share links

# ---- Helper Functions ----

def get_next_model_and_key():
    """Cycle through available Gemini models and corresponding API keys."""
    models_and_keys = [
        ('gemini-1.5-flash', st.secrets["API_KEY_GEMINI_1_5_FLASH"]),
        ('gemini-2.0-flash', st.secrets["API_KEY_GEMINI_2_0_FLASH"]),
        ('gemini-1.5-flash-8b', st.secrets["API_KEY_GEMINI_1_5_FLASH_8B"]),
        ('gemini-2.0-flash-exp', st.secrets["API_KEY_GEMINI_2_0_FLASH_EXP"]),
    ]
    
    model, api_key = random.choice(models_and_keys)
    return model, api_key

def initialize_session():
    """Initializes session variables securely."""
    if 'session_count' not in st.session_state:
        st.session_state.session_count = 0
    if 'block_time' not in st.session_state:
        st.session_state.block_time = None
    if 'user_hash' not in st.session_state:
        st.session_state.user_hash = str(uuid.uuid4())  # Unique session identifier
    if 'generated_text' not in st.session_state:
        st.session_state.generated_text = ""

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

        if response and response.text:
            return response.text.strip()
        else:
            return "No valid response generated."

    except Exception as e:
        return f"Error generating content: {str(e)}"

def search_web(query):
    """Searches the web using Google Custom Search API and returns results."""
    api_key = st.secrets["GOOGLE_API_KEY"]
    search_engine_id = st.secrets["GOOGLE_SEARCH_ENGINE_ID"]

    if not api_key or not search_engine_id:
        return "Google API Key or Search Engine ID is missing."

    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": search_engine_id, "q": query}

    try:
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            return f"Search API Error: {response.status_code} - {response.text}"

    except requests.exceptions.RequestException as e:
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

        if response and response.text:
            return response.text.strip()
        else:
            return "Regeneration failed."

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
        # Generate content using Generative AI
        generated_text = generate_content(prompt)

        # Increment session count
        st.session_state.session_count += 1
        st.session_state.generated_text = generated_text  # Store for potential regeneration

        # Display the generated content safely
        st.subheader("Generated Content:")
        st.markdown(generated_text)

        # Check for similar content online
        st.subheader("Searching for Similar Content Online:")
        search_results = search_web(generated_text)
        display_search_results(search_results)

        # Export options
        st.subheader("Export Generated Content:")
        export_text_to_file(generated_text, "txt")
        export_text_to_file(generated_text, "csv")
        export_text_to_file(generated_text, "json")

        # Social Media Share Links
        twitter_link = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(generated_text)}"
        facebook_link = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(generated_text)}"
        linkedin_link = f"https://www.linkedin.com/shareArticle?mini=true&url={urllib.parse.quote(generated_text)}"
        reddit_link = f"https://www.reddit.com/submit?url={urllib.parse.quote(generated_text)}"
        email_link = f"mailto:?subject=Check out this generated content&body={urllib.parse.quote(generated_text)}"
        whatsapp_link = f"https://wa.me/?text={urllib.parse.quote(generated_text)}"
        telegram_link = f"https://t.me/share/url?url={urllib.parse.quote(generated_text)}"

        st.subheader("Share your content:")

        # Social Media Share Buttons (HTML anchor)
        st.markdown(f'<a href="{twitter_link}" target="_blank"><button style="background-color: #1DA1F2; color: white; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer;">Share on Twitter</button></a>', unsafe_allow_html=True)
        st.write(" ")
        st.markdown(f'<a href="{facebook_link}" target="_blank"><button style="background-color: #1877F2; color: white; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer;">Share on Facebook</button></a>', unsafe_allow_html=True)
        st.write(" ")
        st.markdown(f'<a href="{linkedin_link}" target="_blank"><button style="background-color: #0077B5; color: white; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer;">Share on LinkedIn</button></a>', unsafe_allow_html=True)
        st.write(" ")
        st.markdown(f'<a href="{reddit_link}" target="_blank"><button style="background-color: #FF4500; color: white; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer;">Share on Reddit</button></a>', unsafe_allow_html=True)
        st.write(" ")
        st.markdown(f'<a href="{email_link}"><button style="background-color: #D44638; color: white; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer;">Share via Email</button></a>', unsafe_allow_html=True)
        st.write(" ")
        st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="background-color: #25D366; color: white; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer;">Share on WhatsApp</button></a>', unsafe_allow_html=True)
        st.write(" ")
        st.markdown(f'<a href="{telegram_link}" target="_blank"><button style="background-color: #0088CC; color: white; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer;">Share on Telegram</button></a>', unsafe_allow_html=True)

# Regenerate Content Button
if st.session_state.get('generated_text'):
    if st.button("Regenerate Content"):
        regenerated_text = regenerate_content(st.session_state.generated_text)
        st.subheader("Regenerated Content:")
        st.markdown(regenerated_text)

        # Export options for regenerated content
        st.subheader("Export Regenerated Content:")
        export_text_to_file(regenerated_text, "txt")
        export_text_to_file(regenerated_text, "csv")
        export_text_to_file(regenerated_text, "json")
