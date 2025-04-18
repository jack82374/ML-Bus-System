# Generated by Django 5.1.5 on 2025-02-25 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0012_sitesettings"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="archivestopupdate",
            name="trip",
        ),
        migrations.RemoveField(
            model_name="archivetripupdate",
            name="route",
        ),
        migrations.RemoveField(
            model_name="archivetripupdate",
            name="trip",
        ),
        migrations.RemoveField(
            model_name="archivevehicleposition",
            name="route",
        ),
        migrations.RemoveField(
            model_name="archivevehicleposition",
            name="trip",
        ),
        migrations.AddField(
            model_name="archivestopupdate",
            name="trip_id",
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="archivetripupdate",
            name="route_id",
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="archivetripupdate",
            name="trip_id",
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="archivevehicleposition",
            name="route_id",
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="archivevehicleposition",
            name="trip_id",
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="archivestopupdate",
            name="stop_id",
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]
