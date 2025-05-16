#!/bin/bash
# filepath: /Users/user/Documents/dev/projects/misc/jarvis/python-backend/setup_db.sh

# Make sure we're in the correct directory
cd "$(dirname "$0")"

echo "Setting up the database..."

# Run the init_db.py script
python3 app/db/init_db.py

echo "Database setup completed."
