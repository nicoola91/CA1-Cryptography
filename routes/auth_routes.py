
# Imports the Flask tools needed to create and manage authentication routes
from flask import (
    Blueprint,       # Organises related routes into a separate file
    render_template, # Displays HTML pages
    request,         # Gets information sent from the browser
    redirect,        # Sends the user to another page
    url_for,         # Gets the URL for a specific Flask route
    session,         # Stores information about the logged-in user
    flash,           # Displays messages on the website
    jsonify          # Sends responses back to JavaScript in JSON format
)


# Imports the functions used to register users and check login details
from services.auth_service import register_user, authenticate_user


# Creates a Blueprint called auth to organise account-related routes
auth = Blueprint("auth", __name__)




# Register route
# Allows users to create a new SecureVault account
# Supports GET to display the page and POST to submit the form
@auth.route("/register", methods=["GET", "POST"])
def register():


    # Checks whether the user has submitted the registration form
    if request.method == "POST":


        # Gets the username entered in the registration form
        # Removes any unnecessary spaces from the beginning and end
        username = request.form.get("username", "").strip()


        # Gets the email address entered by the user
        # Removes unnecessary spaces
        email = request.form.get("email", "").strip()


        # Gets the password entered by the user
        password = request.form.get("password", "")



        # Get the protected encryption key information

        # Gets the encrypted master key sent by JavaScript
        encrypted_master_key = request.form.get("encrypted_master_key", "")


        # Gets the random salt used when protecting the master key
        key_salt = request.form.get("key_salt", "")


        # Gets the nonce used when encrypting the master key
        key_nonce = request.form.get("key_nonce", "")



        # Check required fields

        # Checks that the username, email and password have been entered
        if not username or not email or not password:

            # Displays an error message on the registration page
            flash("Please complete all fields.")

            # Sends the user back to the registration page
            return redirect(url_for("auth.register"))


        # Checks that the password contains at least 8 characters
        if len(password) < 8:

            # Displays an error message if the password is too short
            flash("Password must be at least 8 characters.")

            # Sends the user back to the registration page
            return redirect(url_for("auth.register"))



        # Check encryption information

        # Makes sure the encrypted master key, salt and nonce were provided
        if not encrypted_master_key or not key_salt or not key_nonce:

            # Displays an error if the encryption setup is incomplete
            flash("Encryption setup is incomplete. Please try again.")

            # Sends the user back to the registration page
            return redirect(url_for("auth.register"))



        # Register the user

        # Calls register_user() to save the new account in the database
        if register_user(
            username,
            email,
            password,
            encrypted_master_key,
            key_salt,
            key_nonce
        ):

            # Displays a message confirming that registration was successful
            flash("Registration successful. Please log in.")

            # Sends the new user to the login page
            return redirect(url_for("auth.login"))


        # If registration fails, the email address may already be in use
        flash("That email address is already registered!")


        # Sends the user back to the registration page
        return redirect(url_for("auth.register"))


    # If the user has not submitted the form,
    # displays the registration page
    return render_template("register.html")




# Login route
# Allows existing users to sign in to SecureVault
# Supports GET to display the page and POST to process login details
@auth.route("/login", methods=["GET", "POST"])
def login():


    # Checks whether the user has submitted their login details
    if request.method == "POST":


        # Get login information from JSON

        # Gets the information sent from the login page using JavaScript
        # silent=True prevents an error if the request is not valid JSON
        # or does not contain JSON data
        data = request.get_json(silent=True) or {}


        # Gets the email address from the submitted JSON information
        email = data.get("email", "")


        # Gets the password from the submitted JSON information
        password = data.get("password", "")



        # Check the user's login details

        # Calls authenticate_user() to check the email and password
        user = authenticate_user(email, password)


        # Checks whether the login details were incorrect
        if not user:

            # Sends an error message back to the login page as JSON
            # HTTP status 401 means the user is not authorised
            return jsonify({
                "error": "Invalid email or password."
            }), 401



        # Check that encryption information exists

        # Gets the encrypted master key stored for this user
        encrypted_master_key = user["encrypted_master_key"]


        # Gets the salt stored for this user's master key
        key_salt = user["key_salt"]


        # Gets the nonce stored for this user's master key
        key_nonce = user["key_nonce"]


        # Checks that all the encryption information is available
        if not encrypted_master_key or not key_salt or not key_nonce:

            # Sends an error if the encryption information is missing
            return jsonify({
                "error": "Encryption key information is missing."
            }), 400



        # Start the user's session

        # Clears any previous session information
        session.clear()


        # Stores the logged-in user's ID in the session
        session["user_id"] = user["id"]


        # Stores the logged-in user's username in the session
        session["username"] = user["username"]



        # Return the protected key information to the browser

        # Sends a successful login response back to JavaScript
        return jsonify({

            # Message confirming that login was successful
            "message": "Login successful!",

            # Sends the user's ID so JavaScript can identify their account
            "user_id": user["id"],

            # Sends the encrypted master key to the browser
            "encrypted_master_key": encrypted_master_key,

            # Sends the salt needed to recreate the wrapping key
            "key_salt": key_salt,

            # Sends the nonce needed to unlock the master key
            "key_nonce": key_nonce,

            # Sends the URL of the dashboard
            "dashboard_url": url_for("main.dashboard")
        })


    # If the user has not submitted their login details,
    # displays the login page
    return render_template("login.html")




# Logout route
# Allows a logged-in user to sign out of SecureVault
# Only accepts POST requests
@auth.route("/logout", methods=["POST"])
def logout():


    # Clears all information from the user's session
    # This means Flask no longer treats them as logged in
    session.clear()


    # Displays a message confirming that the user has logged out
    flash("You have been logged out.")


    # Sends the user back to the login page
    return redirect(url_for("auth.login"))
