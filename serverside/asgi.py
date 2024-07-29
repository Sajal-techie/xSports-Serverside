"""
ASGI config for serverside project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from django.core.asgi import get_asgi_application
import real_time.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'serverside.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            real_time.routing.websocket_urlpatterns
        )
    )
})
