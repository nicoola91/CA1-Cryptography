from flask import Blueprint, render_template, session, redirect, url_for

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

    return render_template(
        "dashboard.html",
        username = session.get("username")
    )