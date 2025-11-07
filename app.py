from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import get_user, get_tasks_for_today, get_task_by_id, get_courses, get_tasks, add_task, add_course
from db import get_db
from datetime import date
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'human-interactions-class'

#Login page
@app.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user(email, password)

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            # Check if the email exist, wrong password
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            cursor.close()
            db.close()

            if existing_user:
                flash('Incorrect password. Please try again.', 'error')
            else:
                flash('No account found for this email. Please sign up first.')
    return  render_template('login.html')

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        best_time = request.form['best_time']

        db = get_db()
        cursor = db.cursor()
        try:
            query = "INSERT INTO users (email, user_password) VALUES (%s, %s)"
            cursor.execute(query, (email, password))
            db.commit()
        except Exception as e:
            db.rollback()
            flash('Email already exists or invalid input', 'error')
            cursor.close()
            db.close()
            return redirect(url_for('signup'))
        
        cursor.close()
        db.close()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Dashboard page
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    today_date = date.today().strftime("%B %d, %Y")
    user_id = session['user_id']
    tasks = get_tasks_for_today(user_id)

    return render_template('dashboard.html', today_date=today_date, tasks=tasks)

#Task timer page
@app.route('/task/<int:task_id>')
def task_timer(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = get_task_by_id(task_id)
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('task_timer.html', task=task)

#All tasks page
@app.route('/tasks')
def all_tasks():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    tasks = get_tasks(user_id)  # use the function from models.py
    return render_template('tasks.html', tasks=tasks)

# Add task page
@app.route('/tasks/add', methods=['GET'])
def add_task_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, course_name FROM courses WHERE user_id = %s", (user_id,))
    courses = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('add_task.html', courses=courses)

@app.route('/tasks/add', methods=['POST'])
def add_task_submit():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    task_name = request.form['task_name']
    course_id = request.form['course_id']
    description = request.form['description']
    due_date = request.form['due_date']

    add_task(user_id, task_name, course_id, description, due_date)
    flash('Task added successfully!', 'success')
    return redirect(url_for('all_tasks'))

# Setting page
@app.route("/settings")
def settings_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM courses WHERE user_id = %s ORDER BY course_name ASC", (user_id,))
    courses = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("settings.html", courses=courses)

# Add course page
@app.route("/add_course", methods=["GET", "POST"])
def add_course_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        course_name = request.form["course_name"]
        difficulty = request.form["difficulty_level"]
        user_id = session['user_id']

        db = get_db()
        cursor = db.cursor()
        query = "INSERT INTO courses (course_name, difficulty_level, user_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (course_name, difficulty, user_id))
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for("settings_page"))

    return render_template("add_course.html")

# End session
@app.route('/end_session/<int:task_id>', methods=['POST'])
def end_session(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT course_id, study_duration FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    if not task:
        return jsonify({'status': 'error', 'message': 'Task not found'})

    # Update or insert into progress
    cursor.execute("""
        INSERT INTO progress (user_id, course_id, total_minutes)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE total_minutes = total_minutes + VALUES(total_minutes)
    """, (user_id, task['course_id'], task['study_duration']))

    db.commit()
    cursor.close()
    db.close()

    return jsonify({'status': 'success'})

# Progress page
@app.route('/progress')
def progress_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT p.total_minutes, c.course_name
        FROM progress p
        JOIN courses c ON p.course_id = c.id
        WHERE p.user_id = %s
    """
    cursor.execute(query, (user_id,))
    progress = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('progress.html', progress=progress)


if __name__ == '__main__':
    app.run(debug=True) 