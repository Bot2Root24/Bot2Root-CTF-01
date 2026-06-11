#!/bin/bash
set -e
python3 /app/init_db.py
service nginx start
exec gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 120 app:app
