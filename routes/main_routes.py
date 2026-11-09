from flask import Blueprint, render_template, session, redirect, url_for
from database import get_user_files

main = Blueprint("main", __name__)

@main.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))

@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    user_id = session.get("user_id")
    files = get_user_files(user_id)

    return render_template(
        "dashboard.html",
        username = session.get("username"),
        files = files
    )