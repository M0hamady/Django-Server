# Generated by Django 3.2.19 on 2023-06-29 15:30

from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bus_system', '0016_auto_20230625_2214'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='chairs',
            field=models.ManyToManyField(blank=True, related_name='buses', to='bus_system.Chair'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='name',
            field=models.CharField(default='bus', max_length=100),
        ),
        migrations.AlterField(
            model_name='chairtype',
            name='description',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='chairtype',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='trip',
            name='arrival_time',
            field=models.DateField(),
        ),
        migrations.CreateModel(
            name='Trips_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('at_time', models.TimeField()),
                ('end_date', models.DateField()),
                ('day_of_week', multiselectfield.db.fields.MultiSelectField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], max_length=13)),
                ('duration_of_trip', models.PositiveIntegerField()),
                ('uuid', models.UUIDField(blank=True)),
                ('bus', models.ManyToManyField(to='bus_system.Bus')),
                ('from_location', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='trips_data_location_from', to='bus_system.location')),
                ('to_location', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='trips_data_location_to', to='bus_system.location')),
            ],
        ),
        migrations.AddField(
            model_name='trip',
            name='trip_rel_with_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bus_system.trips_data'),
        ),
    ]
