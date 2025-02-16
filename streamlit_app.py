import streamlit as st
import requests
import uuid
import json
import time
import random
import urllib.parse

# ---- Hide Streamlit Default Menu ----
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---- Helper Functions ----

# Function to authenticate with Threads API and get an access token
def authenticate_with_threads_api(app_id, app_secret):
    auth_url = "https://graph.instagram.com/access_token"
    auth_data = {
        "client_id": app_id,
        "client_secret": app_secret,
        "grant_type": "client_credentials"
    }
    auth_response = requests.post(auth_url, data=auth_data)

    if auth_response.status_code == 200:
        access_token = auth_response.json()["access_token"]
        return access_token
    else:
        st.error("Authentication failed. Please check your App ID and App Secret.")
        return None

# Function to get user access token after user has authorized the app
def obtain_user_access_token(app_id, app_secret):
    user_token_url = f"https://graph.instagram.com/oauth/authorize?client_id={app_id}&redirect_uri=https://gridcms.streamlit.app/&scope=user_media,pages_show_list,pages_read_engagement,pages_manage_posts,pages_manage_metadata&response_type=code"
    
    st.write("Please click the link to authorize access to your Threads account:")
    st.write(user_token_url)

    # Get authorization code from URL
    code = st.experimental_get_query_params().get("code")
    if code:
        token_url = "https://graph.instagram.com/oauth/access_token"
        token_data = {
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "authorization_code",
            "code": code[0],
            "redirect_uri": "https://gridcms.streamlit.app/"
        }

        token_response = requests.post(token_url, data=token_data)

        if token_response.status_code == 200:
            user_access_token = token_response.json()["access_token"]
            return user_access_token
        else:
            st.error("Failed to obtain user access token.")
            return None
    return None

# Function to post generated content to Threads (text only)
def post_content_to_threads(user_access_token, generated_text):
    threads_url = "https://graph.instagram.com/v13.0/me/media_publish"
    threads_data = {
        "access_token": user_access_token,
        "caption": generated_text  # Use the generated text as the caption
    }

    threads_response = requests.post(threads_url, json=threads_data)

    if threads_response.status_code == 201:
        st.success("Content posted successfully to Threads!")
    else:
        st.error(f"Failed to post content: {threads_response.text}")

# ---- Main Streamlit App ----

# Streamlit Setup and Initialization
st.title("AI-Powered Ghostwriter with Threads Integration")
st.write("Generate content and post it directly to Threads!")

# Authentication Flow
app_id = st.secrets["THREADS_APP_ID"]
app_secret = st.secrets["THREADS_APP_SECRET"]

if "access_token" not in st.session_state:
    if st.button("Login with Threads"):
        # Authenticate with Threads API using app ID and secret
        access_token = authenticate_with_threads_api(app_id, app_secret)
        if access_token:
            st.session_state.access_token = access_token
            st.success("Authentication successful!")
        else:
            st.error("Authentication failed.")

# If authenticated, allow user to post content
if "access_token" in st.session_state:
    st.write("You are authenticated! Now, generate some content.")

    # Generate content from prompt
    prompt = st.text_area("Enter your prompt:", placeholder="Write a blog about AI trends in 2025.")
    
    if st.button("Generate Response"):
        if not prompt.strip():
            st.warning("Please enter a valid prompt.")
        else:
            # Simulate content generation (Replace with your actual content generation logic)
            generated_text = f"Generated content based on the prompt: {prompt}."
            st.session_state.generated_text = generated_text  # Store for potential regeneration
            st.subheader("Generated Content:")
            st.markdown(generated_text)
            
            # Optionally display an image if needed for posting
            st.write("Ready to post the generated text to Threads.")

            if st.button("Post to Threads"):
                user_access_token = st.session_state.access_token
                if user_access_token:
                    post_content_to_threads(user_access_token, generated_text)
                else:
                    st.error("User is not authenticated. Please log in to Threads first.")
