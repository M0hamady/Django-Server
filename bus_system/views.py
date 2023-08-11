import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import generics,permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, F
from main.settings import BASE_DIR
from .serializers import AvailableTripSerializer, ChairSerializer, PaymentSerializer, ReservationSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from bus_system.models import Bus, Chair, Location, Payment, Reservation, Station, Trip
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
            bus = trip.buses_trip()
        except Bus.DoesNotExist:
            return Response({'error': f'Bus not found in trip with Uuid {trip_id}'}, status=status.HTTP_400_BAD_REQUEST)

        # if bus.id != bus_id:
        #     return Response({'error': f'Bus with Uuid {bus_id} not found in trip with Uuid {trip_id}'}, status=status.HTTP_400_BAD_REQUEST)

        bus_data = {
            'uuid': bus.uuid,
            'bus_salon':bus.bus_salon.name,
            # 'bus_seats': bus.number_of_chairs,
            # 'reserved_chairs_count': bus.reserved_chairs_count,
            # 'unreserved_chairs_count': bus.unreserved_chairs_count,
            'bus_seats_details': bus.number_of_chairs,
            'available_seats': bus.unreserved_chairs,
        }
        return Response(bus_data, status=status.HTTP_200_OK)
    


from decimal import Decimal

class ChairUpdateView(generics.UpdateAPIView):
    queryset = Chair.objects.all()
    lookup_field = 'uuid'
    serializer_class = ChairSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def patch(self, request, *args, **kwargs):
        chair_uuids = request.data.get('chair_uuids', [])
        if not chair_uuids:
            return Response({'message': 'Please provide UUIDs of the chairs to be reserved'})

        reservation = Reservation.objects.create(user=request.user)
        res = []
        for chair_uuid in chair_uuids:
            try:
                chair = self.queryset.get(uuid=chair_uuid)

                if chair.status == 'reserved':
                    res.append({
                        'chair_uuid': chair.uuid,
                        'chair_num': chair.number,
                        'trip_bus': f'{chair.bus_trip.trip.start_location}-{chair.bus_trip.trip.end_location}',
                        'trip_date': f'{chair.bus_trip.trip.start_date}',
                        'bus_num': f'{chair.bus_trip.vehicle_number}',
                        'status': 'error',
                        'message': 'The chair is already reserved.'
                    })
                    return Response({'reservations': res}, status=404)
                else:
                    reservation.add_chairs(chair.uuid)
                    reserve_serializer = ReservationSerializer(reservation, data=request.data, partial=True)
                    if reserve_serializer.is_valid():
                        reserve_serializer.save()
                        res.append({"reserve_client_detail":reserve_serializer.data})
                    else:
                        res.append(reserve_serializer.errors)
            except Chair.DoesNotExist:
                res.append({'message': 'The chair with UUID {} does not exist.'.format(chair_uuid)})

        return Response({'reservations': res})
class UserPaymentsView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user

        # Get all the payments associated with the user's reservations
        payments = Payment.objects.filter(reservation__user=user)

        # Compute the total cost of all payments
        total_cost = payments.aggregate(total=Sum('value'))['total'] or 0

        # Serialize the payments queryset
        serializer = PaymentSerializer(payments, many=True)

        # Return the serialized data with the total cost
        return Response({
            'payment': serializer.data,
            'total_cost': total_cost,
        })
def index(request):
    print(BASE_DIR)

    return render(request, 'base.html')
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
@csrf_exempt
@api_view(['GET'])
def check_reservation(request):
    barcode = request.data.get('barcode')
    if not barcode:
        return JsonResponse({'error': 'Barcode not provided','message':"make sure that barcode in body and its value"}, status=400)
    try:
        reservation = Reservation.objects.get(uuid=barcode)
        # Convert the reservation object to a dictionary
        context = ReservationSerializer(reservation).data
        return JsonResponse(context)
    except Reservation.DoesNotExist:
        return JsonResponse({'error': 'Reservation not found'}, status=404)



from django.contrib import messages 
from django.contrib.auth.models import User

