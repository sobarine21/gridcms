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
    return generate_content(prompt)

def generate_code_snippet(description):
    prompt = f"Generate a code snippet for {description}"
    return generate_content(prompt)

def generate_recipe(ingredients):
    prompt = f"Create a recipe using the following ingredients: {ingredients}"
    return generate_content(prompt)

def generate_song_lyrics(theme):
    prompt = f"Write song lyrics about {theme}"
    return generate_content(prompt)

def generate_workout_plan(fitness_goal):
    prompt = f"Create a workout plan to achieve the following fitness goal: {fitness_goal}"
    return generate_content(prompt)

def generate_travel_itinerary(destination):
    prompt = f"Create a travel itinerary for a trip to {destination}"
    return generate_content(prompt)

def generate_business_plan(business_idea):
    prompt = f"Create a business plan for the following idea: {business_idea}"
    return generate_content(prompt)

def generate_study_schedule(subjects, time):
    prompt = f"Create a study schedule for the following subjects: {subjects} and available time: {time}"
    return generate_content(prompt)

def generate_book_summary(title, author):
    prompt = f"Summarize the book titled '{title}' by {author}"
    return generate_content(prompt)

def generate_meditation_guide(preferences):
    prompt = f"Create a meditation guide based on the following preferences: {preferences}"
    return generate_content(prompt)

def generate_marketing_strategy(business_goals):
    prompt = f"Create a marketing strategy to achieve the following business goals: {business_goals}"
    return generate_content(prompt)

def generate_investment_plan(financial_goals):
    prompt = f"Create an investment plan to achieve the following financial goals: {financial_goals}"
    return generate_content(prompt)

def generate_meal_plan(dietary_preferences):
    prompt = f"Create a meal plan based on the following dietary preferences: {dietary_preferences}"
    return generate_content(prompt)

def generate_job_description(role):
    prompt = f"Create a job description for the following role: {role}"
    return generate_content(prompt)

def generate_interview_questions(job_role):
    prompt = f"Create a list of interview questions for the following job role: {job_role}"
    return generate_content(prompt)

def generate_fashion_advice(trends):
    prompt = f"Provide fashion advice based on the following trends: {trends}"
    return generate_content(prompt)

def generate_home_decor_ideas(theme):
    prompt = f"Suggest home decor ideas based on the following theme: {theme}"
    return generate_content(prompt)

def generate_event_plan(event_type):
    prompt = f"Create an event plan for the following type of event: {event_type}"
    return generate_content(prompt)

def generate_speech(topic):
    prompt = f"Create a speech on the following topic: {topic}"
    return generate_content(prompt)

def generate_product_description(features):
    prompt = f"Create a product description based on the following features: {features}"
    return generate_content(prompt)

def generate_slogan(brand):
    prompt = f"Create a catchy slogan for the following brand or product: {brand}"
    return generate_content(prompt)

def generate_art_description(art_piece):
    prompt = f"Create a description for the following piece of art: {art_piece}"
    return generate_content(prompt)

def generate_horoscope(zodiac_sign):
    prompt = f"Provide a horoscope for the following zodiac sign: {zodiac_sign}"
    return generate_content(prompt)

def generate_love_letter(feelings):
    prompt = f"Write a love letter based on the following feelings: {feelings}"
    return generate_content(prompt)

def generate_apology_letter(situation):
    prompt = f"Write an apology letter for the following situation: {situation}"
    return generate_content(prompt)

def generate_resume(user_input):
    prompt = f"Create a resume based on the following input: {user_input}"
    return generate_content(prompt)

def generate_cover_letter(job_application):
    prompt = f"Create a cover letter for the following job application: {job_application}"
    return generate_content(prompt)

def generate_bucket_list(preferences):
    prompt = f"Create a bucket list based on the following preferences: {preferences}"
    return generate_content(prompt)

def generate_daily_affirmations(user_input):
    prompt = f"Provide daily affirmations based on the following input: {user_input}"
    return generate_content(prompt)

def generate_fitness_challenge(goals):
    prompt = f"Create a fitness challenge to achieve the following goals: {goals}"
    return generate_content(prompt)

