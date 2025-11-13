import mysql.connector
# Configure the MySQL database connection
def get_db():
    return mysql.connector.connect(
        host="localhost",               # Update with your MySQL host
        user="root",      # Your MySQL username
        password="BaolearnSQL",  # Your MySQL password
        database="study_planner",    # Your database name
    )