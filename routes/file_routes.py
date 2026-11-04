from flask import Blueprint

file_routes = Blueprint("file_routes", __name__)

@file_routes.route("/upload", methods=["POST"])
def upload_file():
    pass