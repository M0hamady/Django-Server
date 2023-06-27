from datetime import timedelta, datetime
import datetime as date_time
from django.utils import timezone
from multiselectfield import MultiSelectField
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.core.validators import MinValueValidator,MaxValueValidator
import uuid
from django.db.models import Count


tz = timezone.utc

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    @property
    def location_lat(self):
        if self.latitude ==None :
            return "00.00"
    @property
    def Location_long(self):
        if self.longitude == None :
            return "00.00"
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    # def clean(self):
    #     # validate uniqueness of vehicle_number
    #     if Bus.objects.exclude(id=self.id).filter(vehicle_number=self.vehicle_number).exists():
    #         raise ValidationError({'vehicle_number': 'Vehicle number must be unique.'})

class BusCompany(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)

class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='stations')
    buses = models.ManyToManyField('Bus', related_name='stations',blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,null=True,blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,null=True,blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return self.name
    
    # @property
    def station_lat(self):
        if self.latitude ==None:
            return "00.00"
    # @property
    def station_long(self):
        if self.longitude ==None:
            return "00.00"
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)

class SalonType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
class ChairType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
class Bus(models.Model):
    name = models.CharField(max_length=100, unique=True,default='bus')
    start_station = models.ForeignKey(Station, on_delete=models.SET_NULL,null=True,blank=True ,related_name='starting_buses')
    passing_stations = models.ManyToManyField(Station, related_name='passing_buses',blank=True)
    destination = models.ForeignKey(Station, on_delete=models.SET_NULL,null=True,blank=True, related_name='destination_buses')
    salon_type = models.ForeignKey(SalonType, on_delete=models.CASCADE)
    number_of_chairs = models.PositiveIntegerField()
    price_per_chair = models.DecimalField(max_digits=8, decimal_places=2,blank=True)
    # chairs = models.ManyToManyField('Chair', related_name='buses',blank=True)
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=50)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return self.name + self.vehicle_number

    def pending_chairs(self):
        return self.bus_chairs.filter(status='Pending')
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
    def reserved_chairs(self):
        return Chair.objects.filter(status='Reserved').count()
    @property
    def reserved_chairs_count(self):
        return Chair.objects.filter(status='booked').count()
    
    @property
    def bus_salon(self):
        if not self.salon_type:
            return 'economy'
        return self.salon_type
    @property
    def unreserved_chairs(self):
        chairs = Chair.objects.filter(bus=self,status='available')
        # .annotate(num_reservations=Count('reservation'))
        chair_data = []
        for chair in chairs:
            chair_data.append({
                'id': chair.id,
                'number': chair.number,
                'type': chair.chair_type.name,
                'price_per_chair': str(chair.price_per_chair),
                'uuid': chair.uuid,
            })
        return chair_data

