
# Imports os to work with files and folders
import os

# Imports uuid to generate unique names for encrypted files
import uuid

# Imports base64 to decode and check the encryption nonce
import base64

# Imports Path to create and manage file locations
from pathlib import Path


# Imports the Flask tools needed for uploading and downloading files
from flask import (
    Blueprint,       # Allows us to organise routes into a separate file
    request,         # Gets information sent from the browser
    session,         # Stores information about the logged-in user
    jsonify,         # Sends responses back to JavaScript in JSON format
    current_app,     # Gives access to the current Flask application
    send_file        # Allows Flask to send files to the browser
)


# Imports secure_filename to clean filenames and remove unsafe characters
from werkzeug.utils import secure_filename

# Imports the function used to connect to the SQLite database
from database import get_db_connection



# Creates a Blueprint to organise all file-related routes
file_routes = Blueprint("file_routes", __name__)




# Upload an encrypted file
# This route is called when the browser sends an encrypted file to Flask
@file_routes.route("/upload", methods=["POST"])
def upload_file():


    # Gets the ID of the currently logged-in user from the session
    user_id = session.get("user_id")


    # Checks whether the user is logged in
    if not user_id:

        # Sends an error message if the user is not logged in
        return jsonify({
            "error": "Please log in first."
        }), 401


    # Gets the encrypted file sent from the browser
    uploaded_file = request.files.get("encrypted_file")


    # Gets the encryption nonce sent with the file
    nonce = request.form.get("nonce")


    # Gets the original filename sent from the browser
    filename = request.form.get("filename")


    # Checks that the file, nonce and filename have all been provided
    if not uploaded_file or not nonce or not filename:

        # Returns an error if any required information is missing
        return jsonify({
            "error": "Missing file or encryption information."
        }), 400


    # Checks whether the uploaded file has an empty filename
    if uploaded_file.filename == "":

        # Returns an error if no file was selected
        return jsonify({
            "error": "No file selected."
        }), 400



    # Validate the encryption nonce
    try:

        # Converts the Base64 nonce back into bytes
        decoded_nonce = base64.b64decode(nonce, validate=True)


        # Checks that the nonce is exactly 12 bytes long
        # AES-GCM uses a 12-byte nonce in this project
        if len(decoded_nonce) != 12:

            # Returns an error if the nonce has the wrong length
            return jsonify({
                "error": "Invalid encryption nonce."
            }), 400


    # Handles errors if the nonce is not valid Base64 data
    except (ValueError, base64.binascii.Error):

        # Returns an error if the nonce cannot be decoded correctly
        return jsonify({
            "error": "Invalid encryption nonce."
        }), 400



    # Clean the filename
    # Removes unsafe characters from the original filename
    filename = secure_filename(filename)


    # Checks that the cleaned filename is not empty
    if not filename:

        # Returns an error if the filename is invalid
        return jsonify({
            "error": "Invalid filename."
        }), 400



    # Generate a unique encrypted filename
    # UUID creates a random unique identifier for the stored file
    # The .enc extension shows that this is an encrypted file
    storage_name = str(uuid.uuid4()) + ".enc"


    # Creates the path to the encrypted_files folder
    storage_folder = Path(current_app.root_path) / "encrypted_files"


    # Creates the folder if it does not already exist
    storage_folder.mkdir(parents=True, exist_ok=True)


    # Creates the full path where the encrypted file will be saved
    file_path = storage_folder / storage_name


    # Starts with no database connection
    # This allows us to check whether a connection was successfully opened later
    connection = None


    # Starts error handling in case something goes wrong during the upload
    try:


        # Saves the encrypted file inside the encrypted_files folder
        # The original unencrypted file is not sent to this route
        uploaded_file.save(file_path)


        # Opens a connection to the SQLite database
        connection = get_db_connection()


        # Check that the user account still exists
        # This prevents a file being linked to an account that no longer exists
        user = connection.execute(

            # Searches for the user using their ID
            "SELECT id FROM users WHERE id = ?",

            # Supplies the logged-in user's ID
            (user_id,)

        ).fetchone()


        # Checks whether the user was found in the database
        if not user:


            # Deletes the uploaded file if the user account does not exist
            if file_path.exists():
                os.remove(file_path)


            # Returns an error because the account could not be found
            return jsonify({
                "error": "User account not found."
            }), 401



        # Save the file under the logged-in user's ID
        connection.execute(

            # SQL command that adds the file information to the files table
            """
            INSERT INTO files
            (user_id, filename, storage_name, nonce)
            VALUES (?, ?, ?, ?)
            """,

            # Values that will be saved in the database
            (
                user_id,       # ID of the user who uploaded the file
                filename,      # Original filename
                storage_name,  # Unique name used to store the encrypted file
                nonce          # Nonce needed to decrypt the file later
            )
        )


        # Saves the changes made to the database
        connection.commit()


        # Sends a success message back to the browser
        return jsonify({
            "message": "File uploaded successfully!",
            "filename": filename
        }), 201


    # Handles unexpected errors during the upload
    except Exception:


        # Deletes the encrypted file if the upload process fails
        if file_path.exists():
            os.remove(file_path)


        # Records the error in the Flask application logs
        # This helps with finding and fixing problems
        current_app.logger.exception("File upload failed")


        # Sends an error message back to the browser
        return jsonify({
            "error": "File upload failed."
        }), 500


    # Always runs when the upload function finishes
    finally:

        # Closes the database connection if one was opened
        if connection:
            connection.close()




# Download an encrypted file
# This route is called when the user clicks the Download button
@file_routes.route("/download/<int:file_id>", methods=["GET"])
def download_file(file_id):


    # Get the logged-in user's ID from the Flask session
    user_id = session.get("user_id")


    # Checks whether the user is logged in
    if not user_id:

        # Returns an error if the user is not logged in
        return jsonify({
            "error": "Please log in first."
        }), 401



    # Opens a connection to the SQLite database
    connection = get_db_connection()


    # Starts error handling to make sure the database connection closes
    try:


        # Only retrieve files belonging to this user
        file = connection.execute(

            # Searches for a file using both its ID and the user's ID
            # This prevents users from downloading another user's files
            """
            SELECT *
            FROM files
            WHERE id = ? AND user_id = ?
            """,

            # Supplies the file ID and logged-in user's ID
            (file_id, user_id)

        ).fetchone()


    # Always closes the database connection after the search
    finally:
        connection.close()



    # Checks whether the requested file was found
    if not file:

        # Returns an error if the file does not exist
        # or does not belong to the logged-in user
        return jsonify({
            "error": "File not found."
        }), 404



    # Creates the path to the folder containing encrypted files
    storage_folder = Path(current_app.root_path) / "encrypted_files"


    # Gets the full location of the requested encrypted file
    # Uses the unique storage name saved in the database
    file_path = storage_folder / file["storage_name"]


    # Checks whether the encrypted file actually exists in the folder
    if not file_path.is_file():

        # Returns an error if the stored file cannot be found
        return jsonify({
            "error": "Stored file is missing."
        }), 404



    # Sends the encrypted file back to the user's browser
    response = send_file(

        # Location of the encrypted file
        file_path,

        # Sends the file as general binary data
        mimetype="application/octet-stream",

        # Tells the browser to download the file instead of displaying it
        as_attachment=True,

        # Uses the stored encrypted filename for the download
        download_name=file["storage_name"]
    )


    # Adds the file's nonce to the HTTP response headers
    # The JavaScript needs this nonce to decrypt the downloaded file
    response.headers["X-File-Nonce"] = file["nonce"]


    # Returns the encrypted file and its nonce to the browser
    return response
