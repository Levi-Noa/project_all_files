# LinkedIn About Generator

## 📌 Overview
This project generates a **personalized LinkedIn "About" section** based on similar users and the user's provided details. The feature leverages **embeddings, clustering, and AI models** to create a compelling, tailored description.

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
   git clone <repository-url>
   cd linkedin-about-generator
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Rename `.envTemplate` to `.env` and set the environment variables:
   ```
   mv .envTemplate .env
   ```
   Edit the `.env` file to set your environment variables:
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

**What this means:**

- The system initializes and connects to MongoDB.
- It retrieves the total number of users in the embeddings collection.
- Any warnings (like missing Hadoop libraries) can be ignored.

#### 2️⃣ Processing a Request

When a request is sent to generate a LinkedIn "About" section, logs will appear in the terminal.

**Example Request (via API or Web Form Submission):**

   ```plaintext
   <timestamp> INFO - Generating LinkedIn About section for user_id: <USER_ID>
   <timestamp> INFO - Fetching user <USER_ID> data from MongoDB...
   <timestamp> INFO - Searching for user: <USER_ID>
   <timestamp> INFO - User <USER_ID> is assigned to cluster: <CLUSTER_ID>
   ```

**What this means:**

- The system fetches user data from MongoDB.
- It finds which cluster the user belongs to, allowing the AI model to compare similar profiles.

#### 3️⃣ Extracting Similar Users

The system retrieves similar users based on cluster embeddings.

**Expected Output:**

   ```plaintext
   <timestamp> INFO - Extracting similar users for user_id <USER_ID> in cluster <CLUSTER_ID>...
   <timestamp> INFO - Fetching similar users for user <USER_ID> in cluster <CLUSTER_ID>...
   <timestamp> INFO - Found <TOTAL_USERS> users in cluster <CLUSTER_ID> before filtering.
   <timestamp> INFO - Users with 'About' score >= 6: <FILTERED_USERS> out of <TOTAL_USERS>
   ```

**What this means:**

- The system finds all users in the same cluster.
- It filters users with a high-quality "About" section (score >= 6).
- The number of filtered users is displayed.

#### 4️⃣ Generating the AI Prompt

The system builds a structured prompt for Google Gemini AI.

**Expected Output:**

   ```plaintext
   <timestamp> INFO - Found <NUMBER_OF_SIMILAR_USERS> relevant 'About' sections for user_id <USER_ID>.
   <timestamp> INFO - Final API prompt:
   (Here, the full structured prompt is displayed.)
   ```

**What this means:**

- The AI receives structured data with key details.
- The AI incorporates similar users' insights to generate a personalized LinkedIn "About" section.

#### 5️⃣ Generating & Returning the Final Output

Once the AI processes the request, the LinkedIn About section is generated.

**Expected Output:**

   ```plaintext
   <timestamp> INFO - <IP_ADDRESS> - - [<DATE>] "POST /submit HTTP/1.1" 200 -
   ```

**What this means:**

- The AI successfully generated the "About" section.
- The HTTP 200 status confirms successful processing.
- The output is now available in the web UI or API response.

Once the AI processes the request, the LinkedIn About section is generated.

**Expected Output:**

   ```plaintext
   <timestamp> INFO - <IP_ADDRESS> - - [<DATE>] "POST /submit HTTP/1.1" 200 -
   ```

**What this means:**

- The AI successfully generated the "About" section.
- The HTTP 200 status confirms successful processing.
- The output is now available in the web UI or API response.

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


