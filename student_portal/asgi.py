"""
ASGI-точка входа для асинхронных серверов (Uvicorn, Daphne, Hypercorn),
а также для WebSocket-функций, фоновых задач и пр.
"""

import os
from django.core.asgi import get_asgi_application

# Файл настроек тот же, что и для WSGI
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_portal.settings')

# ASGI-приложение; можно оборачивать в middleware для WebSocket
application = get_asgi_application()
