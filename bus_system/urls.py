from django.urls import path
from .views import All_reservation, BusInTripAPI, CancelReservationAPIView, ChairUpdateView, DeleteChairFromReservationAPIView, LocationStationList, TripList, UserPaymentsView, check_reservation, choose_station, create_trip, index, review_trip, trip_detail

urlpatterns = [
    path('', index, name='index'),
    path('locations/', LocationStationList.as_view(), name='location-station-list'),
    path('trips/', TripList.as_view(), name='trip-list'),
    path('bus-in-trip/', BusInTripAPI.as_view(), name='bus-in-trip-api'),
    path('chairs/reserve/', ChairUpdateView.as_view(), name='reserve_chairs'),
    path('payments/', UserPaymentsView.as_view(), name='user_payments'),
    path('check_reservation/', check_reservation, name='check_reservation'),
    path('reservation/cancel/', CancelReservationAPIView.as_view(), name='cancel_reservation'),
    path('reservation/chair/cancel/', DeleteChairFromReservationAPIView.as_view(), name='cancel_reservation'),
    path('reservation/all/', All_reservation.as_view(), name='all_reservation'),
    path('create_trip/', create_trip, name='create_trip'),
    path('choose_station/<int:trip_id>/', choose_station, name='choose_station'),
    path('review_trip/<int:trip_id>/', review_trip, name='review_trip'),
    path('trip/<int:trip_id>/', trip_detail, name='trip_detail'),    # other URL patterns for your project
]