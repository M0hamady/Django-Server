# Generated by Django 3.2.19 on 2023-07-15 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_system', '0033_reservation_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='chair',
        ),
        migrations.RemoveField(
            model_name='tripstop',
            name='departure_time',
        ),
        migrations.RemoveField(
            model_name='tripstop',
            name='duration',
        ),
        migrations.AddField(
            model_name='reservation',
            name='chairs',
            field=models.ManyToManyField(related_name='reservations', to='bus_system.Chair'),
        ),
    ]
