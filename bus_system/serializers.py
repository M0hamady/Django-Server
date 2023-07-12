import os
from rest_framework import serializers
from .models import BusTrip, Chair, Location, Payment, Reservation, Station, Trip, TripStop

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
        fields = ('id', 'uuid',
                  'get_start_datetime', 'arrival_time',
                    'bus', 'start_location',
                      'end_location', 'distance', 
                      'duration', 'status', 'end_station_name',
                        'start_station_name','stops',
                        'bus_trip_chairs','get_available_chairs')
class TripPaymentSerializer(serializers.ModelSerializer):
    start_station_name = serializers.CharField(source='start_location.name')
    end_station_name = serializers.CharField(source='end_location.name')
    class Meta:
        model = Trip
        fields = ('id', 'uuid',
                  'start_time', 'arrival_time',
                    'bus', 'start_location',
                      'end_location', 'distance', 
                      'duration', 'status', 'end_station_name',
                        'start_station_name',
                        )

class AvailableTripSerializer(serializers.ModelSerializer):
    start_location_name = serializers.CharField(source='start_location.name')
    end_location_name = serializers.CharField(source='end_location.name')
    trips = TripSerializer(many=True)

    class Meta:
        model = Trip
        fields = ('start_location', 'uuid','end_location', 'trips', 'start_location_name', 'end_location_name')

class ChairSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chair
        fields = ['id', 'bus_trip', 'number', 'status', 'chair_type', 'price_per_chair', 'uuid','payment_status']
        read_only_fields = ['id', 'bus', 'number', 'chair_type', 'price_per_chair', 'uuid']
    def validate(self, data):
        if data.get('status') == 'reserved' and not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError('Only authenticated users can reserve chairs.')

        return data


class BusPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusTrip
        fields = '__all__'
class BusSerializer(serializers.ModelSerializer):
    trip = serializers.SerializerMethodField()

    class Meta:
        model = BusTrip
        fields = '__all__'

    def get_trip(self, obj):
        return TripSerializer(obj.trip).data
class PaymentSerializer(serializers.ModelSerializer):
    # chair = serializers.SerializerMethodField()
    # bus = serializers.SerializerMethodField()
    # trip = serializers.SerializerMethodField()
    

    class Meta:
        model = Payment
        fields = '__all__'
    # def get_chair(self, obj):
    #     return ChairSerializer(obj.reservation.chair).data

    # def get_bus(self, obj):
    #     print(Reservation.objects.get(uuid=obj.reservation.uuid).chair.busTrip_uuid)
    #     return BusPaymentSerializer(Reservation.objects.get(uuid=obj.reservation.uuid).chair.bus_trip).data

    # def get_trip(self, obj):
    #     return TripPaymentSerializer(obj.reservation.chair.bus_trip.trip).data
    
class ReservedChairSerializer(serializers.Serializer):
    bus = serializers.CharField()
    number = serializers.IntegerField()
    chair_type = serializers.CharField(source='chair.chair_type.name')
    price_per_chair = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    commission = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        fields = ['bus', 'number', 'chair_type', 'price_per_chair', 'payment_fee', 'commission', 'total_cost']

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
class ReservationSerializer(serializers.ModelSerializer):
    chair_uuid = serializers.ReadOnlyField(source='chair.uuid')
    chair_name = serializers.ReadOnlyField(source='chair.name')
    chair_price = serializers.ReadOnlyField(source='chair.price')
    payment = PaymentSerializer(read_only=True)
    payment_fee = serializers.DecimalField(max_digits=10, decimal_places=2, source='payment.payment_fee')
    commission = serializers.DecimalField(max_digits=10, decimal_places=2, source='payment.commission')
    total_cost = serializers.SerializerMethodField()
    offer = serializers.SerializerMethodField()
    reserved_chairs = ReservedChairSerializer(many=True, read_only=True)
    barcode = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ['id','uuid','status','can_cancel', 'chair_uuid', 'chair_name', 'chair_price', 'payment', 'payment_fee', 'commission', 'total_cost', 'offer', 'reserved_chairs','barcode']

    def get_total_cost(self, obj):
        # Calculate the total cost by adding the chair price and payment fee
        # and commission
        return obj.chair.price_per_chair + obj.payment.payment_fee + obj.payment.commission

    def get_offer(self, obj):
        # Add logic to calculate the offer, if any
        return None
    def validate(self, data):
        # Check if the chair is already reserved
        if data.get('status') == 'reserved' and not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError('Only authenticated users can reserve chairs.')

        return data
    def get_barcode(self, obj):
        if obj.barcode:
            # Get the full URL for the barcode image using the MEDIA_URL setting
            barcode_url = obj.barcode.url
            if barcode_url.startswith(settings.MEDIA_URL):
                barcode_url = barcode_url[len(settings.MEDIA_URL):]
            # Update the base URL and barcode path to match the new location
            base_url = 'http://localhost:8000' # Replace with the full URL of your Django project
            barcode_path = os.path.join('reservations', 'barcode', obj.user.username, os.path.basename(obj.barcode.name))
            barcode_path = barcode_path.replace("\\", "/") # replace backslashes with forward slashes
            return base_url + settings.MEDIA_URL + barcode_path+'.png'

        return None
    