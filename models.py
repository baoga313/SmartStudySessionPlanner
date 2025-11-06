from db import get_db

def get_user(email, password):
    db = get_db()
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user