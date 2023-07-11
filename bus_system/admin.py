from django.contrib import admin
from .models import BusTrip, Location, BusCompany, PaymentMethod, Station, SalonType, ChairType, Bus, Chair, Trip, Reservation, Payment, TripStop, Trips_data

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
    fields = ['number','status','price_per_chair']
    readonly_fields = ['uuid','bus','bus_trip']
    extra = 0

class BusAdmin(admin.ModelAdmin):
    list_display = ('name',  'vehicle_number', 'vehicle_type')
    list_filter = ('vehicle_type',)
    search_fields = ('name', 'vehicle_number')
    inlines = [ChairInline]

class TripStopInline(admin.TabularInline):
    model = TripStop
class TripBusInline(admin.TabularInline):
    model = BusTrip
    extra = 0
class TripAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'bus','start_location', 'arrival_time', 'is_active',)
    list_filter = ('start_location', 'bus',)
    search_fields = ('bus__name', 'start_location__name', 'passing_locations__name')
    inlines = [TripStopInline,TripBusInline]


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('chair', 'user','start_time', 'reserved_at', 'status', 'payment_fee', 'commission', 'total_cost')
    list_filter = ('status',)
    search_fields = ('user__username', 'chair__bus__name', 'chair__number')

    def payment_fee(self, obj):
        return obj.payment.payment_fee

    def commission(self, obj):
        return obj.payment.commission

    def total_cost(self, obj):
        return obj.chair.price_per_chair + obj.payment.payment_fee + obj.payment.commission

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'value', 'status', 'payment_fee', 'commission')
    list_filter = ('status',)
    search_fields = ('reservation__chair__bus__name', 'reservation__user__username')

    def payment_fee(self, obj):
        return obj.payment_fee

    def commission(self, obj):
        return obj.commission
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'payment_fee')

admin.site.register(PaymentMethod, PaymentMethodAdmin)

admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Trips_data)
admin.site.register(BusCompany, BusCompanyAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(SalonType, SalonTypeAdmin)
admin.site.register(ChairType, ChairTypeAdmin)  
admin.site.register(Bus, BusAdmin)
admin.site.register(BusTrip, BusAdmin)
admin.site.register(Trip, TripAdmin)