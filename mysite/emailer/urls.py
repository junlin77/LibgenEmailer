from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("send_to_kindle/", views.send_to_kindle, name="send_to_kindle")
]