class Chair(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bus_chairs')
    number = models.PositiveIntegerField()
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('booked', 'Booked'),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available')
    chair_type = models.ForeignKey(ChairType, on_delete=models.CASCADE,default=1)
    price_per_chair = models.DecimalField(max_digits=8, decimal_places=2,null=True,blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        unique_together = ('bus', 'number')

    def __str__(self):
        return f"{self.bus} - Chair {self.number}"
    def is_reserved(self):
        return self.reservations.filter(status='booked').exists()

    def payment_status(self):
        latest_reservation = self.reservations.order_by('-reserved_at').first()
        if latest_reservation is None:
            return None, None
        payment = latest_reservation.payment
        return  payment.status
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        if not self.price_per_chair:
            self.price_per_chair= self.bus.price_per_chair 
        super().save(*args, **kwargs)
    def payment_value(self):
        latest_reservation = self.reservations.order_by('-reserved_at').first()
        if latest_reservation is None:
            return None, None
        payment = latest_reservation.payment
        return payment.value
def get_trip_stops(trip, fixed_time, week_start):
    """
    Returns a list of TripStop objects for the given trip, as well as
    a fixed datetime object representing the time of day the bus departs
    for the trip on all days in a given week.

    The fixed_time parameter should be a datetime.time object representing
    the time of day the bus departs for the trip.

    The week_start parameter should be a date object representing the first
    day of the week for which trip stops should be returned.
    """
    trip_stops = list(trip.tripstop_set.all())
    time_delta = timedelta(hours=fixed_time.hour, minutes=fixed_time.minute)

    for stop in trip_stops:
        stop.arrival_time += time_delta
        stop.departure_time += time_delta

    # Get the date of the next day with the same weekday as week_start
    now = datetime.now()
    weekday = week_start.weekday()
    next_weekday = (weekday - now.weekday()) % 7
    next_day = now + timedelta(days=next_weekday)

    # Calculate the datetime of the next trip departure time
    next_departure_time = datetime.combine(next_day.date(), fixed_time)
    if next_departure_time < now:
        next_departure_time += timedelta(days=7)

    # Add trip stops to the list if they occur after the next trip departure time
    future_trip_stops = []
    for stop in trip_stops:
        if stop.departure_time >= next_departure_time + timedelta(minutes=30):
            future_trip_stops.append(stop)

    return future_trip_stops, next_departure_time
        
        
class Trip(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Pending', 'Pending'),
    ]

    start_date = models.DateField(null=True,blank=True)
    # uniq = models.u
    start_time = models.TimeField()
    arrival_time = models.DateTimeField()
    DAY_CHOICES = (
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    )
    day_of_week = MultiSelectField(choices=DAY_CHOICES)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='trips')
    start_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='starting_trips')
    end_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='ending_trips')
    distance = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(9)], default=10)
    duration = models.DurationField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return f"{self.start_time} - {self.bus} - {self.start_location} to {self.end_location}"

    def get_buses(self):
        return [self.bus] + list(self.end_location.stations.filter(buses=self.bus))

    def is_active(self):
        return False

    def get_reserved_chairs(self):
        reserved_chairs = self.bus.reserved_chairs_count
        return reserved_chairs
    
    def get_available_chairs(self):
        reserved_chairs = self.bus.unreserved_chairs
        return reserved_chairs
    

    def get_reserved_chairs_with_payments(self):
        reserved_chairs = self.bus.chairs.filter(reservation__status=Reservation.RESERVED, reservation__trip=self)
        total_payments = reserved_chairs.aggregate(total=models.Sum('reservation__payment__value'))['total']
        return total_payments

    def stops(self):
        return self.tripstop_set.order_by('arrival_time')
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
    @classmethod
    def get_available_trips(cls, start_location, end_location, travel_date):
        now = date_time.datetime.now().time()
        half_hour_later = (date_time.datetime.now() + date_time.timedelta(minutes=30)).time()
        trips = cls.objects.filter(
            start_location=start_location,
            end_location=end_location,
            start_date=travel_date
        )
        print(trips,start_location,end_location,travel_date)
        available_trips = []
        for trip in trips:
            available_trips.append(trip)
        #     trip_stops = trip.tripstop_set.filter(
        #         arrival_time__gte=date_time.time(hour=9, minute=0),
        #         departure_time__lte=date_time.time(23, 59, 59),  # optional: limit end time to midnight
        #     ).order_by('arrival_time')
        #     if trip_stops:
        #         next_departure_time = trip_stops[0].departure_time
        #         if next_departure_time.time() >= now and next_departure_time.date() == travel_date:
        #             available_trips.append((trip, next_departure_time))
        return available_trips
from django.core.exceptions import ValidationError

class TripStop(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    arrival_time = models.DateTimeField()
    departure_time = models.TimeField()
    duration = models.DurationField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
    def clean(self):
        pass
        # if self.arrival_time >= self.departure_time:
        #     raise ValidationError('Arrival time must be before departure time.')
        # if self.duration != self.departure_time - self.arrival_time:
        #     raise ValidationError('Duration must be equal to the difference between arrival and departure times.')
class Reservation(models.Model):
    STATUS_CHOICES = [
        ('Reserved', 'Reserved'),
        ('Cancelled', 'Cancelled'),
        ('Expired', 'Expired')
    ]

    chair = models.ForeignKey(Chair, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    reserved_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Reserved')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return f"{self.chair} - {self.status}"

    def can_cancel(self):
        now = timezone.now()
        return self.status == 'Reserved' and (self.reserved_at + timedelta(hours=4)) > now
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Done', 'Done'),
    ]

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='payment')
    value = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return f"{self.reservation} - {self.status}"
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)


class TripSchedule(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.TimeField()
    travel_date = models.DateField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    class Meta:
        unique_together = ('trip', 'travel_date', 'departure_time')
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)