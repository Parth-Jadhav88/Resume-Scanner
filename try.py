from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

print("DEBUG: Loaded DB config -", os.getenv("DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_NAME"))

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
print("✅ Connected successfully")





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