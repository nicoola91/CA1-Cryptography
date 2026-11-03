import sqlite3

DATABASE="users.db"

def get_db_connection():
    connection=sqlite3.connect(DATABASE)
    connection.row_factory=sqlite3.Row
    return connection

def initialise_database():
    connection=get_db_connection()

    connection.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    connection.close()
