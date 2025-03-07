from django.urls import re_path
from ..consumers.terminal_consumer import TerminalConsumer

websocket_urlpatterns = [
    re_path(r"^/?ws/terminal/(?P<session_id>[-\w]+)/?$", TerminalConsumer.as_asgi()),
]
