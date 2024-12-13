from django.urls import path
from . import views

urlpatterns = [
    path('groundstation/', views.get_groundstation_position),
    path('satellite/<int:satellite_id>/positions/', views.get_satellite_position, name='satellite_positions'),
]
