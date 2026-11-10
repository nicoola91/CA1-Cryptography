import sqlite3
import os

DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "users.db"
)


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection



def initialise_database():
    connection = get_db_connection()

    try:
        # Create users table
        connection.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                encrypted_master_key TEXT,
                key_salt TEXT,
                key_nonce TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create files table
        connection.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                filename TEXT NOT NULL,
                storage_name TEXT NOT NULL,
                nonce TEXT NOT NULL,
                salt TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Check users columns
        user_columns = {
            column["name"]
            for column in connection.execute(
                "PRAGMA table_info(users)"
            ).fetchall()
        }

        for column in ["encrypted_master_key", "key_salt", "key_nonce"]:
            if column not in user_columns:
                connection.execute(
                    f"ALTER TABLE users ADD COLUMN {column} TEXT"
                )

        # Check files columns
        file_columns = {
            column["name"]
            for column in connection.execute(
                "PRAGMA table_info(files)"
            ).fetchall()
        }

        if "salt" not in file_columns:
            connection.execute(
                "ALTER TABLE files ADD COLUMN salt TEXT"
            )

        connection.commit()

    finally:
        connection.close()



def get_user_files(user_id):

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            "SELECT * FROM files WHERE user_id = ?",
            (user_id,)
        )

        files = cursor.fetchall()

        return files

    finally:
        connection.close()
