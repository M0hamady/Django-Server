import datetime
from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .serializers import AvailableTripSerializer
from rest_framework import status

from bus_system.models import Bus, Location, Station, Trip
from .serializers import LocationSerializer, TripSerializer

class LocationStationList(generics.ListAPIView):
    serializer_class = LocationSerializer

    def get_queryset(self):
        queryset = Location.objects.all().prefetch_related('stations')
        return queryset
    
class TripList(APIView):
    def post(self, request, format=None):
        start_location_id = request.data.get('start_location_id')
        end_location_id = request.data.get('end_location_id')
        travel_date_str = request.data.get('travel_date')

        errors = {}

        if not start_location_id:
            errors['start_location_id'] = 'start_location_id is required. Example: 1234'

        if not end_location_id:
            errors['end_location_id'] = 'end_location_id is required. Example: 5678'

        if not travel_date_str:
            errors['travel_date'] = 'travel_date is required. Example: 2023-07-01'
        else:
            try:
                travel_date = datetime.datetime.strptime(travel_date_str, '%Y-%m-%d').date()
                if travel_date < timezone.now().date():
                    errors['travel_date'] = 'Travel date cannot be in the past. Example: 2023-07-01'
            except ValueError:
                errors['travel_date'] = 'Invalid travel_date format. Please use YYYY-MM-DD. Example: 2023-07-01'

        if errors:
            return Response({'message': 'Input validation failed.', 'errors': errors}, status=400)

        try:
            start_location = Location.objects.get(id=start_location_id)
        except Location.DoesNotExist:
            errors['start_location_id'] = f'Invalid start_location_id. Example: 1234'

        try:
            end_location = Location.objects.get(id=end_location_id)
        except Location.DoesNotExist:
            errors['end_location_id'] = f'Invalid end_location_id. Example: 5678'

        if errors:
            return Response({'message': 'Input validation failed.', 'errors': errors}, status=400)

        # Get the list of available trips for the given travel date
        available_trips = Trip.get_available_trips(start_location, end_location, travel_date)

        # Serialize the available trips and return the response
        serializer = AvailableTripSerializer({'start_location': start_location, 'end_location': end_location, 'trips': available_trips})
        return Response(serializer.data)
    


class BusInTripAPI(APIView):
    def post(self, request):
        trip_id = request.data.get('trip_uud')
        # bus_id = request.data.get('bus_id')

        if trip_id is None:
            return Response({'error': 'trip_id  are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            trip = Trip.objects.get(uuid=trip_id)
        except Trip.DoesNotExist:
            return Response({'error': f'Trip with ID {trip_id} does not exist'}, status=status.HTTP_404_NOT_FOUND)

        try:
            bus = trip.bus
        except Bus.DoesNotExist:
            return Response({'error': f'Bus not found in trip with Uuid {trip_id}'}, status=status.HTTP_400_BAD_REQUEST)

        # if bus.id != bus_id:
        #     return Response({'error': f'Bus with Uuid {bus_id} not found in trip with Uuid {trip_id}'}, status=status.HTTP_400_BAD_REQUEST)

        bus_data = {
            'uuid': bus.uuid,
            'available_seats': bus.unreserved_chairs,
            'bus_seats': bus.number_of_chairs,
            # 'bus_salon':bus.bus_salon,
            # 'seating_capacity': bus.seating_capacity,
            # 'reserved_chairs_count': bus.reserved_chairs_count,
            # 'unreserved_chairs_count': bus.unreserved_chairs_count,
        }
        return Response(bus_data, status=status.HTTP_200_OK)
    



def index(request):
    return render(request, 'base.html')