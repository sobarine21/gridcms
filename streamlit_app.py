import streamlit as st
import google.generativeai as genai
import requests

# Configure the API key securely from Streamlit's secrets
# Make sure to add GOOGLE_API_KEY in secrets.toml (for local) or Streamlit Cloud Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Threads API Configuration
threads_app_id = st.secrets["THREADS_APP_ID"]
threads_app_secret = st.secrets["THREADS_APP_SECRET"]
redirect_uri = "https://gridcms.streamlit.app/"

# Streamlit App UI
st.title("Ever AI")
st.write("Use Generative AI to get responses based on your prompt.")

# Login to Threads
if st.button("Login to Threads"):
    auth_url = f"https://graph.instagram.com/oauth/authorize?client_id={threads_app_id}&redirect_uri={redirect_uri}&scope=user_media,pages_show_list,pages_read_engagement,pages_manage_posts,pages_manage_metadata&response_type=code"
    st.write("Please click the link to authorize access:")
    st.write(auth_url)

# Get authorization code from URL
code = st.query_params.get("code")

if code:
    # Exchange authorization code for access token
    token_url = "https://graph.instagram.com/oauth/access_token"
    token_data = {
        "client_id": threads_app_id,
        "client_secret": threads_app_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }
    token_response = requests.post(token_url, data=token_data)
    if token_response.status_code == 200:
        access_token = token_response.json()["access_token"]
        st.success("Logged in to Threads successfully")

        # Generate content and post to Threads
        prompt = st.text_input("Enter your prompt:", "Best alternatives to JavaScript?")
        if st.button("Generate and Post"):
            try:
                # Load and configure the model
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Generate response from the model
                response = model.generate_content(prompt)
                
                # Display response in Streamlit
                st.write("Response:")
                st.write(response.text)
                
                # Post response to Threads
                threads_url = "https://graph.instagram.com/v13.0/me/media_publish"
                threads_data = {
                    "access_token": access_token,
                    "image_url": "",  # Replace with the generated image URL
                    "caption": response.text
                }
                threads_response = requests.post(threads_url, json=threads_data)
                if threads_response.status_code == 201:
                    st.success("Content posted successfully")
                else:
                    st.error(f"Failed to post content: {threads_response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.error(f"Failed to obtain access token: {token_response.status_code}")
