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
            DATEDIFF(t.task_date, CURDATE()) as days_until_due,
            CASE 
                WHEN c.difficulty_level = 'Hard' THEN 90
                WHEN c.difficulty_level = 'Medium' THEN 60
                WHEN c.difficulty_level = 'Easy' THEN 45
                ELSE 60
            END AS study_duration,
            -- Priority score for intelligent ordering
            (CASE 
                WHEN DATEDIFF(t.task_date, CURDATE()) = 0 THEN 100  -- Due today
                WHEN DATEDIFF(t.task_date, CURDATE()) = 1 THEN 80   -- Due tomorrow  
                WHEN DATEDIFF(t.task_date, CURDATE()) <= 3 THEN 60  -- Due in 2-3 days
                WHEN DATEDIFF(t.task_date, CURDATE()) <= 7 THEN 40  -- Due this week
                ELSE 20  -- Due later
            END +
            CASE 
                WHEN c.difficulty_level = 'Hard' THEN 30
                WHEN c.difficulty_level = 'Medium' THEN 20
                WHEN c.difficulty_level = 'Easy' THEN 10
                ELSE 15
            END) as priority_score
        FROM tasks t
        LEFT JOIN courses c ON t.course_id = c.id
        WHERE t.user_id = %s
        AND t.task_date >= CURDATE()
        AND t.task_date <= DATE_ADD(CURDATE(), INTERVAL 14 DAY)  -- Next 2 weeks
        ORDER BY priority_score DESC, t.task_date ASC
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
        SELECT t.id, t.subject AS task_name, t.task_date AS due_date,  c.course_name as course_name
        FROM tasks t
        LEFT JOIN courses c ON t.course_id = c.id
        WHERE t.user_id = %s
        ORDER BY task_date ASC
    """
    cursor.execute(query, (user_id,))
    tasks = cursor.fetchall()
    cursor.close()
    db.close()
    return tasks

def delete_task(task_id):
    db = get_db()
    cursor = db.cursor()
    query = "DELETE FROM tasks WHERE id = %s"
    cursor.execute(query, (task_id, ))   
    db.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    db.close()
    return rows_affected > 0

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

def delete_course(course_id):
    db = get_db()
    cursor = db.cursor()
    query = "DELETE FROM course WHERE id = %s"
    cursor.execute(query, (course_id, ))
    db.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    db.close()
    return rows_affected > 0