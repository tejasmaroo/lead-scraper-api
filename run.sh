#!/bin/bash

# Install compatible versions of dependencies
pip install flask==2.0.1 werkzeug==2.0.2 openai==0.28.1 python-dotenv==0.19.2

# Start the application with Gunicorn
exec gunicorn --config gunicorn_config.py app:app