def generate_cleaning_schedule(home):
    prompt = f"Create a cleaning schedule for the following home details: {home}"
    return generate_content(prompt)

def generate_diy_project(materials):
    prompt = f"Suggest DIY projects based on the following materials: {materials}"
    return generate_content(prompt)

def generate_parenting_advice(child_age):
    prompt = f"Provide parenting advice for a child of the following age: {child_age}"
    return generate_content(prompt)

def generate_gardening_tips(plant_type):
    prompt = f"Suggest gardening tips for the following type of plant: {plant_type}"
    return generate_content(prompt)

def generate_pet_care_guide(pet_type):
    prompt = f"Provide a pet care guide for the following type of pet: {pet_type}"
    return generate_content(prompt)

def generate_photography_tips(user_input):
    prompt = f"Suggest photography tips based on the following input: {user_input}"
    return generate_content(prompt)

def generate_language_learning_plan(target_language):
    prompt = f"Create a language learning plan for the following target language: {target_language}"
    return generate_content(prompt)

def generate_mindfulness_exercises(preferences):
    prompt = f"Provide mindfulness exercises based on the following preferences: {preferences}"
    return generate_content(prompt)

def generate_stress_management_tips(user_input):
    prompt = f"Suggest stress management tips based on the following input: {user_input}"
    return generate_content(prompt)

def generate_sleep_schedule(user_needs):
    prompt = f"Create a sleep schedule based on the following needs: {user_needs}"
    return generate_content(prompt)

def generate_career_advice(user_goals):
    prompt = f"Provide career advice based on the following goals: {user_goals}"
    return generate_content(prompt)

def generate_social_media_content(platform):
    prompt = f"Suggest social media content ideas based on the following platform: {platform}"
    return generate_content(prompt)

def generate_dating_profile(user_input):
    prompt = f"Create a dating profile based on the following input: {user_input}"
    return generate_content(prompt)

def generate_playlist(mood):
    prompt = f"Provide a music playlist based on the following mood: {mood}"
    return generate_content(prompt)

def generate_movie_recommendations(user_preferences):
    prompt = f"Suggest movies based on the following preferences: {user_preferences}"
    return generate_content(prompt)

def generate_book_recommendations(user_input):
    prompt = f"Provide book recommendations based on the following input: {user_input}"
    return generate_content(prompt)

def generate_game_ideas(user_preferences):
    prompt = f"Suggest game ideas based on the following preferences: {user_preferences}"
    return generate_content(prompt)

def generate_science_experiment(materials):
    prompt = f"Suggest science experiments based on the following materials: {materials}"
    return generate_content(prompt)

def generate_magic_trick(skill_level):
    prompt = f"Suggest magic tricks based on the following skill level: {skill_level}"
    return generate_content(prompt)

def generate_travel_packing_list(destination, duration):
    prompt = f"Provide a packing list for a trip to {destination} for a duration of {duration}"
    return generate_content(prompt)

def generate_diet_plan(dietary_goals):
    prompt = f"Create a diet plan to achieve the following dietary goals: {dietary_goals}"
    return generate_content(prompt)

def generate_inspirational_quote(theme):
    prompt = f"Provide an inspirational quote about {theme}"
    return generate_content(prompt)

def generate_fun_fact(theme):
    prompt = f"Provide a fun fact about {theme}"
    return generate_content(prompt)

def generate_parenting_tips(child_age):
    prompt = f"Provide parenting tips for a child of the following age: {child_age}"
    return generate_content(prompt)

def generate_trivia_question(theme):
    prompt = f"Create a trivia question about {theme}"
    return generate_content(prompt)

def generate_poetry_analysis(poem):
    prompt = f"Analyze the following poem: {poem}"
    return generate_content(prompt)

def generate_short_story(theme):
    prompt = f"Write a short story about {theme}"
    return generate_content(prompt)

def generate_journal_prompt(theme):
    prompt = f"Provide a journal prompt about {theme}"
    return generate_content(prompt)

