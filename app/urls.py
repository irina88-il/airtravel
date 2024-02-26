from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name="home"),
    path('airlines/<int:airline_id>/', airline_details),
    path('airlines/<int:airline_id>/delete/', airline_delete),
    path('airlines/<int:airline_id>/add_to_flight/', airline_add_to_flight),
    path('flights/<int:flight_id>/', flight_details),
    path('flights/<int:flight_id>/delete/', flight_delete),
]
