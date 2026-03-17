# AI Resume Parser for Campus Drives

A fully functional, end-to-end Proof of Concept (PoC) for mapping student resumes to given Job Descriptions using an AI Semantic Matcher (all-MiniLM-L6-v2) and Regex skill extraction. Built with Python and Streamlit processing data securely via a MongoDB Atlas backend.

## Architecture Structure
This repository contains two distinct front-end portals that read and write from a single shared MongoDB database:

1. **Student Portal** (`student_app.py`): Students input their information and upload a PDF resume. The app automatically extracts text, finds the CGPA, and isolates the "Projects" section using NLP heuristics.
2. **HR Dashboard** (`hr_app.py`): Recruiters provide a Job Description (JD) and a CGPA cut-off. The app automatically scans all pending applicant resumes for key technical skills and uses Cosine Similarity against the JD to calculate a "Base Match Score" and a specific "Project Match Score", generating a ranked leaderboard of the best candidates. 

---

## 🚀 How to Run Locally on Your PC

If you are cloning this project to run on your own machine, follow these exact steps:

### Prerequisites
* **Python 3.8+** installed on your system.
* **MongoDB Server:** This project is already connected to a cloud-hosted MongoDB Atlas cluster, meaning you do not need to set up your own database. Just use the provided connection string in Step 3! 

### 1. Clone the repository
Open your terminal (or Command Prompt) and run:
```bash
git clone https://github.com/jenil2803/campus-ai-resume-parser.git
cd campus-ai-resume-parser
```

### 2. Install Dependencies
Install all required Python packages (Streamlit, PyMongo, PyPDF2, sentence-transformers, Pandas, Scikit-learn):
```bash
pip install -r requirements.txt
```
*(Note: If you are on a Mac, you may need to use `pip3` instead of `pip`).*

### 3. Configure the Environment Variables
You need to connect the applications to your MongoDB database. 
1. In the root folder (`campus-ai-resume-parser`), create a new file named exactly: `.env`
2. Open the `.env` file in any text editor and paste this exact MongoDB connection string:
```txt
MONGO_URI=mongodb+srv://jenil28:jenil123@cluster0.g6ponuy.mongodb.net/?appName=Cluster0
```

### 4. Run the Student Portal
Open a terminal inside the project folder and run the Student application:
```bash
streamlit run student_app.py
```
This will open `http://localhost:8501` in your browser. Feel free to submit a few sample PDF resumes here!

### 5. Run the HR Dashboard
Open a **new, separate terminal window** (keep the Student portal running in the first one), navigate to the project folder, and run:
```bash
streamlit run hr_app.py
```
This will open `http://localhost:8502` in your browser. 
1. Paste a Job Description.
2. Set a minimum CGPA.
3. Click **"Process Pending Applicants"** to execute the AI matching pipeline!

---

## 🛠 Features Included
* **SSL Bypass:** The database configuration currently ignores SSL certificate errors (`tlsAllowInvalidCertificates=True`), making this completely safe to test locally across Windows, Mac, or Linux without configuring system certificates. 
* **Duplicate Prevention:** The student portal prevents the same Roll Number from applying twice.
* **Explainability:** The HR dashboard visually explains the score breakdown (60% Base / 40% Project) and highlights matched Key Skills.
* **Interactive Data:** Recruiters can actively "Schedule Interviews" within the HR portal, turning candidate rows green, or reject candidates.
* **Hidden Reset Utility:** Inside the HR dashboard sidebar, an "Admin Utilities" expander allows you to instantly clear the database for fresh testing.