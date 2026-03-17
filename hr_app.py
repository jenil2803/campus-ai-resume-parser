import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re

from db import get_db_collection

# --- Configuration & Setup ---
st.set_page_config(page_title="HR Dashboard", page_icon="🏢", layout="wide")

# Predefined key skills to look for
KEY_SKILLS = ["Python", "C++", "Java", "Data Structures", "Machine Learning", 
              "MongoDB", "Next.js", "React", "SQL", "Deep Learning", "NLP"]

@st.cache_resource
def load_model():
    """Load the sentence transformer model and cache it."""
    return SentenceTransformer('all-MiniLM-L6-v2')

def extract_key_skills(text):
    """Scan text for core technical skills and return a list."""
    found_skills = []
    
    # PDF extraction sometimes puts spaces/newlines everywhere
    # So we normalize the text to a single continuous string of words separated by single spaces
    text_normalized = " ".join(text.split()).lower()
    
    for skill in KEY_SKILLS:
        skill_lower = skill.lower()
        
        # Exact string containment check since we normalized spaces
        if skill_lower == "c++":
            if "c++" in text_normalized:
                found_skills.append(skill)
        else:
            # We use a regex boundary check but on the normalized text
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_normalized):
                found_skills.append(skill)
                
    return found_skills

def calculate_similarity(model, text1, text2):
    """Calculate cosine similarity between two texts using the model."""
    if not text1.strip() or not text2.strip():
        return 0.0

    embeddings = model.encode([text1, text2])
    sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(sim)

def process_pending_applicants(jd_text, min_cgpa):
    """Process all pending applicants against the JD and criteria."""
    collection = get_db_collection()
    if collection is None:
        st.error("Database connection failed.")
        return
        
    pending_docs = list(collection.find({"status": "Pending"}))
    
    if not pending_docs:
        st.warning("No pending applicants to process.")
        return
        
    model = load_model()
    processed_count = 0
    
    # Process each applicant
    progress_bar = st.progress(0)
    for i, doc in enumerate(pending_docs):
        # 1. Hard Filter on CGPA
        if doc.get("cgpa", 0) < min_cgpa:
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"status": "Rejected - CGPA"}}
            )
            continue
            
        # 2. Extract Key Skills
        skills = extract_key_skills(doc.get("resume_text", ""))
        
        # 3. AI Semantic Mapping
        resume_text = doc.get("resume_text", "")
        projects_text = doc.get("projects_text", "")
        
        base_sim = calculate_similarity(model, jd_text, resume_text)
        
        if projects_text:
            proj_sim = calculate_similarity(model, jd_text, projects_text)
        else:
            proj_sim = 0.0
            
        # Convert to percentage
        base_score_pct = max(0.0, base_sim) * 100
        proj_score_pct = max(0.0, proj_sim) * 100
        
        final_score = (base_score_pct * 0.6) + (proj_score_pct * 0.4)
        
        # 4. Update MongoDB
        collection.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "status": "Processed",
                    "final_score": round(final_score, 2),
                    "base_score": round(base_score_pct, 2),
                    "project_score": round(proj_score_pct, 2),
                    "key_skills_found": skills,
                    # Initialize interview scheduled flag if not present
                    "interview_scheduled": doc.get("interview_scheduled", False)
                }
            }
        )
        processed_count += 1
        progress_bar.progress((i + 1) / len(pending_docs))
        
    st.success(f"Successfully processed {processed_count} applicants.")

def reset_database():
    """Utility to clear the collection for testing."""
    collection = get_db_collection()
    if collection is not None:
        collection.delete_many({})
        st.sidebar.success("Database Reset!")