def generate_icebreaker_question(theme):
    prompt = f"Provide an icebreaker question about {theme}"
    return generate_content(prompt)

def generate_travel_guide(destination):
    prompt = f"Create a travel guide for {destination}"
    return generate_content(prompt)

def generate_cooking_tip(ingredient):
    prompt = f"Provide a cooking tip for {ingredient}"
    return generate_content(prompt)

def generate_yoga_routine(goal):
    prompt = f"Create a yoga routine to achieve the following goal: {goal}"
    return generate_content(prompt)

def generate_motivational_speech(theme):
    prompt = f"Write a motivational speech about {theme}"
    return generate_content(prompt)

def generate_skincare_routine(skin_type):
    prompt = f"Create a skincare routine for the following skin type: {skin_type}"
    return generate_content(prompt)

def generate_birthday_message(theme):
    prompt = f"Write a birthday message about {theme}"
    return generate_content(prompt)

def generate_life_hack(category):
    prompt = f"Provide a life hack for {category}"
    return generate_content(prompt)

def generate_healthy_snack_idea(ingredient):
    prompt = f"Suggest a healthy snack idea using {ingredient}"
    return generate_content(prompt)

def generate_self_care_tip(category):
    prompt = f"Provide a self-care tip for {category}"
    return generate_content(prompt)

def generate_diy_craft_idea(materials):
    prompt = f"Suggest a DIY craft idea using {materials}"
    return generate_content(prompt)

def generate_fitness_tip(goal):
    prompt = f"Provide a fitness tip for {goal}"
    return generate_content(prompt)

def generate_personal_motto(theme):
    prompt = f"Create a personal motto about {theme}"
    return generate_content(prompt)

def generate_daily_planner(tasks):
    prompt = f"Create a daily planner for the following tasks: {tasks}"
    return generate_content(prompt)

def generate_weekly_planner(tasks):
    prompt = f"Create a weekly planner for the following tasks: {tasks}"
    return generate_content(prompt)

def generate_monthly_planner(tasks):
    prompt = f"Create a monthly planner for the following tasks: {tasks}"
    return generate_content(prompt)

def generate_yearly_goal(goal):
    prompt = f"Create a yearly goal plan for {goal}"
    return generate_content(prompt)

def generate_budget_plan(financial_goal):
    prompt = f"Create a budget plan to achieve the following financial goal: {financial_goal}"
    return generate_content(prompt)

def generate_home_organization_tip(category):
    prompt = f"Provide a home organization tip for {category}"
    return generate_content(prompt)

def generate_language_tip(language):
    prompt = f"Provide a language learning tip for {language}"
    return generate_content(prompt)

def generate_productivity_tip(task):
    prompt = f"Provide a productivity tip for {task}"
    return generate_content(prompt)

def generate_study_tip(subject):
    prompt = f"Provide a study tip for {subject}"
    return generate_content(prompt)

def generate_travel_tip(destination):
    prompt = f"Provide a travel tip for {destination}"
    return generate_content(prompt)

def generate_career_tip(field):
    prompt = f"Provide a career tip for {field}"
    return generate_content(prompt)

def generate_networking_tip(goal):
    prompt = f"Provide a networking tip to achieve the following goal: {goal}"
    return generate_content(prompt)

def generate_public_speaking_tip(theme):
    prompt = f"Provide a public speaking tip for {theme}"
    return generate_content(prompt)

def generate_leadership_tip(goal):
    prompt = f"Provide a leadership tip to achieve the following goal: {goal}"
    return generate_content(prompt)

def generate_team_building_activity(goal):
    prompt = f"Suggest a team-building activity to achieve the following goal: {goal}"
    return generate_content(prompt)

def generate_conflict_resolution_tip(situation):
    prompt = f"Provide a conflict resolution tip for the following situation: {situation}"
    return generate_content(prompt)

def generate_time_management_tip(task):
    prompt = f"Provide a time management tip for {task}"
    return generate_content(prompt)

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
        generated_text = generate_content(prompt)
        st.session_state.session_count += 1
        st.session_state.generated_text = generated_text 
