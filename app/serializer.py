from rest_framework import serializers

from .models import *


class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('name',)


class FlightSerializer(serializers.ModelSerializer):
    reactor = AirlineSerializer(read_only=True, many=True)
    owner = UserSerializer(read_only=True, many=False)
    moderator = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Flight
        fields = "__all__"

