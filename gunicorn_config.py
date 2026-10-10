"""
Gunicorn Configuration for Hetzner CPX22 (3 vCPU, 4GB RAM)
===========================================================

Server Specs:
- VPS: Hetzner CPX22
- CPU: 3 vCPU AMD
- RAM: 4GB
- Storage: 80GB SSD
- Bandwidth: 20TB
- Target: 100-150 concurrent requests
- Workers: 7 (formula: 2 × CPU cores + 1 = 2 × 3 + 1)
"""

import multiprocessing
import os

# Server Socket
bind = "127.0.0.1:8004"
backlog = 1024  # Maximum number of pending connections (reduced for 4GB RAM)

# Worker Processes
# Optimized for 4 vCPU server: 3 workers (reduced for efficiency)
# Each worker ~150-200MB RAM = ~600MB total for workers
workers = int(os.getenv('GUNICORN_WORKERS', '3'))
worker_class = "sync"  # Use sync for Django (gevent/eventlet for async)
worker_connections = 25  # 3 workers × 25 = 75 concurrent requests max
max_requests = 1000  # Restart workers after 1000 requests (prevent memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once
timeout = 120  # Worker timeout in seconds (increased for large file operations)
keepalive = 2  # Keep connections alive for 2 seconds

# Memory Management (Critical for 4GB RAM)
worker_tmp_dir = "/dev/shm"  # Use RAM disk for worker heartbeat (Linux only)
preload_app = True  # Load app before forking workers (saves RAM)

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = "gamesapp_gunicorn"

# Server Mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"

# Server Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("🚀 Starting Gunicorn server for AGames...")
    print(f"💻 Server: Hetzner CPX22 (3 vCPU AMD, 4GB RAM)")
    print(f"📊 Configuration: {workers} workers, {worker_connections} connections/worker")
    print(f"💾 Memory optimized for 4GB RAM")
    print(f"🎯 Max concurrent requests: ~{workers * worker_connections}")

def on_reload(server):
    """Called when server is reloaded."""
    print("🔄 Reloading Gunicorn server...")

def when_ready(server):
    """Called just after the server is started."""
    print(f"✅ Gunicorn server is ready! Listening on {bind}")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    print(f"⚠️ Worker {worker.pid} interrupted")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    print(f"❌ Worker {worker.pid} aborted")

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance Tips:
# =================
# 1. Workers = 7 (for 3 vCPU server) - formula: 2 × 3 + 1
# 2. Each worker uses ~150-200MB RAM
# 3. Total workers RAM: ~1.4GB
# 4. Memory allocation (4GB total):
#    - Gunicorn workers: 1.4GB
#    - PostgreSQL: 1.2GB
#    - Redis: 256MB
#    - Nginx: 50MB
#    - OS: 800MB
#    - Buffer: 300MB
# 5. For better performance, enable Redis caching
# 6. Monitor memory with: htop or free -h
# 6. Consider using --worker-class=gevent with gevent installed for async I/O
# 7. This configuration handles 200-300 concurrent requests efficiently

# To run:
# gunicorn -c gunicorn_config.py gamezone.wsgi:application
