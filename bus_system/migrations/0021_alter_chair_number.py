# Generated by Django 3.2.19 on 2023-06-29 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_system', '0020_alter_chair_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chair',
            name='number',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]
