import os
import sys
import logging
import google.generativeai as genai
from pyspark.sql import SparkSession
import numpy as np
from dotenv import load_dotenv
from pymongo import MongoClient
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote

# Ensure the script directory is in the PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Spark
spark = SparkSession.builder \
    .appName("LinkedInAboutGenerator") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.maxResultSize", "2g") \
    .getOrCreate()
    
# Configure logging to show all debug messages and force logs to be written immediately
logging.basicConfig(
    level=logging.INFO,  # Change from DEBUG to INFO or WARNING
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)


def extract_user_info(user_id, collection_basic_data):
    """
    Extracts user information directly from MongoDB, optimizing memory and query performance.
    
    - Avoids reading full CSVs.
    - Fetches only necessary fields from MongoDB.
    """
    NOT_AVAILABLE = "Not available"

    logging.info(f"Fetching user {user_id} data from MongoDB...")
    logging.info(f"Searching for user: {user_id}")

    # Try exact match first
    user_basic = collection_basic_data.find_one({"id": user_id})

    # If not found, try URL-encoded version
    if not user_basic:
        encoded_user_id = quote(user_id)
        logging.warning(f"User '{user_id}' not found. Retrying with encoded ID: {encoded_user_id}")
        user_basic = collection_basic_data.find_one({"id": encoded_user_id})

    # If still not found, try lowercase variant
    if not user_basic:
        lowercase_id = user_id.lower()
        logging.warning(f"User '{user_id}' not found with encoded ID. Retrying with lowercase ID: {lowercase_id}")
        user_basic = collection_basic_data.find_one({"id": lowercase_id})

    if not user_basic:
        logging.error(f"Final attempt: User '{user_id}' not found in MongoDB.")
        return None  # Return None if still not found

    if user_basic:
        return {
            "id": user_id,
            "about": "Not available",
            "current_position": user_basic.get("current_position_name", "Not available"),
            "current_company": user_basic.get("current_company_name", "Not available"),
            "previous_experience_list": user_basic.get("experience_list", "Not available"),
            "education_list": user_basic.get("education_list", "Not available"),
            "task_list": user_basic.get("tasks_list", "Not available"),
            "cluster": user_basic.get("cluster", None)
        }
    return None


def calculate_about_score(about_text):
    """
    Evaluates the quality of a LinkedIn 'About' section.
    """
    try:
        length_score = max(0, min(1, (len(about_text) - 100) / 200))
        professional_keywords = ["motivated", "experienced", "leader", "team", "driven",
                                 "goal-oriented", "skilled", "innovative", "results"]
        professionalism_score = sum(1 for word in professional_keywords if word in about_text.lower()) / len(professional_keywords)
        words = about_text.lower().split()
        engagement_score = len(set(words)) / len(words) if words else 0
        score = (0.4 * length_score) + (0.4 * professionalism_score) + (0.2 * engagement_score)
        return score * 10
    except Exception:
        return 0.0


def generate_from_prompt(user_data):
    """
    Generates LinkedIn 'About' section using Gemini API.
    """
    # Ensure a clear separation between each "About" section with a new line
    similar_profiles_about = "\n\n- " + "\n\n- ".join(user_data['similar_profiles']['abouts'])
    prompt = f"""
    Please generate a {user_data['length'] if user_data['length'] else "compelling and professional"} {user_data['format'] if user_data['format'] else ""} "About" section for a LinkedIn profile using the following details:

    *Current Role & Industry:*
    - Current Title: {user_data['role_industry']['current_title']}
    - Company: {user_data['role_industry']['company']}

    *Previous Roles & Industries:*
    - {user_data['previous_roles_industries']['previous_roles_industries']}
    
    *Education:*
    - {user_data['education']['education']}
    
    *Skills & Capabilities:*
    - Tasks: {user_data['skills_strengths']['hard_skills']}

    *Passion & Goals:*
    - Passion: {user_data['passion_values']['passion']}
    - Goals: {user_data['passion_values']['goals']}

    *Similar Profiles’ About Sections:* {similar_profiles_about}

    *Student:* {user_data['student']}

    Please ensure the LinkedIn "About" section:
    - Is targeted and relevant for the user's field.
    - Uses SEO-friendly keywords.
    - Incorporates similar users' data if applicable.
    - Focuses on: {user_data['focus']}.

    Output only the generated "About" section text.
    """
    logging.info(f"Final API prompt:\n{prompt}")

    try:
        response = genai.GenerativeModel("gemini-pro").generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Failed to generate content from Gemini API: {e}")
        return "Unable to generate LinkedIn About section at this time."


