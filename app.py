from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import re

app = Flask(__name__)


# =====================================
# SKILLS DATABASE
# =====================================

SKILLS = [
    "python", "java", "javascript", "typescript",
    "html", "css", "bootstrap",
    "flask", "django", "fastapi",
    "sql", "mysql", "postgresql", "mongodb",
    "machine learning", "deep learning",
    "data analysis", "data science",
    "pandas", "numpy", "excel",
    "power bi", "tableau",
    "react", "angular", "node.js", "nodejs",
    "c++", "c programming",
    "git", "github",
    "api", "rest api",
    "tensorflow", "scikit-learn",
    "aws", "azure", "docker",
    "linux"
]


# =====================================
# FIND SKILLS
# =====================================

def find_skills(text):

    text = text.lower()
    found_skills = []

    for skill in SKILLS:

        pattern = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills


# =====================================
# RESUME STRENGTH ANALYSIS
# =====================================

def analyze_resume_strength(resume_text):

    checks = []

    text_lower = resume_text.lower()

    # Email Check
    email_found = bool(
        re.search(
            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
            resume_text
        )
    )

    checks.append({
        "name": "Email Address",
        "status": email_found
    })

    # Phone Number Check
    phone_found = bool(
        re.search(
            r'(\+?\d{1,3}[-.\s]?)?\d{10}',
            resume_text
        )
    )

    checks.append({
        "name": "Phone Number",
        "status": phone_found
    })

    # LinkedIn Check
    linkedin_found = "linkedin.com" in text_lower

    checks.append({
        "name": "LinkedIn Profile",
        "status": linkedin_found
    })

    # GitHub Check
    github_found = "github.com" in text_lower

    checks.append({
        "name": "GitHub Profile",
        "status": github_found
    })

    # Projects Check
    projects_found = (
        "project" in text_lower or
        "projects" in text_lower
    )

    checks.append({
        "name": "Projects Section",
        "status": projects_found
    })

    # Education Check
    education_found = (
        "education" in text_lower or
        "university" in text_lower or
        "college" in text_lower or
        "bachelor" in text_lower
    )

    checks.append({
        "name": "Education Section",
        "status": education_found
    })

    # Experience Check
    experience_found = (
        "experience" in text_lower or
        "internship" in text_lower or
        "intern" in text_lower
    )

    checks.append({
        "name": "Experience Section",
        "status": experience_found
    })

    # Calculate Strength Score
    completed_checks = sum(
        1 for check in checks if check["status"]
    )

    strength_score = int(
        (completed_checks / len(checks)) * 100
    )

    return strength_score, checks


# =====================================
# HOME PAGE
# =====================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================
# ANALYZE RESUME
# =====================================

@app.route("/analyze", methods=["POST"])
def analyze():

    resume = request.files.get("resume")
    job_description = request.form.get(
        "job_description",
        ""
    )

    # File Validation
    if not resume or resume.filename == "":
        return "Please upload a PDF resume."

    if not resume.filename.lower().endswith(".pdf"):
        return "Please upload only a PDF file."

    try:

        # =====================================
        # READ PDF
        # =====================================

        reader = PdfReader(resume)

        resume_text = ""

        for page in reader.pages:

            text = page.extract_text()

            if text:
                resume_text += text + "\n"


        if not resume_text.strip():
            return "This PDF does not contain readable text."


        # =====================================
        # SKILL EXTRACTION
        # =====================================

        resume_skills = find_skills(resume_text)

        required_skills = find_skills(
            job_description
        )


        # =====================================
        # MATCHING SKILLS
        # =====================================

        matching_skills = []

        for skill in required_skills:

            if skill in resume_skills:

                matching_skills.append(skill)


        # =====================================
        # MISSING SKILLS
        # =====================================

        missing_skills = []

        for skill in required_skills:

            if skill not in resume_skills:

                missing_skills.append(skill)


        # =====================================
        # MATCH SCORE
        # =====================================

        if len(required_skills) > 0:

            score = int(
                (
                    len(matching_skills)
                    / len(required_skills)
                ) * 100
            )

        else:

            score = 0


        # =====================================
        # MATCH STATUS
        # =====================================

        if score >= 80:

            status = "Excellent Match"
            status_class = "excellent"

        elif score >= 50:

            status = "Good Match"
            status_class = "good"

        else:

            status = "Needs Improvement"
            status_class = "poor"


        # =====================================
        # RESUME STRENGTH
        # =====================================

        strength_score, checks = analyze_resume_strength(
            resume_text
        )


        # =====================================
        # RESUME LENGTH
        # =====================================

        word_count = len(
            resume_text.split()
        )

        if word_count < 200:
            resume_length = "Short"
        elif word_count <= 800:
            resume_length = "Good"
        else:
            resume_length = "Long"


        # =====================================
        # SMART SUGGESTIONS
        # =====================================

        suggestions = []

        if score >= 80:

            suggestions.append(
                "Excellent job! Your resume matches most of the skills required for this position."
            )

        elif score >= 50:

            suggestions.append(
                "Good match. Your resume has relevant skills, but you can improve alignment with the job description."
            )

        else:

            suggestions.append(
                "Your resume currently has a low match with the job requirements. Focus on relevant skills and projects."
            )


        if missing_skills:

            missing_text = ", ".join(
                missing_skills
            )

            suggestions.append(
                f"Consider adding these skills only if you genuinely have experience with them: {missing_text}."
            )


        if strength_score < 70:

            suggestions.append(
                "Your resume is missing some important sections or contact information. Complete the missing checks below."
            )


        if word_count < 200:

            suggestions.append(
                "Your resume appears short. Add more details about projects, achievements and technical experience."
            )

        elif word_count > 800:

            suggestions.append(
                "Your resume appears long. Try to keep the content concise and focus on the most relevant achievements."
            )

        else:

            suggestions.append(
                "Your resume length looks balanced."
            )


        suggestions.append(
            "Use action words and measurable achievements to make your experience more impactful."
        )


        # =====================================
        # SEND DATA TO RESULT PAGE
        # =====================================

        return render_template(
            "result.html",

            score=score,
            status=status,
            status_class=status_class,

            resume_skills=resume_skills,
            total_skills=len(resume_skills),

            matching_skills=matching_skills,
            missing_skills=missing_skills,

            strength_score=strength_score,
            checks=checks,

            word_count=word_count,
            resume_length=resume_length,

            suggestions=suggestions
        )


    except Exception as e:

        return f"Error reading PDF: {str(e)}"


# =====================================
# RUN APPLICATION
# =====================================

if __name__ == "__main__":
    app.run(debug=True)