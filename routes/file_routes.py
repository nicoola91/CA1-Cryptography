import os
import uuid
import base64
from pathlib import Path

from flask import (
    Blueprint,
    request,
    session,
    jsonify,
    current_app,
    send_file
)

from werkzeug.utils import secure_filename

from database import get_db_connection


file_routes = Blueprint("file_routes", __name__)


# Upload an encrypted file
@file_routes.route("/upload", methods=["POST"])
def upload_file():

    # Check that the user is logged in
    if "user_id" not in session:
        return jsonify({
            "error": "Please log in first."
        }), 401

    # Get the encrypted file
    uploaded_file = request.files.get("encrypted_file")

    # Get the encryption information
    nonce = request.form.get("nonce")
    filename = request.form.get("filename")

    # Check that all required information was provided
    if not uploaded_file or not nonce or not filename:
        return jsonify({
            "error": "Missing file or encryption information."
        }), 400

    # Check that the uploaded file is not empty
    if uploaded_file.filename == "":
        return jsonify({
            "error": "No file selected."
        }), 400

    # Validate the Base64 nonce
    try:
        decoded_nonce = base64.b64decode(nonce, validate=True)

        if len(decoded_nonce) != 12:
            return jsonify({
                "error": "Invalid encryption nonce."
            }), 400

    except (ValueError, base64.binascii.Error):
        return jsonify({
            "error": "Invalid encryption nonce."
        }), 400

    # Clean the original filename
    filename = secure_filename(filename)

    if not filename:
        return jsonify({
            "error": "Invalid filename."
        }), 400

    # Create a unique name for the encrypted file
    storage_name = str(uuid.uuid4()) + ".enc"

    # Create the encrypted_files folder
    storage_folder = Path(current_app.root_path) / "encrypted_files"
    storage_folder.mkdir(parents=True, exist_ok=True)

    # Set the encrypted file path
    file_path = storage_folder / storage_name

    try:

        # Save the encrypted file
        uploaded_file.save(file_path)

        # Connect to the database
        connection = get_db_connection()

        try:

            # Store the encrypted file information
            connection.execute(
                """
                INSERT INTO files
                (user_id, filename, storage_name, nonce)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    filename,
                    storage_name,
                    nonce
                )
            )

            connection.commit()

        finally:
            connection.close()

        return jsonify({
            "message": "File uploaded successfully!",
            "filename": filename
        }), 201

    except Exception:

        # Remove the saved file if the database operation fails
        if file_path.exists():
            os.remove(file_path)

        current_app.logger.exception("File upload failed")

        return jsonify({
            "error": "File upload failed."
        }), 500


# Download an encrypted file
@file_routes.route("/download/<int:file_id>", methods=["GET"])
def download_file(file_id):

    # Check that the user is logged in
    if "user_id" not in session:
        return jsonify({
            "error": "Please log in first."
        }), 401

    # Find the file belonging to the logged-in user
    connection = get_db_connection()

    try:

        file = connection.execute(
            """
            SELECT *
            FROM files
            WHERE id = ? AND user_id = ?
            """,
            (
                file_id,
                session["user_id"]
            )
        ).fetchone()

    finally:
        connection.close()

    # Check that the file exists
    if not file:
        return jsonify({
            "error": "File not found."
        }), 404

    # Find the encrypted file on the server
    storage_folder = Path(current_app.root_path) / "encrypted_files"
    file_path = storage_folder / file["storage_name"]

    if not file_path.is_file():
        return jsonify({
            "error": "Stored file is missing."
        }), 404

    # Send the encrypted file to the browser
    response = send_file(
        file_path,
        mimetype="application/octet-stream",
        as_attachment=True,
        download_name=file["filename"]
    )

    # Include the encryption nonce in the response
    response.headers["X-File-Nonce"] = file["nonce"]

    return response
