
# Imports the tools needed to create and manage website pages
from flask import Blueprint, render_template, session, redirect, url_for

# Imports the function that gets files belonging to a specific user
from database import get_user_files


# Creates a Blueprint called main to organise the main website routes
main = Blueprint("main", __name__)


# Creates the homepage route (http://127.0.0.1:5000/)
@main.route("/")
def home():

    # Checks whether the user is currently logged in
    if "user_id" in session:

        # If the user is logged in, send them to their dashboard
        return redirect(url_for("main.dashboard"))

    # If the user is not logged in, send them to the login page
    return redirect(url_for("auth.login"))



# Creates the dashboard route (http://127.0.0.1:5000/dashboard)
@main.route("/dashboard")
def dashboard():

    # Checks whether the user is logged in
    if "user_id" not in session:

        # If they are not logged in, send them to the login page
        return redirect(url_for("auth.login"))


    # Gets the logged-in user's ID from the Flask session
    user_id = session.get("user_id")


    # Gets only the files belonging to this user from the database
    files = get_user_files(user_id)


    # Loads the dashboard.html page and sends information to it
    return render_template(

        # The HTML template that Flask should display
        "dashboard.html",

        # Sends the logged-in user's username to the dashboard
        username = session.get("username"),

        # Sends the user's files to the dashboard
        files = files
    )
