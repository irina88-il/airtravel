from django.db import connection
from django.shortcuts import render, redirect

from .models import *


def get_draft_flight():
    return Flight.objects.filter(status=1).first()


def index(request):
    query = request.GET.get("query", "")
    airlines = Airline.objects.filter(name__icontains=query).filter(status=1)
    draft_flight = get_draft_flight()
    print(draft_flight)

    context = {
        "query": query,
        "airlines": airlines,
        "draft_flight_id": draft_flight.pk if draft_flight else None
    }

    return render(request, "home_page.html", context)


def airline_details(request, airline_id):
    context = {
        "airline": Airline.objects.get(id=airline_id)
    }

    return render(request, "airline_page.html", context)


def airline_delete(request, airline_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE airlines SET status = 2 WHERE id = %s", [airline_id])

    return redirect("/")


def flight_details(request, flight_id):
    flight = Flight.objects.get(id=flight_id)

    context = {
        "flight": flight,
        "airlines": flight.airlines.all()
    }

    return render(request, "flight_page.html", context)


def airline_add_to_flight(request, airline_id):
    airline = Airline.objects.get(pk=airline_id)

    flight = get_draft_flight()

    if flight is None:
        flight = Flight.objects.create()

    flight.airlines.add(airline)
    flight.save()

    return redirect("/")


def flight_delete(request, flight_id):
    flight = Flight.objects.get(pk=flight_id)
    flight.status = 5
    flight.save()
    return redirect("/")