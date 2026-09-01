import os


bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = 2
threads = 2
worker_class = 'gthread'
timeout = 120
accesslog = '-'
errorlog = '-'

# Load the Flask application before opening the listening socket. This keeps
# Autoscale health checks from reaching workers while heavy dependencies are
# still being imported.
preload_app = True