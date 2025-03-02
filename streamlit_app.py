import streamlit as st
import google.generativeai as genai
import time
import random
import uuid
import asyncio
import aiohttp

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
        return None  # Return None if API keys are missing

    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": search_engine_id, "q": query}

    try:
        async with session.get(search_url, params=params) as response:
            if response.status == 200:
                return await response.json()  # Properly get the response JSON
            else:
                return None  # Return None on error
    except requests.exceptions.RequestException as e:
        return None  # Return None on exception

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
            st.warning(f"Session limit reached. Try again in {int(time_left)} seconds or upgrade to pro, https://evertechcms.in/gridai")
            st.stop()
        else:
            st.session_state.block_time = None

    if st.session_state.session_count >= 5:
        st.session_state.block_time = time.time() + 15 * 60  # Block for 15 minutes
        st.warning("Session limit reached. Please wait 15 minutes or upgrade to Pro.")
        st.markdown("You can upgrade to the Pro model & Get lifetime access at just Rs 999 [here](https://forms.gle/TJWH9HJ4kqUTN7Hp9).", unsafe_allow_html=True)
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
    # Convert content to bytes
    content_bytes = content.encode('utf-8')
    
    # Use st.download_button to provide the file download
    st.download_button(
        label="Download as Text File",
        data=content_bytes,
        file_name="generated_content.txt",
        mime="text/plain"
    )

# ---- Main Streamlit App ----

# Initialize session tracking
initialize_session()

# App Title and Description
st.title("AI-Powered Ghostwriter")
st.write("Generate high-quality content and check for originality using Generative AI and Google Search. You can get lifetime access to Grid Pro at Rs 999, visit https://evertechcms.in/gridai")

# Add custom CSS to apply eye-catching animations and a tech-inspired UI theme
hide_streamlit_style = """
    <style>
        /* Global Styling */
        body {
            background: linear-gradient(135deg, #1e1e1e, #2a2a2a);
            color: #e4e4e4;
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
        }

        /* Button Styling */
        .stButton button {
            background-color: #5f6368;
            color: white;
            border-radius: 10px;
            padding: 14px 28px;
            font-size: 16px;
            font-weight: 600;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
        }

        .stButton button:hover {
            background-color: #3a3a3a;
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }

        /* Text Area Styling */
        .stTextArea textarea {
            background-color: #333;
            color: #e4e4e4;
            border-radius: 10px;
            padding: 12px;
            font-size: 16px;
            border: 1px solid #444;
            width: 100%;
            transition: all 0.3s ease;
        }

        .stTextArea textarea:focus {
            border-color: #5f6368;
            outline: none;
            box-shadow: 0 0 5px #5f6368;
        }

        /* Custom Text Styling */
        .stMarkdown {
            color: #e4e4e4;
            font-size: 18px;
            line-height: 1.8;
        }

        /* Success and Warning Styles */
        .stSuccess {
            background-color: #4caf50;
            color: #ffffff;
            padding: 12px;
            border-radius: 6px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
        }

        .stWarning {
            background-color: #ff5722;
            color: #ffffff;
            padding: 12px;
            border-radius: 6px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
        }

        /* Expanders Styling */
        .stExpander {
            background-color: #444;
            color: #e4e4e4;
            border-radius: 10px;
            padding: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Hover Effect for Download Button */
        .stDownloadButton {
            background-color: #008CBA;
            color: white;
            padding: 12px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 6px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        .stDownloadButton:hover {
            background-color: #005f73;
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }

        /* Subtle animations for content */
        .stExpander, .stButton button, .stTextArea textarea {
            animation: fadeIn 0.5s ease-in-out;
        }

        @keyframes fadeIn {
            0% {
                opacity: 0;
            }
            100% {
                opacity: 1;
            }
        }

        /* Hide Streamlit's default UI elements */
        .css-1r6p8d1 {display: none;} /* Hides the Streamlit logo in the top left */
        .css-1v3t3fg {display: none;} /* Hides the star button */
        header {visibility: hidden;} /* Hides the header */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Prompt Input Field
prompt = st.text_area("Enter your prompt:", placeholder="Write a blog about AI trends in 2025.", height=150)

# Session management to check for block time and session limits
check_session_limit()

# Asyncio Event Loop for Concurrency
async def main():
    if st.button("Generate Response"):
        if not prompt.strip():
            st.warning("Please enter a valid prompt.")
        else:
            # Show spinner and countdown before AI request
            with st.spinner("Please wait, generating response..."):
                countdown_time = 5
                countdown_text = st.empty()  # Create an empty container to update the text
                
                # Countdown loop with dynamic updates
                for i in range(countdown_time, 0, -1):
                    countdown_text.markdown(f"Generating response in **{i} seconds...**")
                    time.sleep(1)  # Simulate countdown delay

                # After countdown, make the AI request
                async with aiohttp.ClientSession() as session:
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

                    # Validate search results before accessing
                    if search_results is None:
                        st.warning("Error or no results from the web search.")
                    elif isinstance(search_results, dict) and 'items' in search_results and search_results['items']:
                        st.warning("Similar content found on the web:")
                        for result in search_results['items'][:10]:  # Show top 5 results
                            with st.expander(result.get('title', 'No Title')):
                                st.write(f"**Source:** [{result.get('link', 'Unknown')}]({result.get('link', '#')})")
                                st.write(f"**Snippet:** {result.get('snippet', 'No snippet available.')}")
                                st.write("---")
                    else:
                        st.success("No similar content found online. Your content seems original!")

                    # Trigger Streamlit balloons after generation
                    st.balloons()

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
