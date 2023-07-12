from datetime import datetime
from decimal import Decimal
import os
import timedelta
import datetime as date_time
from django.utils import timezone
from multiselectfield import MultiSelectField
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.core.validators import MinValueValidator,MaxValueValidator
import uuid
from django.db.models import Count
import barcode
from barcode.writer import ImageWriter
from django.db.models.signals import post_save
from django.dispatch import receiver
from main import settings

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
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

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
    name = models.CharField(max_length=100, unique=False)
    description = models.CharField(max_length=200,null=True,blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
class Bus(models.Model):
    name = models.CharField(max_length=100, unique=False,default='bus')
    salon_type = models.ForeignKey(SalonType, on_delete=models.SET_NULL,null=True,related_name='bus_sallon',blank=True)
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
        if  self.number_of_chairs !=0 and self.number_of_chairs > Chair.objects.filter(bus=self).count():
            # num_add_chairs= self.number_of_chairs - self.chairs.count()
            for each_chair in range(self.number_of_chairs):
                chair = Chair.objects.create(
                    number = each_chair+1,
                    bus= self,
                    price_per_chair = self.price_per_chair

                )
                chair.save()
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
class BusTrip(models.Model):
    name = models.CharField(max_length=100, unique=False,default='bus')
    salon_type = models.ForeignKey(SalonType, on_delete=models.CASCADE,related_name='bus_trip_salon')
    number_of_chairs = models.PositiveIntegerField()
    price_per_chair = models.DecimalField(max_digits=8, decimal_places=2,blank=True)
    # chairs = models.ManyToManyField('Chair', related_name='buses',blank=True)
    vehicle_number = models.CharField(max_length=20, unique=False,)
    vehicle_type = models.CharField(max_length=50)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=False)
    trip = models.ForeignKey('Trip',on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self):
        return self.name + self.vehicle_number

    def pending_chairs(self):
        return self.bus_chairs.filter(status='Pending')
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
        if  self.number_of_chairs !=0 and self.number_of_chairs > Chair.objects.filter(bus_trip=self).count():
            # num_add_chairs= self.number_of_chairs - self.chairs.count()
            for each_chair in range(self.number_of_chairs):
                chair = Chair.objects.create(
                    number = each_chair+1,
                    bus_trip= self,
                    price_per_chair = self.price_per_chair

                )
                chair.save()
        super().save(*args, **kwargs)
        
        
    def reserved_chairs(self):
        return Chair.objects.filter(status='Reserved').count()
    def reserved_chairs_count(self):
        return Chair.objects.filter(status='booked').count()
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
        chairs = Chair.objects.filter(bus_trip=self,status='available')
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
def create_bust_rip(salon_type, number_of_chairs, price_per_chair, vehicle_number, vehicle_type,trip):
    bustrip = BusTrip(
        salon_type=salon_type,
        number_of_chairs=number_of_chairs,
        price_per_chair=price_per_chair,
        vehicle_number=vehicle_number,
        vehicle_type=vehicle_type,
        trip=trip,
    )
    bustrip.save()
    return bustrip
