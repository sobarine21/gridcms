import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import time
import random

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Constants for rate-limiting
MAX_GENERATIONS = 2  # Max number of generations per user
TIME_LIMIT = timedelta(minutes=15)  # Time window of 15 minutes

# Session state to track the user's generation history
if "last_generated" not in st.session_state:
    st.session_state.last_generated = []

# Helper function to track and enforce rate-limiting
def check_rate_limit():
    # Remove any old timestamps that are outside the 15-minute window
    now = datetime.now()
    st.session_state.last_generated = [
        timestamp for timestamp in st.session_state.last_generated if now - timestamp < TIME_LIMIT
    ]
    
    if len(st.session_state.last_generated) >= MAX_GENERATIONS:
        return False
    return True


# Streamlit App UI with enhanced features and animations
st.set_page_config(page_title="Ever AI", page_icon=":robot:", layout="centered")
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #00c6ff, #0072ff);
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #00d1b2;
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00b59d;
    }
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid #00d1b2;
        color: white;
        padding: 10px;
        font-size: 16px;
        border-radius: 8px;
        width: 100%;
        max-width: 800px;
        height: 150px;
        box-sizing: border-box;
    }
    .stTextArea textarea:focus {
        outline: none;
        border-color: #00b59d;
    }
    .stMarkdown h3 {
        text-align: center;
        color: #f0f0f0;
        font-size: 28px;
        font-weight: bold;
    }
    .stMarkdown p {
        color: #f0f0f0;
        font-size: 18px;
        text-align: center;
        padding-bottom: 20px;
    }
    .stSpinner {
        color: #00d1b2;
    }
    .footer {
        text-align: center;
        color: #ffffff;
        padding: 15px;
        font-size: 14px;
    }
    .footer a {
        color: #00d1b2;
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)

# Instructional text with animation
st.markdown("""
    <h3>🚀 Welcome to Ever AI!</h3>
    <p>Generate content with cutting-edge AI based on your prompt. You can generate up to 2 responses every 15 minutes.</p>
""", unsafe_allow_html=True)

# Updated pre-prompt to tell the AI to generate up to 2500 characters
pre_prompt = "Please generate a response based on the following input, but ensure that the response does not exceed 5000 characters."

# Prompt input field where the user can enter their own prompt
user_prompt = st.text_area("Enter your prompt here:", "Best alternatives to javascript?", height=150)

# Combine the pre-prompt with the user input
full_prompt = pre_prompt + "\n" + user_prompt

# Rate limit check
if not check_rate_limit():
    st.error("You have reached the maximum limit of 2 responses in the past 15 minutes. Please try again later.")
else:
    # Button to generate response
    if st.button("Generate Response"):
        # Enforce rate-limiting by storing the current time of the generation
        st.session_state.last_generated.append(datetime.now())

        try:
            # Load and configure the model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate response from the model with the combined prompt
            with st.spinner("💡 Generating your response... This might take a moment!"):
                time.sleep(2)  # Simulating delay for the animation effect
                response = model.generate_content(full_prompt)
                
                # Extract the response text
                response_text = response.text
                
                # Display the response in Streamlit
                st.write("### Response:")
                st.write(response_text)
                
                # Triggering cool animations after the process finishes
                st.balloons()  # Trigger Streamlit balloons after generation

        except Exception as e:
            st.error(f"Error: {e}")

# Footer with links
st.markdown("""
    <div class="footer">
        <p>Powered by Streamlit and Google Generative AI | <a href="https://github.com/yourusername/yourrepo" target="_blank">GitHub</a></p>
    </div>
""", unsafe_allow_html=True)