def main():
    st.title("HR Dashboard - Candidate Evaluation")
    
    # --- Sidebar ---
    st.sidebar.header("Job Configuration")
    jd_text = st.sidebar.text_area("Job Description (JD)", height=300, 
                                   placeholder="Enter the job description and requirements here...")
    min_cgpa = st.sidebar.number_input("Minimum CGPA Cut-off", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    
    if st.sidebar.button("Process Pending Applicants", type="primary"):
        if not jd_text.strip():
            st.sidebar.error("Please enter a Job Description.")
        else:
            with st.spinner("Processing applicants using AI..."):
                process_pending_applicants(jd_text, min_cgpa)
                
    # Hidden utility button
    st.sidebar.markdown("---")
    with st.sidebar.expander("Admin Utilities"):
        if st.button("Reset Database"):
            reset_database()
            
    # --- Main View ---
    collection = get_db_collection()
    if collection is None:
        st.error("Database connection failed.")
        return
        
    processed_docs = list(collection.find({"status": "Processed"}).sort("final_score", -1))
    
    if not processed_docs:
        st.info("No processed candidates to display. Adjust your criteria and process pending applications.")
        return
        
    st.subheader(f"Processed Candidates ({len(processed_docs)})")
    
    # Overview Table
    df = pd.DataFrame(processed_docs)
    
    # Fill missing interview_scheduled with False for older records
    if "interview_scheduled" not in df.columns:
        df["interview_scheduled"] = False
    else:
        df["interview_scheduled"] = df["interview_scheduled"].fillna(False)
        
    # Select columns to display
    display_df = df[["name", "roll_no", "cgpa", "final_score", "key_skills_found", "interview_scheduled"]].copy()
    display_df["key_skills_found"] = display_df["key_skills_found"].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    display_df.columns = ["Name", "Roll No", "CGPA", "Final Score (%)", "Matched Skills", "Interview Scheduled"]
    
    # Style the dataframe to highlight scheduled interviews in green
    def highlight_scheduled(row):
        if row["Interview Scheduled"]:
            return ['background-color: rgba(36, 209, 94, 0.2)'] * len(row)
        return [''] * len(row)
        
    styled_df = display_df.style.apply(highlight_scheduled, axis=1)
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("Deep Dive Justification")
    
    # Deep Dive Expanders
    for doc in processed_docs:
        name = doc.get("name", "Unknown")
        roll = doc.get("roll_no", "N/A")
        score = doc.get("final_score", 0.0)
        base_score = doc.get("base_score", 0.0)
        proj_score = doc.get("project_score", 0.0)
        
        with st.expander(f"{name} ({roll}) - Final Score: {score}%"):
            st.markdown("### 📊 Score Breakdown")
            
            # Use columns to lay out the math cleanly
            st.markdown(f"**Final Score ({score}%)** = (Base Match × 60%) + (Project Match × 40%)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Base Match Score:** {base_score}%\n\n*Semantic similarity between the overall Resume text and the Job Description.*")
                st.info(f"**Project Match Score:** {proj_score}%\n\n*Semantic similarity strictly between the extracted Projects section and the Job Description.*")
                st.metric("Extracted CGPA", f"{doc.get('cgpa', 'N/A')}")
                
            with col2:
                st.markdown("### 🛠️ Key Skills Identified")
                skills = doc.get("key_skills_found", [])
                if skills:
                    # Format as markdown tags
                    tags = " ".join([f"`{s}`" for s in skills])
                    st.markdown(tags)
                else:
                    st.write("None identified from core list.")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                if not doc.get("projects_text"):
                    st.warning("⚠️ **No Projects Section Found**: The app could not distinctively find a 'Projects' section in this resume. Only Base Match is contributing to the score.", icon="⚠️")
            
            # Action Buttons
            b_col1, b_col2, _ = st.columns([1, 1, 3])
            
            # Show if already scheduled
            is_scheduled = doc.get("interview_scheduled", False)
            
            with b_col1:
                if is_scheduled:
                    st.success("✅ Interview Scheduled")
                else:
                    if st.button("Schedule Interview", key=f"int_{doc['_id']}", type="primary"):
                        collection.update_one({"_id": doc["_id"]}, {"$set": {"interview_scheduled": True}})
                        st.success(f"Interview scheduled for {name}! Please refresh the page.")
                        
            with b_col2:
                if st.button("Reject (False Positive)", key=f"rej_{doc['_id']}"):
                    collection.update_one({"_id": doc["_id"]}, {"$set": {"status": "Rejected - False Positive"}})
                    st.error(f"{name} rejected. Flagged as false positive. Please refresh the page.")

if __name__ == "__main__":
    main()
