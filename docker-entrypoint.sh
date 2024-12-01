#!/bin/bash

/django/wait-for-it.sh db:3306 -t 60

if /django/venv/bin/python3 manage.py migrate; then
    echo "Migration done successfully."
else
    echo "Failed to migrate." >&2
    exit 1
fi

if /django/venv/bin/python3 manage.py runserver 0.0.0.0:8080; then
    echo "Server start on 0.0.0.0:8080"
else
    echo "Failed to start server." >&2
    exit 1
fi

exec "$@"
