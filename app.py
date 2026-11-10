
import os
from flask import Flask

from database import initialise_database
from routes.file_routes import file_routes
from routes.auth_routes import auth
from routes.main_routes import main

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Load the secret key from an environment variable.
# Do not hard-code the secret key in the project.
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "FLASK_SECRET_KEY is missing. "
        "Set it in PowerShell before starting Flask. "
    )

app.register_blueprint(auth)
app.register_blueprint(main)
app.register_blueprint(file_routes)

initialise_database()

if __name__ == "__main__":
    app.run(debug=True)
