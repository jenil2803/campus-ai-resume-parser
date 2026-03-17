# AI Resume Ranker for Campus Placements

Welcome! This application uses Artificial Intelligence to instantly read student resumes and rank them against a specific Job Description. It saves hours of manual reading by mathematically scoring how well a student's skills and projects match what a recruiter is looking for.

## 🏢 How It Works (The Architecture in Plain English)

Think of this project as an office with three rooms:

1. **The Student Intake Room (The Student Portal):** Students visit a simple webpage where they type in their name, Roll Number, and upload their Resume (as a PDF). The system automatically handles reading the PDF, figuring out their exact CGPA, and separating their "Projects" section from the rest of the text.
2. **The Filing Cabinet (The Database):** Once a student clicks submit, their information is safely locked away in a digital filing cabinet hosted in the cloud (MongoDB Atlas). 
3. **The Recruiter's Desk (The HR Dashboard):** The hiring manager visits a separate webpage. They type in the job requirements (the Job Description) and click "Process". The system's "Brain" (an AI language model called `MiniLM`) then reads every resume in the Filing Cabinet, understands the meaning of the words, and assigns each candidate a score out of 100%. The best matches float straight to the top of the leaderboard!

---

## 🚀 How to Run this App on Your Computer

You don't need to be a programmer to test this out! Just follow these step-by-step instructions.

### Step 1: Prepare Your Computer
Verify that your computer has **Python** installed. 
* Open your computer's Terminal (on Mac) or Command Prompt (on Windows) and type `python3 --version` or `python --version`. As long as it prints a number like `3.8` or higher, you are good to go!

### Step 2: Download the Project
In that same terminal window, copy and paste this command and press Enter to download the code to your computer:
```bash
git clone https://github.com/jenil2803/campus-ai-resume-parser.git
cd campus-ai-resume-parser
```

### Step 3: Install the "Engines"
The code relies on a few pre-built tools (like the PDF reader and the math engines). Tell your computer to install them by typing:
```bash
pip install -r requirements.txt
```
*(Note: If you are on a Mac, you might need to type `pip3` instead of `pip`).*

### Step 4: Add the Database Key
The application needs a "key" to open the cloud Filing Cabinet. 
1. Open the project folder (`campus-ai-resume-parser`) on your computer.
2. Create a brand new, blank file and name it exactly: `.env`
3. Open that `.env` file with any text editor (like Notepad or TextEdit).
4. Paste this exact line of text into the file and save it:
```txt
MONGO_URI=mongodb+srv://jenil28:jenil123@cluster0.g6ponuy.mongodb.net/?appName=Cluster0
```

### Step 5: Start the Student Portal
Go back to your terminal window. Let's turn on the webpage for the students:
```bash
streamlit run student_app.py
```
A webpage will instantly pop up in your browser! Feel free to fill it out and upload a sample PDF resume. 

### Step 6: Start the HR Dashboard
Leave that first terminal window open and running. Open a **brand new terminal window**. 
Navigate back to your project folder:
```bash
cd campus-ai-resume-parser
```
Now, turn on the recruiter's webpage:
```bash
streamlit run hr_app.py
```
A second webpage will open up! 

**To see the magic happen:**
1. Paste a Job Description into the box on the left.
2. Click the big **"Process Pending Applicants"** button.
3. The AI will read the resumes you submitted, score them, and build a ranked table! You can click on any candidate to see exactly *why* they got the score they did.