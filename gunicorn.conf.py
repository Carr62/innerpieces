# Gunicorn configuration file for Digital Ocean deployment

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

# Number of worker processes (2-4 x CPU cores)
workers = 3

# Worker class
worker_class = "sync"

# Timeout for worker processes
timeout = 120

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "innerpieces"

# Preload app for faster worker spawning
preload_app = True
