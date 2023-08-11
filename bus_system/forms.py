# forms.py

from django import forms
from.models import Trip,Trips_data

class CreateTripForm(forms.ModelForm):
    class Meta:
        model = Trips_data
        fields = ['start_date', 'at_time', 'end_date', 'day_of_week', 'bus', 'from_location', 'to_location', 'duration_of_trip']
    def __init__(self, *args, **kwargs):
        WEEK_DAYS = (
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'),
        ('7', 'Sunday'),
    )
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs.update({'type': 'date','class': 'inputField','style_name':'date','id':'date','placeholder':"YYYY-MM-DD"})
        self.fields['at_time'].widget.attrs.update({'class': 'inputField', 'style_name':'time','type': 'time','id':'time'})
        self.fields['end_date'].widget.attrs.update({'class': 'inputField', 'style_name':'date','type': 'time'})
        self.fields['day_of_week'].widget = forms.SelectMultiple(choices=WEEK_DAYS, attrs={'class': 'inputField', 'tyle': 'width: 200px;'})
        self.fields['bus'].widget.attrs.update({'class': 'inputField', 'style': 'width: 200px;'})
        self.fields['from_location'].widget.attrs.update({'class': 'inputField', 'style': 'width: 200px;'})
        self.fields['to_location'].widget.attrs.update({'class': 'inputField', 'style': 'width: 200px;'})
        self.fields['duration_of_trip'].widget.attrs.update({'class': 'inputField', 'style': 'width: 200px;'})

class ChooseStationForm(forms.Form):
    start_station = forms.ChoiceField(choices=[('Station 1', 'Station 1'), ('Station 2', 'Station 2'), ('Station 3', 'Station 3'), ('Station 4', 'Station 4')])
    end_station = forms.ChoiceField(choices=[('Station 1', 'Station 1'), ('Station 2', 'Station 2'), ('Station 3', 'Station 3'), ('Station 4', 'Station 4')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_station'].widget.attrs.update({'class': 'form-control', 'style': 'width: 200px;'})
        self.fields['end_station'].widget.attrs.update({'class': 'form-control', 'style': 'width: 200px;'})

class ReviewTripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['start_date', 'start_time', 'arrival_time', 'day_of_week', 'bus', 'start_location', 'end_location', 'duration', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs.update({'class': 'form-control','id':'dateofbirth', 'type': 'date','name':'dateofbirth', 'readonly': True})
        self.fields['start_time'].widget.attrs.update({'class': 'form-control', 'type': 'time', 'readonly': True})
        self.fields['arrival_time'].widget.attrs.update({'class': 'form-control', 'type': 'time', 'readonly': True})
        self.fields['day_of_week'].widget.attrs.update({'class': 'form-control', 'style': 'width: 200px;', 'readonly': True})
        self.fields['bus'].widget.attrs.update({'class': 'form-control', 'style': 'width: 200px;', 'readonly': True})
        self.fields['start_location'].widget.attrs.update({'class': 'form-control', 'style': 'width: 200px;', 'readonly': True})
        self.fields['end_location'].widget.attrs.update({'class': 'form-control', 'style': 'width: 200px;', 'readonly': True})
        self.fields['duration'].widget.attrs.update({'class': 'form-control', 'style': 'width: 200px;', 'readonly': True})
        self.fields['start_station'].widget.attrs.update({'class': 'form-control', 'style': 'width: 200'})