class CancelReservationAPIView(APIView):
    def get(self, request,):
        try:
            # user = User.objects.get(username=request.user)
            reservations = Reservation.objects.filter(user=request.user)
            serializer = ReservationSerializer(reservations, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    def post(self, request, format=None):
        try:
            reservation_uuid = request.data.get('reservation_uuid')
            if not reservation_uuid:
                message = 'Reservation UUID is required. Example request: {"reservation_uuid": "xxxx-xxxx-xxxx-xxxx"}'
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            try:
                reservation = Reservation.objects.get(uuid=reservation_uuid)
            except Reservation.DoesNotExist:
                message = 'we have no reservation with this uuid {"reservation_uuid": "xxxx-xxxx-xxxx-xxxx"}'
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

            if not reservation:
                message = f'Reservation with UUID {reservation_uuid} not found'
                return Response({'error': message}, status=status.HTTP_404_NOT_FOUND)

            can_cancel, reason = reservation.can_cancel()
            if not can_cancel:
                message = f'Reservation with UUID {reservation_uuid} cannot be cancelled: {reason}.'
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            reservation.status = 'Cancelled'
            reservation.delete()

            message = f'Reservation with UUID {reservation_uuid} has been cancelled'
            return Response({'success': message}, status=status.HTTP_200_OK)

        except TypeError:
            message = 'Invalid request body. Please provide the reservation UUID in the request body in the following format: {"reservation_uuid": "xxxx-xxxx-xxxx-xxxx"}'
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        
class DeleteChairFromReservationAPIView(APIView):
    permission_classes = [IsAuthenticated | IsAdminUser]

    def post(self, request, format=None):
        try:
            reservation_uuid = request.data.get('reservation_uuid')
            chair_uuid = request.data.get('chair_uuid')

            if not reservation_uuid or not chair_uuid:
                message = 'Reservation UUID and chair number are required. Example request: {"reservation_uuid": "xxxx-xxxx-xxxx-xxxx", "chair_uuid": 42}'
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # print(Reservation.objects.filter(user=request.user).values())
                reservation = Reservation.objects.get(uuid=reservation_uuid)
                # print(reservation)
            except Reservation.DoesNotExist:
                message = f'Reservation with UUID {reservation_uuid} not found'
                return Response({'error': message}, status=status.HTTP_404_NOT_FOUND)

            try:
                chair = Chair.objects.get(uuid=chair_uuid)
                print(chair)
            except Chair.DoesNotExist:
                message = f'Chair with number {chair_uuid} not found'
                return Response({'error': message}, status=status.HTTP_404_NOT_FOUND)
            print([chair['uuid'] for chair in reservation.chairs.values()])
            if chair.uuid not in [chair['uuid'] for chair in reservation.chairs.values()] :
                message = f'Chair with number {chair_uuid} is not associated with reservation {reservation_uuid}'
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            try:
                reservation.chairs.remove(chair) 
                reservation.save()
            except:
                message = f'Chair with number {chair_uuid} has not  been removed from reservation {reservation_uuid} '
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

            try:
                chair.status = 'available'
                chair.save()
            except:
                message = f'Chair status does not changed {chair_uuid} has not  been removed from reservation {reservation_uuid} '
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ReservationSerializer(reservation)
            message = f'Chair with number {chair_uuid} has been removed from reservation {reservation_uuid} and is now available'
            return Response({'success': message, 'reservation': serializer.data}, status=status.HTTP_200_OK)

        except TypeError:
            message = 'Invalid request body. Please provide the reservation UUID and chair number in the request body in the following format: {"reservation_uuid": "xxxx-xxxx-xxxx-xxxx", "chair_uuid": 42}'
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
class All_reservation(APIView):
    def get(self, request,):
        try:
            # user = User.objects.get(username=request.user)
            reservations = Reservation.objects.filter(user=request.user)
            serializer = ReservationSerializer(reservations, many=True)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


from.forms import ChooseStationForm, CreateTripForm, ReviewTripForm

def create_trip(request):
    if request.method == 'POST':
        form = CreateTripForm(request.POST)
        if form.is_valid():
            # print(2)
            trip = form.save()

            return redirect('choose_station', trip_id=trip.id)
        if form.errors:
            print(form.errors)
    else:
        form = CreateTripForm()
    
    return render(request, 'trip/create_trip.html', {'form': form})

def choose_station(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    if request.method == 'POST':
        form = ChooseStationForm(request.POST)
        if form.is_valid():
            trip.start_station = form.cleaned_data['start_station']
            trip.end_station = form.cleaned_data['end_station']
            trip.save()
            print(1)
            return redirect('review_trip', trip_id=trip.id)
    else:
        form = ChooseStationForm(initial={'start_station': trip.start_station, 'end_station': trip.end_station})
    return render(request, 'trip/choose_stations.html', {'form': form, 'trip': trip})

def review_trip(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    if request.method == 'POST':
        form = ReviewTripForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            return redirect('trip_detail', trip_id=trip.id)
    else:
        form = ReviewTripForm(instance=trip)
    return render(request, 'trip/review_trip.html', {'form': form, 'trip': trip})

def trip_detail(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    return render(request, 'trip/trip_detail.html', {'trip': trip})