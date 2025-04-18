# Generated by Django 5.1.5 on 2025-02-23 20:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0010_archivetripupdate_day_tripupdate_day"),
    ]

    operations = [
        migrations.AlterField(
            model_name="archivestopupdate",
            name="stop_id",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="website.stops",
            ),
        ),
        migrations.AlterField(
            model_name="archivestopupdate",
            name="trip",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="website.trips",
            ),
        ),
        migrations.AlterField(
            model_name="archivetripupdate",
            name="route",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="website.routes",
            ),
        ),
        migrations.AlterField(
            model_name="archivetripupdate",
            name="trip",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="website.trips",
            ),
        ),
        migrations.AlterField(
            model_name="archivevehicleposition",
            name="route",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="website.routes",
            ),
        ),
        migrations.AlterField(
            model_name="archivevehicleposition",
            name="trip",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="website.trips",
            ),
        ),
        migrations.AlterField(
            model_name="trips",
            name="block_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="trips",
            name="service",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                to="website.calendar",
            ),
        ),
        migrations.AlterField(
            model_name="trips",
            name="shape_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="trips",
            name="trip_headsign",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="trips",
            name="trip_short_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
