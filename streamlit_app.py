import streamlit as st
import google.generativeai as genai
import requests
import time
import os
import random
import uuid
import json
import asyncio
import aiohttp
from io import StringIO

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

async def generate_content_async(prompt, session):
    """Asynchronously generates content using Generative AI."""
    model, api_key = get_next_model_and_key()
    genai.configure(api_key=api_key)
    generative_model = genai.GenerativeModel(model)

    try:
        response = await asyncio.to_thread(generative_model.generate_content, prompt)
        if response and response.text:
            return response.text.strip()
        else:
            return "No valid response generated."
    except Exception as e:
        return f"Error generating content: {str(e)}"

async def search_web_async(query, session):
    """Asynchronously searches the web using Google Custom Search API."""
    api_key = st.secrets["GOOGLE_API_KEY"]
    search_engine_id = st.secrets["GOOGLE_SEARCH_ENGINE_ID"]

    if not api_key or not search_engine_id:
        return "Google API Key or Search Engine ID is missing."

    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": search_engine_id, "q": query}

    try:
        async with session.get(search_url, params=params) as response:
            if response.status == 200:
                return await response.json()  # Properly get the response JSON
            else:
                return f"Search API Error: {response.status} - {await response.text()}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"

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

    if st.session_state.session_count >= 2:
        st.session_state.block_time = time.time() + 15 * 60  # Block for 15 minutes
        st.warning("Session limit reached. Please wait 15 minutes or upgrade to Pro.")
        st.markdown("You can upgrade to the Pro model by filling out the form [here](https://docs.google.com/forms/d/e/1FAIpQLSeEPL4UOtXbgx1YXLM1I_2u_I7n7hWgPWDn6-Tw9yE3tW7syQ/viewform?embedded=true).", unsafe_allow_html=True)
        st.stop()

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

def download_file(content):
    """Provides the option to download generated content as a text file."""
    buffer = StringIO(content)
    buffer.seek(0)
    st.download_button(
        label="Download as Text File",
        data=buffer,
        file_name="generated_content.txt",
        mime="text/plain"
    )

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

# Asyncio Event Loop for Concurrency
async def main():
    if st.button("Generate Response"):
        if not prompt.strip():
            st.warning("Please enter a valid prompt.")
        else:
            async with aiohttp.ClientSession() as session:
                # Generate content using Generative AI asynchronously
                generated_text = await generate_content_async(prompt, session)

                # Increment session count
                st.session_state.session_count += 1
                st.session_state.generated_text = generated_text  # Store for potential regeneration

                # Display the generated content safely
                st.subheader("Generated Content:")
                st.markdown(generated_text)

                # Check for similar content online asynchronously
                st.subheader("Searching for Similar Content Online:")
                search_results = await search_web_async(generated_text, session)

                # Display search results
                if isinstance(search_results, str):
                    st.warning(search_results)
                elif search_results.get('items'):
                    st.warning("Similar content found on the web:")
                    for result in search_results['items'][:5]:  # Show top 5 results
                        with st.expander(result.get('title', 'No Title')):
                            st.write(f"**Source:** [{result.get('link', 'Unknown')}]({result.get('link', '#')})")
                            st.write(f"**Snippet:** {result.get('snippet', 'No snippet available.')}")
                            st.write("---")
                else:
                    st.success("No similar content found online. Your content seems original!")

                # Allow download of the generated content
                download_file(generated_text)

    if st.session_state.get('generated_text'):
        if st.button("Regenerate Content"):
            regenerated_text = regenerate_content(st.session_state.generated_text)
            st.subheader("Regenerated Content:")
            st.markdown(regenerated_text)
            download_file(regenerated_text)

# Run the async main function
asyncio.run(main())
