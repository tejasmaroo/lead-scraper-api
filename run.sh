#!/bin/bash

# Run migrations, seed database, etc. if needed
# python manage.py migrate (example for Django)

# Start the application with Gunicorn
exec gunicorn --config gunicorn_config.py app:app
