import streamlit as st
import google.generativeai as genai
import requests

# Configure the API key securely from Streamlit's secrets
# Make sure to add GOOGLE_API_KEY in secrets.toml (for local) or Streamlit Cloud Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Threads API Configuration
threads_app_id = st.secrets["THREADS_APP_ID"]
threads_app_secret = st.secrets["THREADS_APP_SECRET"]
user_token = st.secrets["USER_TOKEN"]
app_token = st.secrets["APP_TOKEN"]

# Streamlit App UI
st.title("Ever AI")
st.write("Use Generative AI to get responses based on your prompt.")

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
        threads_url = f"https://graph.instagram.com/v13.0/me/media_publish?access_token={user_token}"
        threads_data = {
            "caption": response.text
        }
        threads_headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        threads_response = requests.post(threads_url, json=threads_data, headers=threads_headers)
        if threads_response.status_code == 201:
            st.success("Content posted successfully")
        else:
            st.error(f"Failed to post content: {threads_response.status_code}")
            st.write("Error Response:")
            st.write(threads_response.text)
    except Exception as e:
        st.error(f"Error: {e}")
