import streamlit as st
import PyPDF2
import re
from db import get_db_collection

def extract_text_from_pdf(pdf_file):
    """Reads a PDF file and extracts text."""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def extract_cgpa(text):
    """Extracts CGPA from text using Regex."""
    # Common pattern: CGPA 9.5, CGPA: 9.5, etc.
    match = re.search(r'cgpa[\s:-]*([0-9]{1,2}\.[0-9]{1,2})', text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    # Common pattern: 8.5/10 or 8.5 / 10
    match = re.search(r'([0-9]{1,2}\.[0-9]{1,2})\s*/\s*10', text)
    if match:
        return float(match.group(1))
        
    return 0.0

def extract_projects_section(text):
    """Extracts the projects section from the resume text."""
    lines = text.split('\n')
    project_text = []
    in_project_section = False
    
    # Common headers that typically delineate sections
    stop_headers = [
        'SKILLS', 'TECHNICAL SKILLS', 'EDUCATION', 'EXPERIENCE', 
        'WORK EXPERIENCE', 'CERTIFICATIONS', 'ACHIEVEMENTS', 
        'EXTRA CURRICULAR', 'DECLARATION', 'INTERESTS', 'LANGUAGES',
        'PROFESSIONAL EXPERIENCE', 'REFERENCES'
    ]
                    
    for line in lines:
        cleaned_line = line.strip().upper()
        
        # Check if we are entering the projects section
        if not in_project_section:
            if cleaned_line in ['PROJECTS', 'ACADEMIC PROJECTS', 'PERSONAL PROJECTS']:
                in_project_section = True
                continue
            # Heuristic for variations like "PROJECTS / INTERNSHIPS"
            if 'PROJECTS' in cleaned_line and len(cleaned_line) < 30:
                in_project_section = True
                continue
        else:
            # We are inside the project section, check if we've hit a new section
            is_stop = False
            for header in stop_headers:
                if header == cleaned_line or (header in cleaned_line and len(cleaned_line) < 25):
                    is_stop = True
                    break
            
            if is_stop:
                break
                
            project_text.append(line)
            
    return "\n".join(project_text).strip()

def main():
    st.set_page_config(page_title="Student Portal", page_icon="🎓", layout="centered")
    st.title("Campus Placement - Student Application")
    st.markdown("Please fill out the form below and upload your resume to apply for the upcoming placement drive.")
    
    # Application Form
    with st.form("application_form"):
        name = st.text_input("Full Name")
        roll_no = st.text_input("Roll Number")
        pdf_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
        
        submitted = st.form_submit_button("Submit Application")
        
        if submitted:
            if not name.strip() or not roll_no.strip() or not pdf_file:
                st.error("Please fill all fields and upload a PDF resume.")
            else:
                with st.spinner("Processing application..."):
                    collection = get_db_collection()
                    if collection is None:
                        st.error("Database connection failed. Please ensure MongoDB is running.")
                    else:
                        # Check if roll number already exists
                        existing_doc = collection.find_one({"roll_no": roll_no.strip()})
                        if existing_doc:
                            st.warning(f"An application with Roll Number '{roll_no.strip()}' has already been submitted.")
                        else:
                            # 1. Parse PDF
                            resume_text = extract_text_from_pdf(pdf_file)
                            
                            if not resume_text:
                                st.error("Could not extract text from the PDF. Please try another file.")
                            else:
                                # 2. Extract Data via Regex/NLP heuristics
                                cgpa = extract_cgpa(resume_text)
                                projects_text = extract_projects_section(resume_text)
                                
                                # 3. Store document in MongoDB
                                doc = {
                                    "name": name.strip(),
                                    "roll_no": roll_no.strip(),
                                    "cgpa": cgpa,
                                    "resume_text": resume_text,
                                    "projects_text": projects_text,
                                    "status": "Pending",
                                    "final_score": 0.0,
                                    "base_score": 0.0,
                                    "project_score": 0.0,
                                    "key_skills_found": []
                                }
                                collection.insert_one(doc)
                                
                                st.success(f"Application submitted successfully for {name} ({roll_no})!")

if __name__ == "__main__":
    main()
