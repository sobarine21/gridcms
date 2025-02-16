import streamlit as st
import google.generativeai as genai
import requests
import time
import random
import uuid
import json
import pandas as pd
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

def get_next_model_and_key():
    """Cycle through available Gemini models and corresponding API keys."""
    models_and_keys = [
        ('gemini-1.5-flash', st.secrets["API_KEY_GEMINI_1_5_FLASH"]),
        ('gemini-2.0-flash', st.secrets["API_KEY_GEMINI_2_0_FLASH"]),
        ('gemini-1.5-flash-8b', st.secrets["API_KEY_GEMINI_1_5_FLASH_8B"]),
        ('gemini-2.0-flash-exp', st.secrets["API_KEY_GEMINI_2_0_FLASH_EXP"]),
    ]
    return random.choice(models_and_keys)

def initialize_session():
    """Initializes session variables securely."""
    session_defaults = {
        "session_count": 0,
        "block_time": None,
        "user_hash": str(uuid.uuid4()),
        "generated_text": "",
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

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
        return response.text.strip() if response and response.text else "No valid response generated."
    except Exception as e:
        return f"Error generating content: {str(e)}"

def search_web(query):
    """Searches the web using Google Custom Search API and returns results."""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        search_engine_id = st.secrets["GOOGLE_SEARCH_ENGINE_ID"]
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": api_key, "cx": search_engine_id, "q": query}
        response = requests.get(search_url, params=params)
        return response.json().get("items", []) if response.status_code == 200 else f"Search API Error: {response.status_code}"
    except Exception as e:
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
        return response.text.strip() if response and response.text else "Regeneration failed."
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
    elif file_format == "md":
        st.download_button(label="Download as Markdown", data=text, file_name="generated_text.md", mime="text/markdown")

# ---- New Feature Functions ----

def generate_poem(theme):
    prompt = f"Write a poem about {theme}"
    poem = generate_content(prompt)
    st.markdown(poem)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(poem)
    display_search_results(search_results)
    export_text_to_file(poem, "md")

def generate_code_snippet(description):
    prompt = f"Generate a code snippet for {description}"
    code_snippet = generate_content(prompt)
    st.markdown(f"```python\n{code_snippet}\n```")
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(code_snippet)
    display_search_results(search_results)
    export_text_to_file(code_snippet, "md")

def generate_recipe(ingredients):
    prompt = f"Create a recipe using the following ingredients: {ingredients}"
    recipe = generate_content(prompt)
    st.markdown(recipe)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(recipe)
    display_search_results(search_results)
    export_text_to_file(recipe, "md")

def generate_song_lyrics(theme):
    prompt = f"Write song lyrics about {theme}"
    lyrics = generate_content(prompt)
    st.markdown(lyrics)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(lyrics)
    display_search_results(search_results)
    export_text_to_file(lyrics, "md")

def generate_workout_plan(fitness_goal):
    prompt = f"Create a workout plan to achieve the following fitness goal: {fitness_goal}"
    workout_plan = generate_content(prompt)
    st.markdown(workout_plan)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(workout_plan)
    display_search_results(search_results)
    export_text_to_file(workout_plan, "md")

def generate_travel_itinerary(destination):
    prompt = f"Create a travel itinerary for a trip to {destination}"
    itinerary = generate_content(prompt)
    st.markdown(itinerary)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(itinerary)
    display_search_results(search_results)
    export_text_to_file(itinerary, "md")

def generate_business_plan(business_idea):
    prompt = f"Create a business plan for the following idea: {business_idea}"
    business_plan = generate_content(prompt)
    st.markdown(business_plan)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(business_plan)
    display_search_results(search_results)
    export_text_to_file(business_plan, "md")

def generate_study_schedule(subjects, time):
    prompt = f"Create a study schedule for the following subjects: {subjects} and available time: {time}"
    study_schedule = generate_content(prompt)
    st.markdown(study_schedule)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(study_schedule)
    display_search_results(search_results)
    export_text_to_file(study_schedule, "md")

def generate_book_summary(title, author):
    prompt = f"Summarize the book titled '{title}' by {author}"
    book_summary = generate_content(prompt)
    st.markdown(book_summary)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(book_summary)
    display_search_results(search_results)
    export_text_to_file(book_summary, "md")

def generate_meditation_guide(preferences):
    prompt = f"Create a meditation guide based on the following preferences: {preferences}"
    meditation_guide = generate_content(prompt)
    st.markdown(meditation_guide)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(meditation_guide)
    display_search_results(search_results)
    export_text_to_file(meditation_guide, "md")

def generate_marketing_strategy(business_goals):
    prompt = f"Create a marketing strategy to achieve the following business goals: {business_goals}"
    marketing_strategy = generate_content(prompt)
    st.markdown(marketing_strategy)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(marketing_strategy)
    display_search_results(search_results)
    export_text_to_file(marketing_strategy, "md")

def generate_investment_plan(financial_goals):
    prompt = f"Create an investment plan to achieve the following financial goals: {financial_goals}"
    investment_plan = generate_content(prompt)
    st.markdown(investment_plan)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(investment_plan)
    display_search_results(search_results)
    export_text_to_file(investment_plan, "md")

def generate_meal_plan(dietary_preferences):
    prompt = f"Create a meal plan based on the following dietary preferences: {dietary_preferences}"
    meal_plan = generate_content(prompt)
    st.markdown(meal_plan)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(meal_plan)
    display_search_results(search_results)
    export_text_to_file(meal_plan, "md")

def generate_job_description(role):
    prompt = f"Create a job description for the following role: {role}"
    job_description = generate_content(prompt)
    st.markdown(job_description)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(job_description)
    display_search_results(search_results)
    export_text_to_file(job_description, "md")

def generate_interview_questions(job_role):
    prompt = f"Create a list of interview questions for the following job role: {job_role}"
    interview_questions = generate_content(prompt)
    st.markdown(interview_questions)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(interview_questions)
    display_search_results(search_results)
    export_text_to_file(interview_questions, "md")

def generate_fashion_advice(trends):
    prompt = f"Provide fashion advice based on the following trends: {trends}"
    fashion_advice = generate_content(prompt)
    st.markdown(fashion_advice)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(fashion_advice)
    display_search_results(search_results)
    export_text_to_file(fashion_advice, "md")

def generate_home_decor_ideas(theme):
    prompt = f"Suggest home decor ideas based on the following theme: {theme}"
    home_decor_ideas = generate_content(prompt)
    st.markdown(home_decor_ideas)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(home_decor_ideas)
    display_search_results(search_results)
    export_text_to_file(home_decor_ideas, "md")

def generate_event_plan(event_type):
    prompt = f"Create an event plan for the following type of event: {event_type}"
    event_plan = generate_content(prompt)
    st.markdown(event_plan)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(event_plan)
    display_search_results(search_results)
    export_text_to_file(event_plan, "md")

def generate_speech(topic):
    prompt = f"Create a speech on the following topic: {topic}"
    speech = generate_content(prompt)
    st.markdown(speech)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(speech)
    display_search_results(search_results)
    export_text_to_file(speech, "md")

def generate_product_description(features):
    prompt = f"Create a product description based on the following features: {features}"
    product_description = generate_content(prompt)
    st.markdown(product_description)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(product_description)
    display_search_results(search_results)
    export_text_to_file(product_description, "md")

def generate_slogan(brand):
    prompt = f"Create a catchy slogan for the following brand or product: {brand}"
    slogan = generate_content(prompt)
    st.markdown(slogan)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(slogan)
    display_search_results(search_results)
    export_text_to_file(slogan, "md")

def generate_art_description(art_piece):
    prompt = f"Create a description for the following piece of art: {art_piece}"
    art_description = generate_content(prompt)
    st.markdown(art_description)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(art_description)
    display_search_results(search_results)
    export_text_to_file(art_description, "md")

def generate_horoscope(zodiac_sign):
    prompt = f"Provide a horoscope for the following zodiac sign: {zodiac_sign}"
    horoscope = generate_content(prompt)
    st.markdown(horoscope)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(horoscope)
    display_search_results(search_results)
    export_text_to_file(horoscope, "md")

def generate_love_letter(feelings):
    prompt = f"Write a love letter based on the following feelings: {feelings}"
    love_letter = generate_content(prompt)
    st.markdown(love_letter)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(love_letter)
    display_search_results(search_results)
    export_text_to_file(love_letter, "md")

def generate_apology_letter(situation):
    prompt = f"Write an apology letter for the following situation: {situation}"
    apology_letter = generate_content(prompt)
    st.markdown(apology_letter)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(apology_letter)
    display_search_results(search_results)
    export_text_to_file(apology_letter, "md")

def generate_resume(user_input):
    prompt = f"Create a resume based on the following input: {user_input}"
    resume = generate_content(prompt)
    st.markdown(resume)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(resume)
    display_search_results(search_results)
    export_text_to_file(resume, "md")

def generate_cover_letter(job_application):
    prompt = f"Create a cover letter for the following job application: {job_application}"
    cover_letter = generate_content(prompt)
    st.markdown(cover_letter)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(cover_letter)
    display_search_results(search_results)
    export_text_to_file(cover_letter, "md")

def generate_bucket_list(preferences):
    prompt = f"Create a bucket list based on the following preferences: {preferences}"
    bucket_list = generate_content(prompt)
    st.markdown(bucket_list)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(bucket_list)
    display_search_results(search_results)
    export_text_to_file(bucket_list, "md")

def generate_daily_affirmations(user_input):
    prompt = f"Provide daily affirmations based on the following input: {user_input}"
    daily_affirmations = generate_content(prompt)
    st.markdown(daily_affirmations)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(daily_affirmations)
    display_search_results(search_results)
    export_text_to_file(daily_affirmations, "md")

def generate_fitness_challenge(goals):
    prompt = f"Create a fitness challenge to achieve the following goals: {goals}"
    fitness_challenge = generate_content(prompt)
    st.markdown(fitness_challenge)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(fitness_challenge)
    display_search_results(search_results)
    export_text_to_file(fitness_challenge, "md")

def generate_cleaning_schedule(home):
    prompt = f"Create a cleaning schedule for the following home details: {home}"
    cleaning_schedule = generate_content(prompt)
    st.markdown(cleaning_schedule)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(cleaning_schedule)
    display_search_results(search_results)
    export_text_to_file(cleaning_schedule, "md")

def generate_diy_project(materials):
    prompt = f"Suggest DIY projects based on the following materials: {materials}"
    diy_project = generate_content(prompt)
    st.markdown(diy_project)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(diy_project)
    display_search_results(search_results)
    export_text_to_file(diy_project, "md")

def generate_parenting_advice(child_age):
    prompt = f"Provide parenting advice for a child of the following age: {child_age}"
    parenting_advice = generate_content(prompt)
    st.markdown(parenting_advice)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(parenting_advice)
    display_search_results(search_results)
    export_text_to_file(parenting_advice, "md")

def generate_gardening_tips(plant_type):
    prompt = f"Suggest gardening tips for the following type of plant: {plant_type}"
    gardening_tips = generate_content(prompt)
    st.markdown(gardening_tips)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(gardening_tips)
    display_search_results(search_results)
    export_text_to_file(gardening_tips, "md")

def generate_pet_care_guide(pet_type):
    prompt = f"Provide a pet care guide for the following type of pet: {pet_type}"
    pet_care_guide = generate_content(prompt)
    st.markdown(pet_care_guide)
    st.subheader("Searching for Similar Content Online:")
    search_results = search_web(pet_care_guide)
    display_search_results(search)