class Chair(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, related_name='bus_chairs',null=True,blank=True )
    bus_trip = models.ForeignKey(BusTrip, on_delete=models.SET_NULL, related_name='bus_chairs_trip',null=True,blank=True )
    number = models.CharField(max_length=12,null=True,blank=True)
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
    @property
    def busTrip_uuid(self):
        return self.bus_trip.uuid
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
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'),
        ('7', 'Sunday'),
    )
    day_of_week = models.CharField(max_length=150,choices=DAY_CHOICES)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL,null=True, related_name='trips')
    start_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='starting_trips')
    end_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='ending_trips')
    distance = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(9)], default=10)
    duration = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    trip_rel_with_data = models.ForeignKey('Trips_data',on_delete=models.SET_NULL,null=True,blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return f"{self.start_time} - {self.bus} - {self.start_location} to {self.end_location}"
    
    def get_buses(self):
        return [self.bus_trip] + list(self.end_location.stations.filter(buses=self.bus))
    @property
    def get_start_datetime(self):
        arrival_datetime = self.arrival_time
        tz = arrival_datetime.tzinfo
        start_datetime = timezone.make_aware(datetime.combine(self.start_date, self.start_time), tz)
        start_datetime += arrival_datetime - datetime.combine(arrival_datetime.astimezone(tz).date(), arrival_datetime.astimezone(tz).time(), tz)
        return start_datetime
    def is_active(self):
        return False
    def buses_trip (self):
        return BusTrip.objects.get(trip = self)
    def get_reserved_chairs(self):
        reserved_chairs = self.bus_trip.reserved_chairs_count
        return reserved_chairs
    
    def get_available_chairs(self):
        reserved_chairs = BusTrip.objects.get(trip =self).unreserved_chairs

        return reserved_chairs
    
    def bus_trip_chairs(self):
        return BusTrip.objects.get(trip= self).number_of_chairs

    def get_reserved_chairs_with_payments(self):
        reserved_chairs = self.bus_trip.chairs.filter(reservation__status=Reservation.RESERVED, reservation__trip=self)
        total_payments = reserved_chairs.aggregate(total=models.Sum('reservation__payment__value'))['total']
        return total_payments

    def stops(self):
        return self.tripstop_set.order_by('arrival_time')
    
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
        # self.create_bus_trip()
        if self.bus:
           create_bust_rip(self.bus.salon_type,
                        self.bus.number_of_chairs,
                        self.bus.price_per_chair,
                        self.bus.vehicle_number,
                        self.bus.vehicle_type,
                        trip=self)
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
def add_hours(date_str,time_str, hours_to_add):
    # Split the time string into its components
    h, m, s = map(int, time_str.split(':'))

    # Add the number of hours to the hours component
    h += hours_to_add

    # Calculate the number of days to add (if any)
    days_to_add, h = divmod(h, 24)

    # Format the result as a string and return it
    # 
    return f'{h:02d}:{m:02d}:{s:02d}'
def create_trip(start_date, start_time, arrival_time, day_of_week, bus, start_location, end_location, duration):
    trip = Trip(
        start_date=start_date,
        start_time=start_time,
        arrival_time=arrival_time,
        day_of_week=day_of_week,
        bus=bus,
        start_location=start_location,
        end_location=end_location,
        duration=duration,
    )
    
    trip.save()
    return trip
class Trips_data(models.Model):
    start_date = models.DateField()
    at_time  = models.TimeField()
    end_date = models.DateField()
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
    bus = models.ForeignKey(Bus,related_name='buses',blank=True,on_delete=models.SET_NULL,null=True)
    from_location = models.ForeignKey(Location,default=1,on_delete=models.CASCADE,related_name='trips_data_location_from')
    to_location = models.ForeignKey(Location,default=1,on_delete=models.CASCADE,related_name='trips_data_location_to')
    duration_of_trip = models.PositiveIntegerField()
    uuid = models.UUIDField(blank=True)
    def __str__(self):
        return 'Trip: from: ' +f'{self.start_date}'+f' to:{self.end_date}'
    def generate_trips(self):
        trip_date = self.start_date 
       
        while trip_date <= self.end_date :
            if str(trip_date.weekday()) in self.day_of_week :
                trip_start_time = self.at_time
                trip_arrival_time =add_hours(trip_date,str(trip_start_time), self.duration_of_trip) 
                trip_duration = self.duration_of_trip
                create_trip(trip_date,trip_arrival_time,trip_date,str(trip_date.weekday()),
                            self.bus,self.from_location,self.to_location,
                            self.duration_of_trip)
                
            trip_date =trip_date +  timedelta.Timedelta(days=1)
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
        self.generate_trips()
    
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
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, unique=True)
    payment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return self.name

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('Reserved', 'Reserved'),
        ('Cancelled', 'Cancelled'),
        ('Expired', 'Expired')
    ]
    start_time = models.DateTimeField(null=True,blank=True)

    chair = models.ForeignKey(Chair, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    reserved_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Reserved')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL,null=True, related_name='reservations')
    payment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    barcode = models.ImageField(upload_to='./media/barcodes/', blank=True, null=True)
    # def __str__(self):
    #     return f"{self.chair} - {self.status}"
    # @property
    
    @property
    def company_commission(self):
        print(PaymentMethod.objects.first().payment_fee)
        return BusCompany.objects.get(id=1).commission
    def save(self, *args, **kwargs):
        # Combine start_date and start_time into a single datetime object
        start_datetime = datetime.combine(self.chair.bus_trip.trip.start_date, self.chair.bus_trip.trip.start_time)
        # Set reservation start time to be the combined datetime object + the chair's start time
        self.start_time = start_datetime 
        if not self.pk:
            # Set the default payment method if no payment method is specified
            if not self.payment_method:
                self.payment_method = PaymentMethod.objects.first()
                self.payment_fee =PaymentMethod.objects.first().payment_fee
                EAN = barcode.get_barcode_class('code128')
                ean = EAN(str(self.uuid), writer=ImageWriter())
                filename = f"reservation_{self.uuid}.png"
                barcode_path = os.path.join('reservations', 'barcode', self.user.username, filename)
                barcode_full_path = os.path.join(settings.MEDIA_ROOT, barcode_path)
                os.makedirs(os.path.dirname(barcode_full_path), exist_ok=True)
                ean.save(barcode_full_path)
                self.barcode.name = barcode_path

        super().save(*args, **kwargs)
    def can_cancel(self):
        now = timezone.now()
        if self.start_time:
            cancellation_deadline = self.start_time - timedelta.Timedelta(hours=4)
            try:
                print(now-timedelta.Timedelta(hours = 4) <= self.start_time,self.status == 'Reserved')
                if now-timedelta.Timedelta(hours = 4) <= self.start_time and self.status == 'Reserved':
                    print(1)
                    return True, ''
                else:
                    return False, f'Reservations cannot be cancelled less than 4 hours before the scheduled start time. The cancellation deadline for this reservation is {cancellation_deadline}.'
            except:return False, f'Reservations cancel can not be display while creation,  check for it after creation'
        else:
            return False, f'Reservations cannot be cancelled with no  scheduled start time. try to create new reservation to insure of err.'
            
    def delete(self, *args, **kwargs):
        # delete the payment when the reservation is cancelled
        self.chair.status = 'available'
        self.chair.save()
        if self.status == 'Cancelled' and hasattr(self, 'payment'):
            self.payment.delete()

        # update the corresponding chair's status
        

        super().delete(*args, **kwargs)
@receiver(post_save, sender=Reservation)
def update_chair_status(sender, instance, **kwargs):
    # update the corresponding chair's status when the reservation status is changed
    if instance.status == 'Reserved':
        instance.chair.status = 'reserved'
        instance.chair.save()
    elif instance.status == 'Cancelled':
        instance.chair.status = 'available'
        instance.chair.save()

    
    # def __str__(self):
    #     return f"{self.user.username} - {self.chair.bus.name} - {self.chair.number}"
class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Done', 'Done'),
    ]

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='payment')
    value = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    payment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.reservation} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()

        # Calculate the payment fee based on the reservation payment method and any applicable fees
        self.payment_fee = self.reservation.payment_method.payment_fee

        # Calculate the commission based on the payment fee and the bus company commission rate
        commission_rate = BusCompany.objects.get(id=1).commission
        self.commission =  commission_rate

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