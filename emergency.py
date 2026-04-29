"""
routes/emergency.py
Emergency alert reporting — users can report incidents on the road.
Reports are stored in the SQLite database for admin review.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3, os
from functools import wraps

emergency_bp = Blueprint("emergency", __name__)
DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expressway.db")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def get_db_conn():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ── Report Emergency (GET shows form / POST submits) ─────────────────────────
@emergency_bp.route("/emergency", methods=["GET", "POST"])
@login_required
def emergency():
    if request.method == "POST":
        location    = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()

        if not location or not description:
            flash("Both location and description are required.", "danger")
            return render_template("emergency.html")

        conn = get_db_conn()
        conn.execute(
            "INSERT INTO emergency_reports (user_id, location, description) VALUES (?, ?, ?)",
            (session["user_id"], location, description)
        )
        conn.commit()
        conn.close()

        flash("🚨 Emergency report submitted! Authorities have been notified.", "success")
        return redirect(url_for("emergency.emergency"))

    return render_template("emergency.html")
