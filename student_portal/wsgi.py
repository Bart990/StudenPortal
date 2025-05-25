"""
WSGI-точка входа, генерируется стандартной командой django-admin startproject
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_portal.settings")
application = get_wsgi_application()
