from django.urls import path
from . import views

urlpatterns = [
    # path("search/", views.search, name="search"), # non-dynamic search
    path('', views.partial_search, name='partial_search'),
    path("send_to_kindle/", views.send_to_kindle, name="send_to_kindle"),
]