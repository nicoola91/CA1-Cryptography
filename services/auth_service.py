import sqlite3

from database import get_db_connection
from crypto.passwords import hash_password, verify_password


def register_user(
    username,
    email,
    password,
    encrypted_master_key,
    key_salt,
    key_nonce
):

    username = username.strip()
    email = email.strip().lower()

    # Hash the login password
    password_hash = hash_password(password)

    connection = get_db_connection()

    try:

        connection.execute(
            """
            INSERT INTO users (
                username,
                email,
                password_hash,
                encrypted_master_key,
                key_salt,
                key_nonce
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                email,
                password_hash,
                encrypted_master_key,
                key_salt,
                key_nonce
            )
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def authenticate_user(email, password):

    email = email.strip().lower()

    connection = get_db_connection()

    try:

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        # Check the login password
        if user and verify_password(
            password,
            user["password_hash"]
        ):

            return user

        return None

    finally:

        connection.close()
