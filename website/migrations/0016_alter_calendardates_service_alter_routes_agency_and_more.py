# Generated by Django 5.1.1 on 2025-03-24 12:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0015_alter_archivestopupdate_schedule_relationship_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="calendardates",
            name="service",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="website.calendar"
            ),
        ),
        migrations.AlterField(
            model_name="routes",
            name="agency",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="website.agency"
            ),
        ),
        migrations.AlterField(
            model_name="stoptimes",
            name="stop",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="website.stops"
            ),
        ),
        migrations.AlterField(
            model_name="stoptimes",
            name="trip",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="website.trips"
            ),
        ),
        migrations.AlterField(
            model_name="trips",
            name="route",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="website.routes"
            ),
        ),
        migrations.AlterField(
            model_name="trips",
            name="service",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="website.calendar",
            ),
        ),
    ]
