import sqlite3

DATABASE = "users.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def initialise_database():

    connection = get_db_connection()

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

    # Check existing users columns
    user_columns = connection.execute(
        "PRAGMA table_info(users)"
    ).fetchall()

    user_column_names = [
        column["name"] for column in user_columns
    ]

    # Add encryption columns if they do not exist
    if "encrypted_master_key" not in user_column_names:
        connection.execute(
            "ALTER TABLE users ADD COLUMN encrypted_master_key TEXT"
        )

    if "key_salt" not in user_column_names:
        connection.execute(
            "ALTER TABLE users ADD COLUMN key_salt TEXT"
        )

    if "key_nonce" not in user_column_names:
        connection.execute(
            "ALTER TABLE users ADD COLUMN key_nonce TEXT"
        )

    # Check existing files columns
    file_columns = connection.execute(
        "PRAGMA table_info(files)"
    ).fetchall()

    file_column_names = [
        column["name"] for column in file_columns
    ]

    # Add salt column if it does not exist
    if "salt" not in file_column_names:
        connection.execute(
            "ALTER TABLE files ADD COLUMN salt TEXT"
        )

    connection.commit()
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
