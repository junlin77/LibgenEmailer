from django.urls import path
from . import views

urlpatterns = [
    path("", views.search, name="search"),
    path('partial-search/', views.partial_search, name='partial_search'),
    path("send_to_kindle/", views.send_to_kindle, name="send_to_kindle"),
]