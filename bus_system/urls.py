from django.urls import path
from .views import BusInTripAPI, CancelReservationAPIView, ChairUpdateView, LocationStationList, TripList, UserPaymentsView, check_reservation, index

urlpatterns = [
    path('', index, name='index'),
    path('locations/', LocationStationList.as_view(), name='location-station-list'),
    path('trips/', TripList.as_view(), name='trip-list'),
    path('bus-in-trip/', BusInTripAPI.as_view(), name='bus-in-trip-api'),
    path('chairs/reserve/', ChairUpdateView.as_view(), name='reserve_chairs'),
    path('payments/', UserPaymentsView.as_view(), name='user_payments'),
    path('check_reservation/', check_reservation, name='check_reservation'),
    path('reservation/cancel/', CancelReservationAPIView.as_view(), name='cancel_reservation'),    # other URL patterns for your project
]