# Generated by Django 3.2.19 on 2023-08-17 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0020_roadmapitem_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='roadmapitem',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
