from db import get_db
from datetime import date

def get_user(email, password):
    db = get_db()
    query = "SELECT * FROM users WHERE email = %s AND user_password = %s"
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user

def get_tasks_for_today(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT 
            t.id, 
            t.subject, 
            t.description, 
            t.task_date, 
            c.course_name,
            c.difficulty_level,
            CASE 
                WHEN c.difficulty_level = 'Hard' THEN 90
                WHEN c.difficulty_level = 'Medium' THEN 60
                WHEN c.difficulty_level = 'Easy' THEN 45
                ELSE 60
            END AS study_duration
        FROM tasks t
        LEFT JOIN courses c ON t.course_id = c.id
        WHERE t.user_id = %s
        AND t.task_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 2 DAY)
        ORDER BY t.task_date ASC
    """
    cursor.execute(query, (user_id,))
    tasks = cursor.fetchall()
    cursor.close()
    db.close()
    return tasks

def get_task_by_id(task_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT t.*, c.course_name, c.difficulty_level
        FROM tasks t
        LEFT JOIN courses c ON t.course_id = c.id
        WHERE t.id = %s
    """
    cursor.execute(query, (task_id,))
    task = cursor.fetchone()
    cursor.close()
    db.close()
    return task

def get_tasks(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT id, subject AS task_name, task_date AS due_date, description AS course_name
        FROM tasks
        WHERE user_id = %s
        ORDER BY task_date ASC
    """
    cursor.execute(query, (user_id,))
    tasks = cursor.fetchall()
    cursor.close()
    db.close()
    return tasks

def get_courses():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, course_name FROM courses")
    courses = cursor.fetchall()
    cursor.close()
    db.close()
    return courses


def add_task(user_id, task_name, course_id, description, due_date):
    db = get_db()
    cursor = db.cursor()
    query = """
        INSERT INTO tasks (user_id, subject, course_id, description, task_date)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (user_id, task_name, course_id, description, due_date))
    db.commit()
    cursor.close()
    db.close()

def get_courses():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, course_name, difficulty_level FROM courses")
    courses = cursor.fetchall()
    cursor.close()
    db.close()
    return courses


def add_course(course_name, difficulty_level):
    db = get_db()
    cursor = db.cursor()
    query = "INSERT INTO courses (course_name, difficulty_level) VALUES (%s, %s)"
    cursor.execute(query, (course_name, difficulty_level))
    db.commit()
    cursor.close()
    db.close()
