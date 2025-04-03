from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('stops/', views.get_stops, name='stops_data'),
    path('locations/', views.get_locations, name='live_locations'),
    path('shapes/', views.get_shapes, name='get_shapes'),
    path('stop_entries/<str:stop_id>/', views.stop_entries, name='stop_entries'),
    path('stop_example/<str:stop_id>/', views.stop_page, name='stops_page'),
    path('stop_example_admin/<str:stop_id>/', views.stop_page_admin, name='stops_page'),
    path('about/', views.about, name='about')
    #path('predict/', views.predict, name='predict')
]