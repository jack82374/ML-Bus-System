from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('stops/', views.get_stops, name='stops_data'),
]