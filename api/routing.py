from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/graphql/', consumers.GraphQLConsumer.as_asgi()),
]