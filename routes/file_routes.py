from flask import (
    Blueprint,
    session,
    redirect,
    url_for,
    send_from_directory,
    request
)

from database import get_user_file, get_db_connection

import os
import uuid
from werkzeug.utils import secure_filename


file_routes = Blueprint("file_routes", __name__)

STORAGE_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "storage"
)


@file_routes.route("/download/<int:file_id>")
def download_file(file_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    file = get_user_file(file_id, session["user_id"])

    if file is None:
        return "File not found", 404

    return send_from_directory(
        STORAGE_FOLDER,
        file["storage_name"],
        as_attachment=True,
        download_name=file["filename"]
    )


@file_routes.route("/upload", methods=["POST"])
def upload_file():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if "file" not in request.files:
        return "No file selected", 400

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return "No file selected", 400

    filename = secure_filename(uploaded_file.filename)

    if not filename:
        return "Invalid filename", 400

    user_id = session["user_id"]

    storage_name = f"{user_id}_{uuid.uuid4().hex}_{filename}"

    os.makedirs(STORAGE_FOLDER, exist_ok=True)

    storage_path = os.path.join(
        STORAGE_FOLDER,
        storage_name
    )

    uploaded_file.save(storage_path)

    connection = get_db_connection()

    try:
        connection.execute(
            """
            INSERT INTO files (
                user_id,
                filename,
                storage_name,
                nonce
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                filename,
                storage_name,
                ""
            )
        )

        connection.commit()

    except Exception:
        if os.path.exists(storage_path):
            os.remove(storage_path)

        raise

    finally:
        connection.close()

    return redirect(url_for("main.dashboard"))