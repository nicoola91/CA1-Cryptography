from flask import(
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)

from services.auth_service import register_user, authenticate_user

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please complete all fields.")
            return redirect(url_for("auth.register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.")
            return redirect(url_for("auth.register"))

        if register_user(username, email, password):
            flash("Registration successful. Please log in.")
            return redirect(url_for("auth.login"))

        flash("That email address is already registered!")
        return redirect(url_for("auth.register"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        user = authenticate_user(email, password)

        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!")

            return redirect(url_for("main.dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


@auth.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))
