from rest_framework import serializers
from .models import Location, Station, Trip, TripStop

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ('id','uuid', 'name', 'address','station_long', 'station_lat', )

class LocationSerializer(serializers.ModelSerializer):
    stations = StationSerializer(many=True)

    class Meta:
        model = Location
        fields = ('id','uuid', 'name', 'Location_long', 'location_lat', 'stations')

from rest_framework import serializers
from .models import Trip
class TripStopSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='station.name')

    class Meta:
        model = TripStop
        fields = ('id','uuid', 'station', 'location_name', 'arrival_time', 'departure_time')
    def validate(self, data):
        # Call the parent validate method
        super().validate(data)

        # Check if there are any stops
        if not self.context['trip'].tripstop_set.exists():
            raise serializers.ValidationError("At least one stop is required.")

        return data
class TripSerializer(serializers.ModelSerializer):
    start_station_name = serializers.CharField(source='start_location.name')
    end_station_name = serializers.CharField(source='end_location.name')
    stops = TripStopSerializer(many=True, read_only=True)
    class Meta:
        model = Trip
        fields = ('id', 'uuid','start_time', 'arrival_time', 'bus', 'start_location', 'end_location', 'distance', 'duration', 'status', 'end_station_name', 'start_station_name','stops','get_available_chairs')

class AvailableTripSerializer(serializers.ModelSerializer):
    start_location_name = serializers.CharField(source='start_location.name')
    end_location_name = serializers.CharField(source='end_location.name')
    trips = TripSerializer(many=True)

    class Meta:
        model = Trip
        fields = ('start_location', 'uuid','end_location', 'trips', 'start_location_name', 'end_location_name')