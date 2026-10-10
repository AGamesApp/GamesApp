#!/bin/bash
exec /root/game/agames/venv/bin/gunicorn \
    --config /root/GamesApp/agames-main/gunicorn_config.py \
    gamezone.wsgi:application

