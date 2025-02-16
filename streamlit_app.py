import streamlit as st
import streamlit_oauth
import time
import random
import uuid
import json
import pandas as pd
import urllib.parse

# ---- Helper Functions ----

def google_login():
    """Handles user login via Google."""
    oauth = streamlit_oauth.OAuth2(
        client_id=st.secrets["google"]["client_id"],
        client_secret=st.secrets["google"]["client_secret"],
        scopes=["profile"],
    )
    
    # Get user information after OAuth
    user_info = oauth.get_user_info()

    # Check if user is authenticated
    if user_info:
        st.session_state.user_info = user_info
        st.success(f"Logged in as {user_info['name']}")
    else:
        st.warning("Please log in with Google.")

def initialize_session():
    """Initializes session variables securely."""
    if "user_info" not in st.session_state:
        st.session_state["user_info"] = None
    if "session_count" not in st.session_state:
        st.session_state["session_count"] = 0
    if "block_time" not in st.session_state:
        st.session_state["block_time"] = None
    if "generated_text" not in st.session_state:
        st.session_state["generated_text"] = ""

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
    """Generates content using a mock AI model."""
    # Here, we just return a placeholder response.
    return f"This is the content generated for the prompt: {prompt}"

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

def social_share_buttons(content):
    """Generate social media share buttons for Twitter, Facebook, and LinkedIn."""
    twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(content)}"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(content)}"
    linkedin_url = f"https://www.linkedin.com/shareArticle?mini=true&url={urllib.parse.quote(content)}"

    st.markdown(f"""
        <div>
            <a href="{twitter_url}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/60/Twitter_logo_2012.svg" width="40" alt="Share on Twitter" />
            </a>
            <a href="{facebook_url}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" width="40" alt="Share on Facebook" />
            </a>
            <a href="{linkedin_url}" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/7/75/LinkedIn_logo_initials.png" width="40" alt="Share on LinkedIn" />
            </a>
        </div>
    """, unsafe_allow_html=True)

# ---- Main Streamlit App ----

# Initialize session tracking
initialize_session()

# App Title and Description
st.title("AI-Powered Ghostwriter")
st.write("Generate high-quality content and check for originality using Generative AI and Google Search.")

# Google login
if not st.session_state.user_info:
    google_login()
else:
    st.write(f"Welcome, {st.session_state.user_info['name']}!")
    
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

            # Social media share buttons
            social_share_buttons(generated_text)

            # Export generated content
            st.subheader("Export Generated Content:")
            for format in ["txt", "csv", "json"]:
                export_text_to_file(generated_text, format)

    # Regenerate Content Button
    if st.session_state.get('generated_text'):
        if st.button("Regenerate Content"):
            regenerated_text = generate_content(f"Rewrite the following content to make it original:\n\n{st.session_state.generated_text}")
            st.subheader("Regenerated Content:")
            st.markdown(regenerated_text)

            # Export Regenerated Content
            st.subheader("Export Regenerated Content:")
            for format in ["txt", "csv", "json"]:
                export_text_to_file(regenerated_text, format)
