"""
routes/admin.py
Admin panel — view users, emergency reports, and travel history.
Protected by a simple admin flag on the user record.
Default admin credentials: username=admin / password=admin123
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os
from functools import wraps

admin_bp = Blueprint("admin", __name__)
DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expressway.db")


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_db_conn():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def admin_required(f):
    """Decorator that checks both login AND admin flag."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in.", "warning")
            return redirect(url_for("auth.login"))
        if not session.get("is_admin"):
            flash("Admin access only.", "danger")
            return redirect(url_for("dashboard.dashboard"))
        return f(*args, **kwargs)
    return decorated


def ensure_admin_exists():
    """Create default admin account on first run if it doesn't exist."""
    conn = get_db_conn()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = 'admin'"
    ).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, 1)",
            ("admin", "admin@expressway.com", generate_password_hash("admin123"))
        )
        conn.commit()
        print("[Admin] Default admin account created → username: admin / password: admin123")
    conn.close()


# Create admin on import
try:
    ensure_admin_exists()
except Exception:
    pass  # DB may not exist yet on first import; init_db() handles it


# ── Admin Panel ───────────────────────────────────────────────────────────────
@admin_bp.route("/admin")
@admin_required
def admin_panel():
    """Main admin dashboard with all data tables."""
    conn = get_db_conn()

    users      = conn.execute(
        "SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()

    emergencies = conn.execute(
        """SELECT er.*, u.username
           FROM emergency_reports er
           LEFT JOIN users u ON er.user_id = u.id
           ORDER BY er.created_at DESC"""
    ).fetchall()

    routes = conn.execute(
        """SELECT rh.*, u.username
           FROM route_history rh
           LEFT JOIN users u ON rh.user_id = u.id
           ORDER BY rh.created_at DESC"""
    ).fetchall()

    conn.close()

    stats = {
        "total_users":       len(users),
        "total_routes":      len(routes),
        "total_emergencies": len(emergencies),
        "pending_alerts":    sum(1 for e in emergencies if e["status"] == "Pending"),
    }

    return render_template(
        "admin.html",
        users=users,
        emergencies=emergencies,
        routes=routes,
        stats=stats
    )


# ── Update emergency status ───────────────────────────────────────────────────
@admin_bp.route("/admin/resolve/<int:report_id>", methods=["POST"])
@admin_required
def resolve_emergency(report_id):
    conn = get_db_conn()
    conn.execute(
        "UPDATE emergency_reports SET status = 'Resolved' WHERE id = ?", (report_id,)
    )
    conn.commit()
    conn.close()
    flash(f"Report #{report_id} marked as resolved.", "success")
    return redirect(url_for("admin.admin_panel"))
