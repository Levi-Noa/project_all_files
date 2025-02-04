import os
import sys  
from flask import Flask, request, render_template, redirect, url_for, flash
import google.generativeai as genai
import csv
from dotenv import load_dotenv
import re
from urllib.parse import unquote
import secrets
import logging

# Dynamically get the absolute path of the current script and add its parent directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from generate_about import generate_about_for_user

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(16))  # Use the .env key or generate one

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Define the Gemini Model
model = genai.GenerativeModel('gemini-pro')

def generate_linkedin_about(user_data):

    
    prompt = f"""
        Please generate a {user_data['length'] if user_data['length'] else "compelling and professional"} {user_data['format'] if user_data['format'] else ""} "About" section for a LinkedIn profile using the following information:

        *Current Role & Industry:*
      Current Title: {user_data['role_industry']['current_title']}
      Company: {user_data['role_industry']['company']}

      *Previous Roles & Industries:*
      {user_data['previous_roles_industries']['previous_roles_industries']}
      
      *Education:*
      {user_data['education']['education']}
      
      *skills & Capabilities:*
      Tasks: {user_data['skills_strengths']['hard_skills']}

      *Passion & Goals:*
      Passion: {user_data['passion_values']['passion']}
      Goals: {user_data['passion_values']['goals']}

      *About sections of similar profiles:*
      About sections: {', '.join(user_data['similar_profiles']['abouts'])}

      *Student:* {user_data['student']['student']}

      Please make sure to write a LinkedIn "About" section that is:
       - Targeted and Relevant: Focused on the user's {user_data['focus']}!!.
       - Optimized for LinkedIn: Using relevant keywords.
       - Use similar users data if they seem to have similar carreer paths.
       Output only the "About" section text.
    """
    print(prompt)
    response = model.generate_content(prompt)
    return response.text

@app.route('/')
def form():
    return render_template('Form.html')

@app.route('/submit', methods=['POST'])
def submit():
    userId = request.form.get('userId')
    if userId:
        userId = unquote(userId.strip())  # Decode URL-encoded characters
    if not userId:
        userLink = request.form.get('userLink')
        # Regular expression to match the pattern of LinkedIn profile URL
        match = re.search(r"linkedin\.com/in/([a-zA-Z0-9\-]+)", userLink)
        if match:
            userId = match.group(1)
        else:
            userId = None
            
    goals = request.form.get('goals')
    passions = request.form.get('passions')
    is_student = request.form.get('student') == 'Yes'
    format_section = request.form.get('format')
    length = request.form.get('length')
    focus = request.form.get('focus')
    
    generated_about, generated_score = generate_about_for_user(userId, is_student, passions, goals, format_section, length, focus)
    if generated_score == -1:
        user_found = False
    else:
        user_found = True
    if not user_found:
        flash('User not found. Please enter a valid LinkedIn User ID.', 'error')
        return redirect(url_for('form'))

    linkedin_about = generated_about.split('*')[-1]
    linkedin_about = linkedin_about.split(':')[-1]
    return render_template('result.html', linkedin_about=linkedin_about)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
    #app.run(debug=True)