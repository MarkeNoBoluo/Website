# Gunicorn configuration for Flask blog application
# Production WSGI server configuration for Raspberry Pi deployment

# Bind to Unix socket (not TCP port)
# Nginx will connect to this socket
bind = 'unix:/tmp/blog.sock'

# Worker configuration
workers = 2  # As specified in requirements
worker_class = 'sync'  # Default, suitable for Flask
worker_connections = 1000
timeout = 30  # seconds
keepalive = 2

# Process naming and user
proc_name = 'blog'
user = 'pi'  # Run as pi user per user decision
group = 'pi'

# Logging configuration
accesslog = 'logs/gunicorn_access.log'
errorlog = 'logs/gunicorn_error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process management
max_requests = 1000  # Restart workers after 1000 requests to prevent memory leaks
max_requests_jitter = 50  # Add randomness to restart timing
preload_app = True  # Load application before forking workers

# Socket permissions
umask = 0o007  # Socket readable/writable by owner and group
# Note: Nginx (www-data user) needs access - will be handled by adding www-data to pi group

# Application specification
wsgi_app = 'wsgi:app'  # Import path for Gunicorn
chdir = '/home/pi/blog'  # Working directory - adjust as needed for Raspberry Pi deployment