
# Imports SQLite so the application can work with the database
import sqlite3

# Imports the function used to connect to the database
from database import get_db_connection

# Imports the functions used to hash and check passwords
from crypto.passwords import hash_password, verify_password


# Function used to register a new user
def register_user(
    username,
    email,
    password,
    encrypted_master_key,
    key_salt,
    key_nonce
):

    # Removes any unnecessary spaces from the username
    username = username.strip()

    # Removes spaces from the email and converts it to lowercase
    # This makes sure emails are stored in a consistent format
    email = email.strip().lower()


    # Hashes the user's password before storing it in the database
    # The original password is not stored as plain text
    password_hash = hash_password(password)


    # Opens a connection to the SQLite database
    connection = get_db_connection()


    # Starts error handling to make sure the database connection is closed
    # even if something goes wrong
    try:


        # Adds the new user's information to the users table
        connection.execute(

            # SQL command used to insert a new user
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

            # Values inserted into the database
            # The question marks above are replaced with these values
            (
                username,
                email,
                password_hash,
                encrypted_master_key,
                key_salt,
                key_nonce
            )
        )


        # Saves the changes made to the database
        connection.commit()


        # Returns True to show that registration was successful
        return True


    # Handles database errors, such as trying to register with an email
    # address that already exists
    except sqlite3.IntegrityError:


        # Returns False to show that registration was unsuccessful
        return False


    # Always closes the database connection when the function finishes
    finally:

        connection.close()



# Function used to check a user's login details
def authenticate_user(email, password):

    # Removes unnecessary spaces from the email and converts it to lowercase
    email = email.strip().lower()


    # Opens a connection to the SQLite database
    connection = get_db_connection()


    # Starts error handling to make sure the connection is closed
    try:


        # Searches the users table for an account with the entered email
        user = connection.execute(

            # SQL command that finds the matching email address
            "SELECT * FROM users WHERE email = ?",

            # Supplies the email address for the SQL question mark
            (email,)

        ).fetchone()

        # fetchone() returns the matching user if one exists
        # Otherwise, it returns None


        # Checks that the account exists and that the entered password is correct
        if user and verify_password(
            password,
            user["password_hash"]
        ):


            # Returns the user's database information if login is successful
            return user


        # Returns None if the account does not exist or the password is incorrect
        return None


    # Always closes the database connection when the function finishes
    finally:

        connection.close()
