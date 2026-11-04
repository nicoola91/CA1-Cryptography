import sqlite3

DATABASE = "users.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def initialise_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            filename TEXT NOT NULL,
            storage_name TEXT NOT NULL,
            nonce TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def get_user_files(user_id):
    connection = get_db_connection()

    files = connection.execute(
        "SELECT * FROM files WHERE user_id = ?",
        (user_id,)
    ).fetchall()

    connection.close()
    return files


def get_user_file(file_id, user_id):
    connection = get_db_connection()

    file = connection.execute(
        "SELECT * FROM files WHERE id = ? AND user_id = ?",
        (file_id, user_id)
    ).fetchone()

    connection.close()
    return file