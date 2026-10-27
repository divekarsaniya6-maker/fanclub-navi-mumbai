from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "fanclub.db"))

SPORTS = ["Football", "Cricket", "Badminton", "Padel", "Pickleball", "Basketball"]
SLOTS = ["8:00 PM - 9:00 PM", "9:00 PM - 10:00 PM"]
PRICE_PER_SLOT = 200

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                sport TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                players INTEGER NOT NULL DEFAULT 1,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

@app.route("/")
def home():
    return render_template("index.html", sports=SPORTS, slots=SLOTS, price=PRICE_PER_SLOT)

@app.route("/book", methods=["POST"])
def book():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    sport = request.form.get("sport", "").strip()
    booking_date = request.form.get("booking_date", "").strip()
    time_slot = request.form.get("time_slot", "").strip()
    players_raw = request.form.get("players", "1").strip()
    notes = request.form.get("notes", "").strip()

    if not all([name, phone, sport, booking_date, time_slot]):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("home") + "#booking")
    if sport not in SPORTS or time_slot not in SLOTS:
        flash("Please choose a valid sport and time slot.", "error")
        return redirect(url_for("home") + "#booking")
    try:
        players = int(players_raw)
        if players < 1 or players > 30:
            raise ValueError
        datetime.strptime(booking_date, "%Y-%m-%d")
    except ValueError:
        flash("Please enter a valid date and player count (1–30).", "error")
        return redirect(url_for("home") + "#booking")

    with get_db() as conn:
        # Prevent two bookings for the same sport, date and slot from being confirmed/pending together.
        conflict = conn.execute("""
            SELECT id FROM bookings
            WHERE sport = ? AND booking_date = ? AND time_slot = ?
              AND status IN ('Pending', 'Confirmed')
            LIMIT 1
        """, (sport, booking_date, time_slot)).fetchone()
        if conflict:
            flash("That sport and time slot already has a booking request for this date. Please choose another slot or date.", "error")
            return redirect(url_for("home") + "#booking")
        conn.execute("""
            INSERT INTO bookings
            (name, phone, email, sport, booking_date, time_slot, players, notes, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
        """, (name, phone, email, sport, booking_date, time_slot, players, notes, datetime.now().isoformat(timespec="seconds")))
    flash("Booking request submitted! The team will contact you to confirm availability.", "success")
    return redirect(url_for("home") + "#booking")

@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()
    if not name or not message:
        flash("Please enter your name and message.", "error")
        return redirect(url_for("home") + "#contact")
    with get_db() as conn:
        conn.execute(
            "INSERT INTO contact_messages (name, phone, email, message, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, phone, email, message, datetime.now().isoformat(timespec="seconds"))
        )
    flash("Thanks for contacting FanClub! Your message has been saved.", "success")
    return redirect(url_for("home") + "#contact")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        expected_user = os.environ.get("ADMIN_USERNAME", "admin")
        expected_pass = os.environ.get("ADMIN_PASSWORD", "FanClub@123")
        if username == expected_user and password == expected_pass:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("admin_login.html")

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    status_filter = request.args.get("status", "All")
    with get_db() as conn:
        if status_filter in ["Pending", "Confirmed", "Cancelled", "Completed"]:
            bookings = conn.execute("SELECT * FROM bookings WHERE status=? ORDER BY created_at DESC", (status_filter,)).fetchall()
        else:
            bookings = conn.execute("SELECT * FROM bookings ORDER BY created_at DESC").fetchall()
        messages = conn.execute("SELECT * FROM contact_messages ORDER BY created_at DESC").fetchall()
        total = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM bookings WHERE status='Pending'").fetchone()[0]
        confirmed = conn.execute("SELECT COUNT(*) FROM bookings WHERE status='Confirmed'").fetchone()[0]
        message_count = conn.execute("SELECT COUNT(*) FROM contact_messages").fetchone()[0]
    return render_template("admin.html", bookings=bookings, messages=messages,
                           status_filter=status_filter, total=total, pending=pending,
                           confirmed=confirmed, message_count=message_count)

@app.route("/admin/booking/<int:booking_id>/status", methods=["POST"])
def update_status(booking_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    status = request.form.get("status", "")
    if status not in ["Pending", "Confirmed", "Cancelled", "Completed"]:
        flash("Invalid booking status.", "error")
    else:
        with get_db() as conn:
            conn.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
        flash("Booking status updated.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "FanClub Navi Mumbai"})

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG") == "1")
