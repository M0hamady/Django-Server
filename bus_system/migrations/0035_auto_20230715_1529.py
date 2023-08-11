# Generated by Django 3.2.19 on 2023-07-15 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_system', '0034_auto_20230715_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='value',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='start_time',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
