import mysql.connector
# Configure the MySQL database connection
def get_db():
    return mysql.connector.connect(
        host="localhost",               # Update with your MySQL host
        user="root",      # Your MySQL username
        password="maghariou",  # Your MySQL password
        database="project_management"    # Your database name
    )