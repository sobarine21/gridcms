import streamlit as st
import google.generativeai as genai
import requests

# Configure the API key securely from Streamlit's secrets
# Make sure to add GOOGLE_API_KEY in secrets.toml (for local) or Streamlit Cloud Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Threads API Configuration
threads_app_id = st.secrets["THREADS_APP_ID"]
threads_app_secret = st.secrets["THREADS_APP_SECRET"]
threads_user_token = st.secrets["THREADS_USER_TOKEN"]

# Streamlit App UI
st.title("Ever AI")
st.write("Use Generative AI to get responses based on your prompt.")

# Prompt input field
prompt = st.text_input("Enter your prompt:", "Best alternatives to JavaScript?")

# Button to generate response
if st.button("Generate Response"):
    try:
        # Load and configure the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response from the model
        response = model.generate_content(prompt)
        
        # Display response in Streamlit
        st.write("Response:")
        st.write(response.text)
        
        # Post response to Threads
        if st.button("Post to Threads"):
            # Authenticate with Threads API
            auth_url = "https://graph.instagram.com/access_token"
            auth_data = {
                "client_id": threads_app_id,
                "client_secret": threads_app_secret,
                "grant_type": "client_credentials"
            }
            auth_response = requests.post(auth_url, data=auth_data)
            if auth_response.status_code == 200:
                access_token = auth_response.json()["access_token"]
                
                # Obtain user access token
                token_url = "https://graph.instagram.com/oauth/access_token"
                token_data = {
                    "client_id": threads_app_id,
                    "client_secret": threads_app_secret,
                    "grant_type": "authorization_code",
                    "code": threads_user_token,
                    "redirect_uri": "https://gridcms.streamlit.app/"
                }
                token_response = requests.post(token_url, data=token_data)
                if token_response.status_code == 200:
                    user_access_token = token_response.json()["access_token"]
                    
                    # Post content to Threads
                    threads_url = "https://graph.instagram.com/v13.0/me/media_publish"
                    threads_data = {
                        "access_token": user_access_token,
                        "image_url": "",  # Replace with the generated image URL
                        "caption": response.text
                    }
                    threads_response = requests.post(threads_url, json=threads_data)
                    if threads_response.status_code == 201:
                        st.success("Content posted successfully")
                    else:
                        st.error(f"Failed to post content: {threads_response.status_code}")
                else:
                    st.error(f"Failed to obtain user access token: {token_response.status_code}")
            else:
                st.error(f"Authentication failed: {auth_response.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")
