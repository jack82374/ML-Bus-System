# Generated by Django 5.1.5 on 2025-03-26 17:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0016_alter_calendardates_service_alter_routes_agency_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="NextDelay",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("delay", models.FloatField()),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="website.trips"
                    ),
                ),
            ],
        ),
    ]
