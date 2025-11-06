import mysql.connector
# Configure the MySQL database connection
def get_db():
    return mysql.connector.connect(
        host="localhost",               # Update with your MySQL host
        user="root",      # Your MySQL username
        password="password",  # Your MySQL password
        database="human_interactions",    # Your database name
        auth_plugin= "mysql_native_password"
    )