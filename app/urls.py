from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/airlines/search/', search_airlines),  # GET
    path('api/airlines/<int:airline_id>/', get_airline_by_id),  # GET
    path('api/airlines/<int:airline_id>/image/', get_airline_image),  # GET
    path('api/airlines/<int:airline_id>/update/', update_airline),  # PUT
    path('api/airlines/<int:airline_id>/update_image/', update_airline_image),  # PUT
    path('api/airlines/<int:airline_id>/delete/', delete_airline),  # DELETE
    path('api/airlines/create/', create_airline),  # POST
    path('api/airlines/<int:airline_id>/add_to_flight/', add_airline_to_flight),  # POST

    # Набор методов для заявок
    path('api/flights/search/', search_flights),  # GET
    path('api/flights/<int:flight_id>/', get_flight_by_id),  # GET
    path('api/flights/<int:flight_id>/update/', update_flight),  # PUT
    path('api/flights/<int:flight_id>/update_state/', update_flight_state),  # PUT
    path('api/flights/<int:flight_id>/update_status_user/', update_status_user),  # PUT
    path('api/flights/<int:flight_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/flights/<int:flight_id>/delete/', delete_flight),  # DELETE
    path('api/flights/<int:flight_id>/delete_airline/<int:airline_id>/', delete_airline_from_flight),  # DELETE
 
    # Набор методов для аутентификации и авторизации
    path("api/register/", register),
    path("api/login/", login),
    path("api/check/", check),
    path("api/logout/", logout)
]
