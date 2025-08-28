import  mysql.connector

def get_db_connection():
    return  mysql.connector.connect(
        host="localhost",
        user="root",        # your MySQL username
        password="ss34892@@##", # your MySQL password
        database="todo_app"      # your DB name
    )

