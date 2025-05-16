#!/bin/bash
echo "Initializing database..."
python app/db/init_db.py
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
