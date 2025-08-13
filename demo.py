print("App is starting...")
from flask import Flask, render_template, request, session, redirect
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import request, redirect, flash, url_for
from db import get_db_connection



from flask_mail import Mail, Message



sys.path.append(os.path.abspath(os.path.dirname(__file__)))
app = Flask(__name__)

# --- Load environment variables and email credentials before using them in app.config ---
from dotenv import load_dotenv
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = EMAIL_USER
app.config['MAIL_PASSWORD'] = EMAIL_PASS
app.config['MAIL_DEFAULT_SENDER'] = EMAIL_USER

mail = Mail(app)

app.secret_key = 'supersecret'

from db import get_db_connection

connection = get_db_connection()




# ------------------ Routes ------------------

@app.route('/')
def index():
    return render_template('1option_page.html')


@app.route('/view-all-resumes')
def view_all_resumes():
    from db import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM resumes ORDER BY id DESC")
    resumes = cursor.fetchall()
    conn.close()

    return render_template('view_resumes.html', resumes=resumes)





#.    6 aug -----------------
from flask import Flask, render_template, request, session, redirect, flash
from werkzeug.security import check_password_hash
from db import get_db_connection
@app.route('/recruiter-login', methods=['GET', 'POST'])
def recruiter_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM recruiter_register WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
               session['recruiter_id'] = user[0]
               session['email'] = user[1]  # assuming email is in column index 1 
               session['role'] = 'recruiter'
        return redirect('/recruiter-dashboard')
    else:
            return render_template('recruiter_login.html', show_result=True, success=False, error="Invalid credentials")
    
    return render_template('recruiter_login.html')


@app.route('/recruiter-dashboard')  # use dash for consistency
def recruiter_dashboard():
    if 'email' in session and session.get('role') == 'recruiter':
        return render_template('hr_dashboard.html')
    else:
        return redirect('/recruiter-login')
    

#--------------- sending email route ------
@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        to_email = request.form['to_email']
        subject = request.form['subject']
        message = request.form['message']

        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        flash('✅ Email sent successfully!', 'success')

    except Exception as e:
        print("❌ Error sending email:", e)
        flash('❌ Failed to send email. Please try again.', 'danger')

    return redirect(url_for('view_all_resumes'))  # redirect to your dashboard page



#--------------------------mail confirmation ----------------------------------------------------------

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


load_dotenv()

def send_registration_email(receiver_email, receiver_name):
    sender_email = os.getenv('EMAIL_USER')
    sender_password = os.getenv('EMAIL_PASS')

    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to ResumeScan!"
    message["From"] = sender_email
    message["To"] = receiver_email

    html = f"""
    <html>
        <body>
            <h2>Welcome, {receiver_name}!</h2>
            <p>Thank you for registering on ResumeScan. You can now log in and upload your resume.</p>
        </body>
    </html>
    """

    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Registration email sent successfully.")
    except Exception as e:
        print("Error sending email:", e)
# ------------------ Resume Matching Route ------------------

# @app.route('/match-resumes', methods=['POST'])
# def match_resumes():
#     if session.get('role') != 'recruiter':
#         return redirect('/')

#     required_input = request.form['required_skills']
#     required_skills = [skill.strip().lower() for skill in required_input.split(',')]

#     from extractor import extract_skills, extract_text_from_pdf
#     text = extract_text_from_pdf("uploads/sample_resume.pdf")  # ⚠️ Replace this with dynamic path later
#     extracted_skills = extract_skills(text)

#     matched = list(set(required_skills).intersection(set(extracted_skills)))
#     percentage = (len(matched) / len(required_skills)) * 100 if required_skills else 0

#     return render_template("match_result.html",
#                            matched=matched,
#                            score=round(percentage, 2),
#                            extracted_skills=extracted_skills,
#                            required=required_skills)




