from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, jsonify
)

from services.auth_service import register_user, authenticate_user

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Get the protected encryption key information
        encrypted_master_key = request.form.get("encrypted_master_key", "")
        key_salt = request.form.get("key_salt", "")
        key_nonce = request.form.get("key_nonce", "")

        # Check required fields
        if not username or not email or not password:
            flash("Please complete all fields.")
            return redirect(url_for("auth.register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.")
            return redirect(url_for("auth.register"))

        # Check encryption information
        if not encrypted_master_key or not key_salt or not key_nonce:
            flash("Encryption setup is incomplete. Please try again.")
            return redirect(url_for("auth.register"))

        # Register the user
        if register_user(
            username,
            email,
            password,
            encrypted_master_key,
            key_salt,
            key_nonce
        ):

            flash("Registration successful. Please log in.")
            return redirect(url_for("auth.login"))

        flash("That email address is already registered!")
        return redirect(url_for("auth.register"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        # Get login information from JSON
        data = request.get_json(silent=True) or {}

        email = data.get("email", "")
        password = data.get("password", "")

        # Check the user's login details
        user = authenticate_user(email, password)

        if not user:
            return jsonify({
                "error": "Invalid email or password."
            }), 401

        # Check that encryption information exists
        encrypted_master_key = user["encrypted_master_key"]
        key_salt = user["key_salt"]
        key_nonce = user["key_nonce"]

        if not encrypted_master_key or not key_salt or not key_nonce:
            return jsonify({
                "error": "Encryption key information is missing."
            }), 400

        # Start the user's session
        session.clear()

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        # Return the protected key information to the browser
        return jsonify({
            "message": "Login successful!",
            "encrypted_master_key": encrypted_master_key,
            "key_salt": key_salt,
            "key_nonce": key_nonce,
            "dashboard_url": url_for("main.dashboard")
        })

    return render_template("login.html")


@auth.route("/logout", methods=["POST"])
def logout():

    session.clear()

    flash("You have been logged out.")

    return redirect(url_for("auth.login"))
