from django.contrib import admin
from .models import Location, BusCompany, Station, SalonType, ChairType, Bus, Chair, Trip, Reservation, Payment, TripStop

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)

class BusCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'address', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'email', 'phone_number', 'address')

class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'location')
    search_fields = ('name', 'address')

class SalonTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class ChairTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    search_fields = ('name',)

class ChairInline(admin.TabularInline):
    model = Chair
    # extra = 0
    extra = 40

class BusAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_station', 'destination', 'vehicle_number', 'vehicle_type')
    list_filter = ('start_station', 'destination', 'vehicle_type')
    search_fields = ('name', 'vehicle_number')
    inlines = [ChairInline]

class TripStopInline(admin.TabularInline):
    model = TripStop
class TripAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'bus', 'start_location', 'arrival_time', 'is_active','get_reserved_chairs')
    list_filter = ('start_location', 'bus',)
    search_fields = ('bus__name', 'start_location__name', 'passing_locations__name')
    inlines = [TripStopInline]


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('chair', 'user', 'reserved_at', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'chair__bus__name', 'chair__number')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'value', 'status')
    list_filter = ('status',)
    search_fields = ('reservation__chair__bus__name', 'reservation__user__username')

admin.site.register(Location, LocationAdmin)
admin.site.register(BusCompany, BusCompanyAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(SalonType, SalonTypeAdmin)
admin.site.register(ChairType, ChairTypeAdmin)  
admin.site.register(Bus, BusAdmin)
admin.site.register(Trip, TripAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Payment, PaymentAdmin)