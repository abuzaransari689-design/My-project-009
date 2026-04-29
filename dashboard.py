"""
routes/dashboard.py
User dashboard: route simulation, toll calculation, and travel history.
No external APIs — all route data is generated with realistic random logic.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
import sqlite3, os, random, math
from functools import wraps

dashboard_bp = Blueprint("dashboard", __name__)
DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expressway.db")

TOLL_RATE_PER_KM = 2.0   # ₹2 per km
AVG_SPEED_KMH    = 80    # assumed highway speed


# ── Login-required decorator ─────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def get_db_conn():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ── Route simulation logic ────────────────────────────────────────────────────
def simulate_route(source: str, destination: str) -> dict:
    """
    Generate realistic dummy route data based on source/destination strings.
    Uses a deterministic seed so the same pair always gives the same result.
    """
    seed = sum(ord(c) for c in (source + destination).lower())
    rng  = random.Random(seed)

    distance_km   = round(rng.uniform(15, 450), 1)
    travel_minutes = int((distance_km / AVG_SPEED_KMH) * 60)
    hours, mins   = divmod(travel_minutes, 60)

    traffic_choices = ["Low", "Medium", "High"]
    traffic_weights = [0.4, 0.4, 0.2]
    traffic         = rng.choices(traffic_choices, weights=traffic_weights)[0]

    # Traffic adds delay
    delay = {"Low": 0, "Medium": 10, "High": 25}[traffic]
    total_minutes = travel_minutes + delay
    t_hours, t_mins = divmod(total_minutes, 60)

    toll_amount  = round(distance_km * TOLL_RATE_PER_KM, 2)
    fuel_cost    = round(distance_km * 6, 2)   # ₹6/km average
    total_cost   = round(toll_amount + fuel_cost, 2)

    return {
        "source":      source,
        "destination": destination,
        "distance_km": distance_km,
        "travel_time": f"{t_hours}h {t_mins}m",
        "traffic":     traffic,
        "toll_amount": toll_amount,
        "fuel_cost":   fuel_cost,
        "total_cost":  total_cost,
        "speed_kmh":   AVG_SPEED_KMH,
    }


# ── Dashboard (GET) ───────────────────────────────────────────────────────────
@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard with travel history."""
    conn    = get_db_conn()
    history = conn.execute(
        "SELECT * FROM route_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("dashboard.html", history=history, result=None)


# ── Find Route (POST) ─────────────────────────────────────────────────────────
@dashboard_bp.route("/find_route", methods=["POST"])
@login_required
def find_route():
    """Process the route-finding form and display simulated results."""
    source      = request.form.get("source", "").strip()
    destination = request.form.get("destination", "").strip()

    if not source or not destination:
        flash("Please enter both source and destination.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    if source.lower() == destination.lower():
        flash("Source and destination cannot be the same.", "warning")
        return redirect(url_for("dashboard.dashboard"))

    result = simulate_route(source, destination)

    # Persist to route_history
    conn = get_db_conn()
    conn.execute(
        """INSERT INTO route_history
           (user_id, source, destination, distance_km, travel_time, traffic, toll_amount)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            session["user_id"],
            result["source"],
            result["destination"],
            result["distance_km"],
            result["travel_time"],
            result["traffic"],
            result["toll_amount"],
        )
    )
    conn.commit()
    history = conn.execute(
        "SELECT * FROM route_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("dashboard.html", result=result, history=history)
