# LinkedIn About Generator
## 📌 Overview
This project generates a **personalized LinkedIn "About" section** based on similar users and the user's provided details. The feature leverages **embeddings, clustering, and AI models** to create a compelling, tailored description.

---

## 1.1 Concept and Motivation
In recent years, LinkedIn has become a massive social network with a unique culture centered around the professional and academic careers of its users. Professionals share insights about their work and expertise daily, making the platform a key hub for career growth and networking. However, despite its importance, many users struggle to craft a compelling 'About' section that effectively highlights their skills and experience - only 21% of the users in our data have filled out their 'About' section. Our project aims to bridge this gap by developing an AI-powered tool that generates personalized 'About' sections, helping users create impactful profiles that better showcase their professional strengths.

## 1.2 Workflow
Our workflow consists of five main stages: Data Collection, Scoring and Creating a Base Group, Clustering, Finding Similar Users, and Generating.

- **Data Collection**: We begin by scraping job position data from the O*NET website, extracting information on 1,016 different positions, each with its associated common tasks.
- **Scoring and Creating a Base Group**: We develop a scoring system for LinkedIn 'About' sections to assess their effectiveness. This helps create a base group of well-structured profiles, which serves as a reference for generating new content.
- **Clustering**: We create a text representing each user based on its attributes, and then use the BERT embedding of this text as the initial vector representation of the users. We then assign the target user to a cluster. The clusters were computed using the K-Means algorithm, with K = 148, that was trained only on users with an existing 'About' section.
- **Finding Similar Users**: We identify similar users in the target user's cluster, and we search only users that have an 'About' score above a predefined threshold. Similarity is computed by comparing their attributes and job roles using embedding-based cosine similarity, ensuring personalized and relevant content generation.
- **Generating**: We use the Gemini API to generate a personalized 'About' section for the target user, incorporating insights from previous stages along with their basic data generation.

---

## 🚀 Usage

Send a request with the relevant parameters to generate a **custom LinkedIn "About" section**.  
The system analyzes **similar user profiles** and user-provided data (via `userId` or `userLink`) to craft a professional summary.  

---

