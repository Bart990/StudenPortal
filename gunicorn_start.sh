#!/usr/bin/env bash
. /opt/portal/venv/bin/activate
exec gunicorn portal.wsgi:application \
     --bind unix:/run/portal.sock \
     --workers 3
