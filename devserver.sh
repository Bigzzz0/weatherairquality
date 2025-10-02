#!/bin/bash
set -e

# The simple dev server doesn't work well with our preview proxy.
# So, we're using the flask dev server instead.
# Learn more: https://flask.palletsprojects.com/en/3.0.x/cli/#run-the-development-server

if [ -z "$PORT" ]; then
  PORT=5000
fi

# Activate the virtual environment
source .venv/bin/activate

# Set FLASK_APP to specify the application file
export FLASK_APP=main.py

# Run the Flask development server using the virtual environment's python
.venv/bin/python -m flask run --port=$PORT --host=0.0.0.0 --debugger
