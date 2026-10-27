# FanClub Navi Mumbai — Full-Stack Website

A responsive Flask + SQLite project for a local sports booking website. Includes a public website, booking form, contact form, and password-protected admin dashboard.

## Features
- Responsive green, yellow, and white design
- Football, Cricket, Badminton, Padel, Pickleball, and Basketball cards
- Booking form with date, slot, sport, player count, and contact details
- Booking requests saved to SQLite
- Basic conflict check for a sport/date/time slot
- Contact messages saved to SQLite
- Admin login and booking status management
- Health endpoint at `/health`

## Venue details
- **Venue:** Ryan Vibgyor KPC Empyrean, Kharghar, Navi Mumbai
- **Price:** ₹200 per player / slot
- **Evening slots:** 8:00 PM–9:00 PM and 9:00 PM–10:00 PM
- **Contact:** +91 86899 22049

## Run locally (Windows)
1. Install Python 3.10+.
2. Extract this ZIP and open the extracted folder in VS Code.
3. Open Terminal in that folder and run:

   ```powershell
   py -m venv .venv
   .venv\\Scripts\\activate
   pip install -r requirements.txt
   python app.py
   ```

4. Open `http://127.0.0.1:5000`.

If PowerShell blocks activation, run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and then `.\.venv\Scripts\python.exe app.py`.

## Admin dashboard
- URL: `http://127.0.0.1:5000/admin/login`
- Default demo username: `admin`
- Default demo password: `FanClub@123`

**Before deploying publicly:** set strong `SECRET_KEY`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD` environment variables. The defaults are for local demonstration only. Do not use the demo password for a public deployment.

## Deploy on Render
1. Push this folder to a GitHub repository.
2. Create a new **Web Service** on Render and connect the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add environment variables: `SECRET_KEY` (a long random value), `ADMIN_USERNAME`, and `ADMIN_PASSWORD`.
6. Note: Render's local filesystem can be temporary on some service configurations. For persistent bookings, attach a persistent disk or move the database to a managed database before using it for real customers.

## Important limitations
This is a functional educational project, not a production booking/payment system. It does not process payments, send SMS/email notifications, or provide a live availability calendar. Booking requests are pending until an admin updates the status. Use HTTPS and stronger security controls before accepting real customer data.
