#!/bin/bash
exec /root/game/agames/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --worker-class sync \
    --timeout 60 \
    --bind unix:/run/gunicorn.sock \
    gamezone.wsgi:application

