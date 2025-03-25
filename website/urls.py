from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('stops/', views.get_stops, name='stops_data'),
    path('locations/', views.get_locations, name='live_locations'),
    path('shapes/', views.get_shapes, name='get_shapes'),
    path('stop_entries/<str:stop_id>/', views.stop_entries, name='stop_entries'),
    path('predict/', views.predict, name='predict')
]