@app.route('/match-resumes', methods=['POST'])
def match_resumes():
    if session.get('role') != 'recruiter':
        return redirect('/')

    job_description = request.form['required_skills']
    from db import get_db_connection
    from utils.embedding_matcher import get_embedding, get_similarity_score

    jd_embedding = get_embedding(job_description)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM resumes")
    resumes = cursor.fetchall()
    conn.close()

    results = []
    for resume in resumes:
        resume_embedding = get_embedding(resume["extracted_text"])
        similarity = get_similarity_score(jd_embedding, resume_embedding)
        results.append({
            "name": resume["name"],
            "email": resume["email"],
            "score": round(similarity * 100, 2)
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    print("Match Results:", results)  # ✅ Confirm in terminal

    return render_template("match_result.html", results=results, jd=job_description)
# ------------------ HR Dashboard ------------------

# @app.route('/hr-dashboard')
# def hr_dashboard():
#     if session.get('role') != 'recruiter':
#         return redirect('/')
#     return render_template('hr_dashboard.html')






#----- todayy   6 aug 






# @app.route('/hr-dashboard')
# def hr_dashboard():
#     if session.get('role') != 'recruiter':
#         return redirect('/')

#     from db import get_db_connection
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM resumes ORDER BY id DESC")
#     resumes = cursor.fetchall()
#     conn.close()

#     return render_template('hr_dashboard.html', resumes=resumes)

# ------------------ Candidate Login ------------------

# @app.route('/candidate-login', methods=['GET', 'POST'])
# def candidate_login():
#     error = None
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         if email in CANDIDATE_CREDENTIALS and CANDIDATE_CREDENTIALS[email] == password:
#             session['role'] = 'candidate'
#             session['email'] = email
#             return redirect('/upload-resume')
#         else:
#             error = "Invalid candidate credentials"
#     return render_template('candidate_login.html', error=error)




@app.route('/candidate-login', methods=['GET', 'POST'])
def candidate_login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM candidates WHERE email = %s AND password = %s", (email, password))
        candidate = cursor.fetchone()
        conn.close()

        if candidate:
            session['role'] = 'candidate'
            session['email'] = candidate['email']
            session['name'] = candidate['name']
            return redirect('/upload-resume')  # or candidate dashboard
        else:
            error = "Invalid candidate credentials"
    
    return render_template('candidate_login.html', error=error)

# ------------------ Candidate Dashboard ------------------

# @app.route('/upload-resume')
# def candidate_dashboard():
#     if session.get('role') != 'candidate':
#         return redirect('/')
#     return f"Welcome Candidate {session.get('email')}! You are logged in."

@app.route('/upload-resume', methods=['GET', 'POST'])
def candidate_dashboard():
    if session.get('role') != 'candidate':
        return redirect('/')

    if request.method == 'POST':
        from extraction import submit  # 🔄 This will do parsing + DB insert
        submit()  # You already created this
        return render_template('uploads.html', message="Resume uploaded successfully!")

    return render_template('uploads.html')  # Upload form page
#----------------------------- candidate register-----------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO candidates (name, email, password) VALUES (%s, %s, %s)", 
                       (name, email, password))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/candidate-login')
    
    return render_template('candidate_register.html')
#-----------------------------------candidate login - -- direct connection to db 

# ------------------ Logout ------------------

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect('/')

# ------------------ Run ------------------

if __name__ == "__main__":
    app.run(debug=True)





#------------------------------------  REVISED ---- BELOW 👇🏻__________________

# from flask import render_template, request, session, redirect
# from flask import Flask
# app = Flask(__name__)
# app.secret_key = 'supersecret'

# # Dummy credentials
# RECRUITER_CREDENTIALS = {
#     "ParthJadhav@gmail.com": "hr1122"
# }
# CANDIDATE_CREDENTIALS = {
#     "stud@gmail.com": "pa123"
# }

# @app.route('/')
# def index():
#     return render_template('1option_page.html')

# @app.route('/recruiter-login', methods=['GET', 'POST'])
# def recruiter_login():
#     error = None
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         if email in RECRUITER_CREDENTIALS and RECRUITER_CREDENTIALS[email] == password:
#             session['role'] = 'recruiter'
#             session['email'] = email
#             return redirect('/hr-dashboard')
#         else:
#             error = "Invalid recruiter credentials"
#     return render_template('recruiter_login.html', error=error)

# #----------------------------------- 10th july -------
# @app.route('/match-resumes', methods=['POST'])
# def match_resumes():
#     if session.get('role') != 'recruiter':
#         return redirect('/')

#     required_input = request.form['required_skills']
#     required_skills = [skill.strip().lower() for skill in required_input.split(',')]

#     # Simulate extracted skills from latest uploaded resume (link actual logic later)
#     from extractor import extract_skills, extract_text_from_pdf
#     text = extract_text_from_pdf("uploads/sample_resume.pdf")  # TEMP HARDCODED
#     extracted_skills = extract_skills(text)

#     matched = list(set(required_skills).intersection(set(extracted_skills)))
#     percentage = (len(matched) / len(required_skills)) * 100 if required_skills else 0

#     return render_template("match_result.html", matched=matched, score=round(percentage, 2), extracted_skills=extracted_skills, required=required_skills)



# @app.route('/hr-dashboard')
# def hr_dashboard():
#     if session.get('role') != 'recruiter':
#         return redirect('/')
#     return render_template('hr_dashboard.html')
# #-------------

# @app.route('/candidate-login', methods=['GET', 'POST'])
# def candidate_login():
#     error = None
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         if email in CANDIDATE_CREDENTIALS and CANDIDATE_CREDENTIALS[email] == password:
#             session['role'] = 'candidate'
#             session['email'] = email
#             return redirect('/upload-resume')  # candidate dashboard
#         else:
#             error = "Invalid candidate credentials"
#     return render_template('candidate_login.html', error=error)

# @app.route('/hr-dashboard')
# def hr_dashboard():
#     if session.get('role') != 'recruiter':
#         return redirect('/')
#     return f"Welcome HR {session.get('email')}! You are logged in."

# @app.route('/upload-resume')
# def candidate_dashboard():
#     if session.get('role') != 'candidate':
#         return redirect('/')
#     return f"Welcome Candidate {session.get('email')}! You are logged in."

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect('/')

# if __name__ == "__main__":
#     app.run(debug=True)