def extract_similar_users_abouts(user_id, number_of_top_users, cluster_id, collection_embeddings):
    logging.info(f"Extracting similar users for user_id {user_id} in cluster {cluster_id}...")

    # Step 1: Fetch the target user's embeddings
    user_data = collection_embeddings.find_one({"id": user_id}, {"_id": 0, "experience_averaged_embeddings": 1})
    if not user_data or "experience_averaged_embeddings" not in user_data:
        logging.warning(f"No embeddings found for user_id {user_id}.")
        return []

    user_embedding = np.array(user_data["experience_averaged_embeddings"]).reshape(1, -1)

    # Step 2: Fetch similar users in **one optimized query**
    similar_users_cursor = collection_embeddings.find(
        {"cluster": cluster_id, "id": {"$ne": user_id}},  
        {"id": 1, "about": 1, "experience_averaged_embeddings": 1, "_id": 0}  
    )
    similar_users_list = list(similar_users_cursor)
    logging.info(f"Found {len(similar_users_list)} users in cluster {cluster_id} before filtering.")

    if not similar_users_list:
        return []
    
    # Step 3: Filter users with an 'About' score >= 6
    filtered_users = []
    for user in similar_users_list:
        if "about" in user and "experience_averaged_embeddings" in user:
            about_text = user["about"]
            score = calculate_about_score(about_text)
            if score >= 6:
                filtered_users.append(user)

    logging.info(f"Users with 'About' score >= 6: {len(filtered_users)} out of {len(similar_users_list)}")

    if not filtered_users:
        logging.warning(f"No similar users with an 'About' score >= 6 found in cluster {cluster_id}.")
        return []

    # Step 4: Extract embeddings and about sections
    about_sections = [user["about"] for user in filtered_users]
    user_embeddings_np = []
    for user in filtered_users:
        embedding = user["experience_averaged_embeddings"]
        if isinstance(embedding, dict):
            if 'array' in embedding:
                embedding = embedding['array']
            elif 'values' in embedding:
                embedding = embedding['values']
            else:
                logging.error(f"Invalid embedding format for user {user['id']}: {embedding}")
                return []
        user_embeddings_np.append(embedding)

    user_embeddings_np = np.array(user_embeddings_np)

    if user_embeddings_np.size == 0:
        logging.warning("No valid embeddings found among similar users.")
        return []

    # Step 5: Compute cosine similarity scores
    try:
        similarity_scores = cosine_similarity(user_embedding, user_embeddings_np).flatten()
        logging.info(f"Similarity scores (first 3): {similarity_scores[:3]}")  # Show only the first 3 scores
    except Exception as e:
        logging.error(f"Error computing cosine similarity: {e}")
        return []

    # Step 6: Select top N similar users
    top_indices = np.argsort(similarity_scores)[-number_of_top_users:][::-1]  # Highest similarity first

    # Step 7: Extract top users' "About" sections
    top_about_sections = [about_sections[i] for i in top_indices if i < len(about_sections)]
    logging.info(f"Top about sections (first 50 chars of first 1): {[section[:50] for section in top_about_sections[:1]]}...")  # Show only the first 50 characters of the first about section

    logging.info(f"Found {len(top_about_sections)} relevant 'About' sections for user_id {user_id}.")

    return top_about_sections



def generate_final_response(about_table, user_info, is_student, passion, goals, format, length, focus):
    """
    Generates the final LinkedIn About response.
    """
    user_data_example = {
        "role_industry": {
            "current_title": f"{user_info['current_position']}",
            "company": f"{user_info['current_company']}",
        },
        "previous_roles_industries": {
            "previous_roles_industries": user_info['previous_experience_list']
        },
        "education": {
            "education": user_info['education_list']
        },
        "skills_strengths": {
            "hard_skills": user_info['task_list']
        },
        "passion_values": {
            "passion": passion if passion is not None else "",
            "goals": goals if goals is not None else ""
        },
        "similar_profiles": {
            "abouts": about_table
        },
        "student": "Yes" if is_student else "No",
        "format": format if format is not None else "",
        "length": length if length is not None else "",
        "focus": focus if focus is not None else ""
    }
    return generate_from_prompt(user_data_example)


def generate_about_for_user(user_id, is_student, passion, goals, format, length, focus):
    logging.info(f"Generating LinkedIn About section for user_id: {user_id}")

    # Ensure MongoDB connection
    MONGO_URI = os.getenv("MONGO_URI")
    client = MongoClient(MONGO_URI)
    db = client["linkdin_generator_database"]
    collection_basic_data = db["basic_data"]
    collection_embeddings = db["embedding_with_index"]

    # Fetch user data from MongoDB
    user_info = extract_user_info(user_id, collection_basic_data)
    if not user_info:
        return None, -1

    # Find similar profiles
    
    # Fetch cluster ID from embeddings table
    user_embedding_info = collection_embeddings.find_one({"id": user_id}, {"cluster": 1, "_id": 0})
    cluster_id = user_embedding_info.get("cluster") if user_embedding_info else None
    logging.info(f"User {user_id} is assigned to cluster: {cluster_id}")

    # Fetch all users in the same cluster
    cluster_users = list(collection_embeddings.find({"cluster": cluster_id}, {"id": 1, "_id": 0}))

    if not cluster_users:
        logging.error(f"No users found in cluster {cluster_id}. This may indicate missing data.")

    about_table = extract_similar_users_abouts(user_id, int(os.getenv("NUM_OF_LINKEDIN_SIMILAR_PROFILES", 5)), cluster_id, collection_embeddings)

    # Generate LinkedIn About section
    linkedin_about = generate_final_response(about_table, user_info, is_student, passion, goals, format, length, focus)
    if linkedin_about == "Unable to generate LinkedIn About section at this time.":
        return linkedin_about, -1
    score = calculate_about_score(linkedin_about) if linkedin_about else -1
    if linkedin_about == "Unable to generate LinkedIn About section at this time.":
        score = -1
    return linkedin_about, score



