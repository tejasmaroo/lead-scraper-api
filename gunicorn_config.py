import os

# Bind to the port provided by Render
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Number of worker processes
workers = os.environ.get('WEB_CONCURRENCY', 3)

# Use threads for handling requests
threads = os.environ.get('PYTHON_MAX_THREADS', 1)

# Timeout in seconds
timeout = 60

# Access log configuration
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Error log
errorlog = '-'

# Disable daemon mode
daemon = False