## 🎥 Video Demonstration
To see how the feature works, watch this **demo video**:  
[![Watch the Demo](https://img.youtube.com/vi/SINRY2aq6Ak/0.jpg)](https://www.youtube.com/watch?v=SINRY2aq6Ak)  

📌 **Click the image above to watch the tutorial!**  

---

## 📂 Project Structure
```
/linkedin-about-generator/
│
├── /app/                     # Main application files
│   ├── server.py             # Flask API for handling requests
│   ├── generate_about.py     # Logic for generating the LinkedIn "About" section
│   ├── pre_process.py        # Data loading & preprocessing from MongoDB
│   ├── templates/            # HTML templates for the website
│   │   ├── Form.html         # Input form for user data
│   │   ├── result.html       # Displays the generated "About" section
│
├── /data/                    # Stores processed embeddings & data
│   ├── embedding_df.csv      # Preprocessed embeddings
│   ├── basic_data_df.csv     # User profiles from MongoDB
│
├── Dockerfile                # Containerization setup
├── requirements.txt          # Required dependencies
├── README.md                 # Project documentation (this file)
│
└── .env                      # Environment variables (API keys, DB credentials)
```

---
## 📝 Instructions

1. Clone the repository:
   ```
   git clone https://github.com/Levi-Noa/project_all_files.git
   ```

2. Rename `.envTemplate` to `.env` :
   ```
   mv .envTemplate .env
   ```
   
3. Edit the `.env` file to set your environment variables:
   ```plaintext
   GOOGLE_API_KEY=<Set-your_google_api_key_here>
   MONGO_URI=<Set-your-mongo-uri>
   NUM_OF_LINKEDIN_SIMILAR_PROFILES=5
   GEMINI_MODEL="gemini-pro"
   ```

   **Setting Up Environment Variables**

   ### GOOGLE_API_KEY:
   1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
   2. Create/select a project and navigate to **APIs & Services** > **Credentials**.
   3. Click **Create credentials** > **API key**.
   4. Copy the API key and replace `<Set-your_google_api_key_here>`.

   ### MONGO_URI:
   1. Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
   2. Create/use a cluster, add a user in **Database Access**, and add your IP in **Network Access**.
   3. Click **Connect** on your cluster, choose **Connect your application**, and replace `<Set-your-mongo-uri>` with the connection string.
## Docker Instructions

To build and run the Docker image for this application, follow these steps:

1. Build the Docker image:
   ```
   docker build -t linkedin-about-generator .
   ```

2. Run the Docker container:
   ```
   docker run -p 5001:5000 linkedin-about-generator
   ```
   **To see the application, after running the Docker container, open your web browser and navigate to:**

         http://localhost:5001/
   ---

## 📭 API Endpoints
**POST `/submit`**  
🔹 Generates the LinkedIn "About" section based on user input.

| **Parameter**  | **Type**  | **Description** |
|---------------|----------|----------------|
| `userId`      | `string`  | Unique LinkedIn user ID |
| `userLink`    | `string`  | Full LinkedIn profile URL |
| `goals`       | `string`  | User's career goals |
| `passions`    | `string`  | User's passions |
| `is_student`  | `boolean` | Whether the user is a student |
| `format`      | `string`  | Format of the "About" section (e.g., bullet points, paragraph) |
| `length`      | `string`  | Desired length (short, medium, long) |
| `focus`       | `string`  | Main focus (e.g., skills, leadership, career growth) |

---

## 📌 How the Output is Generated

#### 1️⃣ User Data Extraction
The system fetches user details from MongoDB using `userId` or `userLink`.

**Extracted details include:**
- 📌 Current Role & Company
- 📌 Previous Experience
- 📌 Education & Skills
- 📌 Passions & Goals (if provided)

#### 2️⃣ Finding Similar Profiles
The system retrieves profiles from the same cluster based on their embeddings.

**Criteria for consideration:**
- ✅ Users with a high "About" quality score (above 6)
- ✅ Cosine similarity is used to rank the most relevant users

#### 3️⃣ Structuring the AI Prompt
The AI receives a detailed, structured prompt, including:

- 📌 User’s Career Background
- 📌 Key Skills & Responsibilities
- 📌 Personal Goals & Passions
- 📌 Similar Users’ "About" Sections

#### 4️⃣ Generating the Final Output
The AI writes a professional, SEO-friendly LinkedIn "About" section:

- ✅ The result incorporates elements from similar users where relevant
- ✅ The output is tailored based on selected preferences (tone, length, focus)


🚀 This ensures a highly relevant, personalized, and industry-specific LinkedIn summary!


## 📌 Monitoring the Workflow & Expected Output

When running the application, you should expect structured logs that help monitor the workflow. Below is a breakdown of the expected terminal output and how to interpret it.

#### 1️⃣ Starting the Application

When you run the Docker container, the system initializes the environment, loads dependencies, and connects to MongoDB.

**Command to start the container:**

   ```bash
   docker run -p 5001:5000 linkedin-about-generator
   ```
   **Expected Output:**

   ```plaintext
   <timestamp> INFO - Connecting to MongoDB...
   <timestamp> INFO - Connected to MongoDB.
   <timestamp> INFO - Total users in embedding_users collection: <NUMBER_OF_USERS>
   <timestamp> INFO - Closing down clientserver connection
   ```

   **Explanation:**

   - System initializes and connects to MongoDB.
   - Ignore warnings like missing Hadoop libraries.

   #### 2️⃣ Processing a Request

   Logs appear when generating a LinkedIn "About" section.

   **Example Request:**

   ```plaintext
   <timestamp> INFO - Generating LinkedIn About section for user_id: <USER_ID>
   <timestamp> INFO - Fetching user <USER_ID> data from MongoDB...
   <timestamp> INFO - Searching for user: <USER_ID>
   <timestamp> INFO - User <USER_ID> is assigned to cluster: <CLUSTER_ID>
   ```

   **Explanation:**

   - Fetches user data and assigns cluster for comparison.

   #### 3️⃣ Extracting Similar Users

   Retrieves similar users based on cluster embeddings.

   **Expected Output:**

   ```plaintext
   <timestamp> INFO - Extracting similar users for user_id <USER_ID> in cluster <CLUSTER_ID>...
   <timestamp> INFO - Fetching similar users for user <USER_ID> in cluster <CLUSTER_ID>...
   <timestamp> INFO - Found similar users in cluster <CLUSTER_ID> before filtering.
   <timestamp> INFO - Users with 'About' score >= 6: <FILTERED_USERS> out of <TOTAL_USERS>
   ```

   **Explanation:**

   - Finds and filters users with high-quality "About" sections.

   #### 4️⃣ Generating the AI Prompt

   Builds a structured prompt for Google Gemini AI.

   **Expected Output:**

   ```plaintext
   <timestamp> INFO - Found <NUMBER_OF_SIMILAR_USERS> relevant 'About' sections for user_id <USER_ID>.
   <timestamp> INFO - Final API prompt:
   (Full structured prompt displayed here.)
   ```

   **Explanation:**

   - AI receives structured data to generate a personalized "About" section.

   #### 5️⃣ Generating & Returning the Final Output

   AI processes the request and generates the LinkedIn About section.

   **Expected Output:**

   ```plaintext
   <timestamp> INFO - <IP_ADDRESS> - - [<DATE>] "POST /submit HTTP/1.1" 200 -
   ```

   **Explanation:**

   - AI successfully generated the "About" section.
   - HTTP 200 status confirms successful processing.
   - Output available in web UI or API response.

#### 🔍 Troubleshooting & Monitoring Logs

If issues arise, use these steps to debug:

**Check for Errors:**

Look for lines containing `ERROR`.

**Example:**

   ```plaintext
   <timestamp> ERROR - Exception on /submit [POST]
   ```

This means an issue occurred while processing the request.

**View Live Logs:**

Use this command inside the running Docker container:

   ```bash
   docker logs -f <container_id>
   ```

Replace `<container_id>` with the actual Docker container ID.

**Check MongoDB Connection:**

If MongoDB is unreachable, restart it:

   ```bash
   sudo systemctl restart mongod
   ```

**Restart the Application:**

Stop the container and start again:

   ```bash
   docker stop <container_id>
   docker run -p 5001:5000 linkedin-about-generator
   ```

#### 🚀 Summary

- The system processes user data, finds similar profiles, and generates a LinkedIn About section.
- Logs show each processing step, from data extraction to AI generation.
- Use logs to debug issues, check MongoDB connectivity, and restart the application if needed.

📌 With these logs, you can easily monitor and optimize the LinkedIn About Generator's performance! 🔥



## 🛠️ Technologies Used
- **Python** (Flask, Pandas, NumPy, Scikit-learn)
- **MongoDB** (Database)
- **PySpark** (Data Processing)
- **Google Generative AI** (Gemini API)
- **Docker** (Containerization)

---


