"""
routes/auth.py
Handles user registration, login, and logout.
Passwords are hashed with werkzeug before storage.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

auth_bp = Blueprint("auth", __name__)
DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expressway.db")


def get_db_conn():
    """Return a fresh SQLite connection (used outside request context)."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ── Home page ────────────────────────────────────────────────────────────────
@auth_bp.route("/")
def index():
    """Public landing page."""
    return render_template("index.html")


# ── Signup ───────────────────────────────────────────────────────────────────
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Register a new user account."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Basic validation
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("signup.html")

        hashed_pw = generate_password_hash(password)

        try:
            conn = get_db_conn()
            conn.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_pw)
            )
            conn.commit()
            conn.close()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))

        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "danger")
            return render_template("signup.html")

    return render_template("signup.html")


# ── Login ────────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate an existing user."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter username and password.", "danger")
            return render_template("login.html")

        conn = get_db_conn()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            # Store user info in session
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = user["is_admin"]
            flash(f"Welcome back, {username}!", "success")

            # Redirect admins to the admin panel
            if user["is_admin"]:
                return redirect(url_for("admin.admin_panel"))
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


# ── Logout ───────────────────────────────────────────────────────────────────
@auth_bp.route("/logout")
def logout():
    """Clear the session and redirect to home."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.index"))
