from django.urls import path
from .views import BusInTripAPI, LocationStationList, TripList, index

urlpatterns = [
     path('', index, name='index'),
    path('locations/', LocationStationList.as_view(), name='location-station-list'),
     path('trips/', TripList.as_view(), name='trip-list'),
     path('bus-in-trip/', BusInTripAPI.as_view(), name='bus-in-trip-api'),
    # other URL patterns for your project
]