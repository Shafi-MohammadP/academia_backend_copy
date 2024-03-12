import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from notifications import routing as route


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digiClass_backend.settings')


django_asgi_application = get_asgi_application()

websocket_application = AuthMiddlewareStack(
    URLRouter(route.websocket_urlpatterns)
)


application = ProtocolTypeRouter(
    {
        "http": django_asgi_application,
        "websocket": websocket_application
    }
)
# """
# ASGI config for digiClass_backend project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application


# application = get_asgi_application()
