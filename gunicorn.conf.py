import os

# Render and most cloud hosts set the PORT environment variable.
# Default to 5000 for local runs.
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"

# Concurrency settings suitable for Render free / standard tiers
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
threads = int(os.environ.get("PYTHON_GET_THREADS", "2"))
timeout = 120
accesslog = "-"
errorlog = "-"
