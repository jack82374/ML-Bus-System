# Generated by Django 5.1.5 on 2025-02-17 20:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0006_alter_stoptimes_arrival_time_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArchiveStopUpdate",
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
                ("stop_sequence", models.IntegerField()),
                ("arrival_time", models.IntegerField()),
                ("arrival_uncertainty", models.IntegerField()),
                ("arrival_delay", models.IntegerField()),
                ("departure_delay", models.IntegerField()),
                ("schedule_relationship", models.CharField(max_length=255)),
                (
                    "stop_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="website.stops",
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT, to="website.trips"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArchiveTripUpdate",
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
                ("start_time", models.IntegerField()),
                ("start_date", models.IntegerField()),
                ("schedule_relationship", models.CharField(max_length=255)),
                ("direction_id", models.SmallIntegerField()),
                ("vehicle_id", models.IntegerField(blank=True, null=True)),
                ("timestamp", models.DateTimeField()),
                (
                    "route",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="website.routes",
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="website.trips",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArchiveVehiclePosition",
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
                ("start_time", models.IntegerField()),
                ("start_date", models.IntegerField()),
                ("schedule_relationship", models.CharField(max_length=255)),
                ("direction_id", models.SmallIntegerField()),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("timestamp", models.DateTimeField()),
                ("vehicle_id", models.IntegerField()),
                (
                    "route",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="website.routes",
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="website.trips",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StopUpdate",
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
                ("stop_sequence", models.IntegerField()),
                ("arrival_time", models.IntegerField()),
                ("arrival_uncertainty", models.IntegerField()),
                ("arrival_delay", models.IntegerField()),
                ("departure_delay", models.IntegerField()),
                ("schedule_relationship", models.CharField(max_length=255)),
                (
                    "stop_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="website.stops"
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="website.trips"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TripUpdate",
            fields=[
                (
                    "trip",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="website.trips",
                    ),
                ),
                ("start_time", models.IntegerField()),
                ("start_date", models.IntegerField()),
                ("schedule_relationship", models.CharField(max_length=255)),
                ("direction_id", models.SmallIntegerField()),
                ("vehicle_id", models.IntegerField(blank=True, null=True)),
                ("timestamp", models.DateTimeField()),
                (
                    "route",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="website.routes"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="VehiclePosition",
            fields=[
                (
                    "trip",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="website.trips",
                    ),
                ),
                ("start_time", models.IntegerField()),
                ("start_date", models.IntegerField()),
                ("schedule_relationship", models.CharField(max_length=255)),
                ("direction_id", models.SmallIntegerField()),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("timestamp", models.DateTimeField()),
                ("vehicle_id", models.IntegerField(blank=True, null=True)),
                (
                    "route",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="website.routes"
                    ),
                ),
            ],
        ),
    ]
