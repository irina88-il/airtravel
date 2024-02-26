from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializer import *


def get_draft_flight():
    return Flight.objects.filter(status=1).first()


@api_view(["GET"])
def search_airlines(request):
    query = request.GET.get("query", "")
    airlines = Airline.objects.filter(status=1).filter(name__icontains=query)
    serializer = AirlineSerializer(airlines, many=True)

    draft_flight = get_draft_flight()

    data = {
        "airlines": serializer.data,
        "draft_flight_id": draft_flight.pk if draft_flight else None
    }

    return Response(data)


@api_view(["GET"])
def get_airline_by_id(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    serializer = AirlineSerializer(airline, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_airline(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    serializer = AirlineSerializer(airline, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_airline(request):
    Airline.objects.create()

    airlines = Airline.objects.all()
    serializer = AirlineSerializer(airlines, many=True)
    
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_airline(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    airline.status = 2
    airline.save()

    airlines = Airline.objects.filter(status=1)
    serializer = AirlineSerializer(airlines, many=True)
    
    return Response(serializer.data)


@api_view(["POST"])
def add_airline_to_flight(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)

    flight = get_draft_flight()

    if flight is None:
        flight = Flight.objects.create()

    flight.airlines.add(airline)
    flight.save()

    serializer = AirlineSerializer(flight.airlines, many=True)
    
    return Response(serializer.data)


@api_view(["GET"])
def get_airline_image(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)

    return HttpResponse(airline.image, content_type="image/png")


@api_view(["PUT"])
def update_airline_image(request, airline_id):
    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    airline = Airline.objects.get(pk=airline_id)
    serializer = AirlineSerializer(airline, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["GET"])
def get_flights(request):
    status = int(request.GET.get("status", -1))
    date_start = request.GET.get("date_start")
    date_end = request.GET.get("date_end")

    flights = Flight.objects.exclude(status__in=[1, 5])

    if status != -1:
        flights = flights.filter(status=status)

    if date_start and parse_datetime(date_start):
        flights = flights.filter(date_formation__gte=parse_datetime(date_start))

    if date_end and parse_datetime(date_end):
        flights = flights.filter(date_formation__lte=parse_datetime(date_end))

    serializer = FlightSerializer(flights, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_flight_by_id(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)
    serializer = FlightSerializer(flight, many=False)
    
    return Response(serializer.data)


@api_view(["PUT"])
def update_flight(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)
    serializer = FlightSerializer(flight, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    flight.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)

    if flight.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight.status = 2
    flight.date_formation = timezone.now()
    flight.save()

    serializer = FlightSerializer(flight, many=False)
    
    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, flight_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = request.data["status"]

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight = Flight.objects.get(pk=flight_id)

    if flight.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    flight.status = request_status
    flight.date_complete = timezone.now()
    flight.save()

    serializer = FlightSerializer(flight, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
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
def delete_airline_from_flight(request, flight_id, airline_id):
    if not Flight.objects.filter(pk=flight_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not Airline.objects.filter(pk=airline_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    flight = Flight.objects.get(pk=flight_id)
    flight.airlines.remove(Airline.objects.get(pk=airline_id))
    flight.save()

    serializer = AirlineSerializer(flight.airlines, many=True)
    
    return Response(serializer.data)

