from django.urls import path

from .admin_views import p2p_network_analytics

urlpatterns = [
    path("p2p-network/", p2p_network_analytics, name="p2p_network_analytics"),
]
