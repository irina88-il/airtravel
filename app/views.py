import requests
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .jwt_helper import *
from .permissions import *
from .serializers import *
from .utils import identity_user


def get_draft_flight(request):
    user = identity_user(request)

    if user is None:
        return None

    flight = Flight.objects.filter(owner_id=user.id).filter(status=1).first()

    return flight


@api_view(["GET"])
def search_airlines(request):
    query = request.GET.get("query", "")

    airline = Airline.objects.filter(status=1).filter(name__icontains=query)

    serializer = AirlineSerializer(airline, many=True)

    draft_flight = get_draft_flight(request)

    resp = {
        "airlines": serializer.data,
        "draft_flight_id": draft_flight.pk if draft_flight else None
    }

    return Response(resp)


@api_view(["GET"])
def get_airline_by_id(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    serializer = AirlineSerializer(airline)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_airline(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    serializer = AirlineSerializer(airline, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsModerator])
def create_airline(request):
    airline = Airline.objects.create()

    serializer = AirlineSerializer(airline)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_airline(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    airline.status = 2
    airline.save()

    airline = Airline.objects.filter(status=1)
    serializer = AirlineSerializer(airline, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_airline_to_flight(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)

    flight = get_draft_flight(request)

    if flight is None:
        flight = Flight.objects.create()
        flight.date_perform = timezone.now()
        flight.save()

    if flight.airlines.contains(airline):
        return Response(status=status.HTTP_409_CONFLICT)

    flight.airlines.add(airline)
    flight.owner = identity_user(request)
    flight.save()

    serializer = FlightSerializer(flight)
    return Response(serializer.data)


@api_view(["GET"])
def get_airline_image(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)

    return HttpResponse(airline.image, content_type="image/png")


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_airline_image(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    serializer = AirlineSerializer(airline, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_flights(request):
    user = identity_user(request)

    status_id = int(request.GET.get("status", -1))
    date_start = request.GET.get("date_start")
    date_end = request.GET.get("date_end")

    flights = Flight.objects.exclude(status__in=[1, 5])

    if not user.is_moderator:
        flights = flights.filter(owner=user)

    if status_id > 0:
        flights = flights.filter(status=status_id)

    if date_start and parse_datetime(date_start):
        flights = flights.filter(date_formation__gte=parse_datetime(date_start))

    if date_end and parse_datetime(date_end):
        flights = flights.filter(date_formation__lte=parse_datetime(date_end))

    serializer = FlightsSerializer(flights, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_flight_by_id(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)
    serializer = FlightSerializer(flight)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_flight(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)

    serializer = FlightSerializer(flight, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    flight.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsRemoteService])
def update_flight_state(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)

    serializer = FlightSerializer(flight, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    flight.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)

    flight.status = 2
    flight.date_formation = timezone.now()
    flight.save()

    calculate_state(flight_id)

    serializer = FlightSerializer(flight)

    return Response(serializer.data)


def calculate_state(flight_id):
    data = {
        "flight_id": flight_id
    }

    requests.post("http://127.0.0.1:8080/calc_state/", json=data, timeout=7)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight = Flight.objects.get(pk=flight_id)

    if flight.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight.moderator = identity_user(request)
    flight.status = request_status
    flight.date_complete = timezone.now()
    flight.save()

    serializer = FlightSerializer(flight)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_flight(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)

    if flight.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight.status = 5
    flight.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_airline_from_flight(request, flight_id, airline_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)
    flight.airlines.remove(Airline.objects.get(pk=airline_id))
    flight.save()

    if flight.airlines.count() == 0:
        flight.delete()
        return Response(status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        message = {"message": "invalid credentials"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token(user.id)

    user_data = {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "is_moderator": user.is_moderator,
        "access_token": access_token
    }

    return Response(user_data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    access_token = create_access_token(user.id)

    message = {
        'message': 'User registered successfully',
        'user_id': user.id,
        "access_token": access_token
    }

    return Response(message, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def check(request):
    token = get_access_token(request)

    if token is None:
        message = {"message": "Token is not found"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    if token in cache:
        message = {"message": "Token in blacklist"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    payload = get_jwt_payload(token)
    user_id = payload["user_id"]

    user = CustomUser.objects.get(pk=user_id)
    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    access_token = get_access_token(request)

    if access_token not in cache:
        cache.set(access_token, settings.JWT["ACCESS_TOKEN_LIFETIME"])

    message = {
        "message": "Вы успешно вышли из аккаунта"
    }

    return  Response(message, status=status.HTTP_200_OK)
