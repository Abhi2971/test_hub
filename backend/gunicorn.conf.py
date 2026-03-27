"""
Gunicorn configuration for ExamSaaS production deployment.
"""
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "sync"
worker_connections = 1000
threads = 2
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '{"remote_addr":"%(h)s","request_id":"%({X-Request-ID}i)s","response_code":"%(s)s","request_method":"%(m)s","request_path":"%(U)s","request_time":"%(D)s","response_length":"%(B)s"}'

# Process naming
proc_name = "examsaas-api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Preload application
preload_app = True

# Worker lifecycle hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    pass


def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    pass


def when_ready(server):
    """Called just after the server is started."""
    pass


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    pass


def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    pass


def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    pass


def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    pass


def pre_exec(server):
    """Called just before a new master process is forked."""
    pass


def pre_request(worker, req):
    """Called just before a worker processes the request."""
    worker.log.debug("%s %s" % (req.method, req.path))


def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    pass


def child_exit(server, worker):
    """Called just after a worker has been exited."""
    pass


def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    pass


def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    pass


def on_exit(server):
    """Called just before exiting Gunicorn."""
    pass
