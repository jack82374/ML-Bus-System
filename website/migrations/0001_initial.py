# Generated by Django 5.1.5 on 2025-01-25 21:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('agency_id', models.IntegerField(primary_key=True, serialize=False)),
                ('agency_name', models.CharField(max_length=255)),
                ('agency_url', models.CharField(max_length=255)),
                ('agency_timezone', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('service_id', models.IntegerField(primary_key=True, serialize=False)),
                ('monday', models.BooleanField()),
                ('tuesday', models.BooleanField()),
                ('wednesday', models.BooleanField()),
                ('thursday', models.BooleanField()),
                ('friday', models.BooleanField()),
                ('saturday', models.BooleanField()),
                ('sunday', models.BooleanField()),
                ('start_date', models.IntegerField()),
                ('end_date', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='FeedInfo',
            fields=[
                ('feed_publisher_name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('feed_publisher_url', models.CharField(max_length=255)),
                ('feed_lang', models.CharField(max_length=10)),
                ('feed_start_date', models.IntegerField()),
                ('feed_end_date', models.IntegerField()),
                ('feed_version', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Shapes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shape_pt_lat', models.FloatField()),
                ('shape_pt_lon', models.FloatField()),
                ('shape_pt_sequence', models.IntegerField()),
                ('shape_dist_traveled', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Stops',
            fields=[
                ('stop_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('stop_code', models.IntegerField(blank=True, null=True)),
                ('stop_name', models.CharField(max_length=255)),
                ('stop_desc', models.CharField(max_length=512)),
                ('stop_lat', models.FloatField()),
                ('stop_lon', models.FloatField()),
                ('zone_id', models.IntegerField(blank=True, null=True)),
                ('stop_url', models.CharField(max_length=255)),
                ('location_type', models.SmallIntegerField(blank=True, null=True)),
                ('parent_station', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UniqueShape',
            fields=[
                ('shape_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='CalendarDates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.IntegerField()),
                ('exception_type', models.SmallIntegerField()),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='website.calendar')),
            ],
        ),
        migrations.CreateModel(
            name='Routes',
            fields=[
                ('route_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('route_short_name', models.CharField(max_length=12)),
                ('route_long_name', models.CharField(max_length=255)),
                ('route_desc', models.CharField(max_length=512)),
                ('route_type', models.SmallIntegerField()),
                ('route_url', models.CharField(max_length=255)),
                ('route_color', models.CharField(max_length=6)),
                ('route_text_color', models.CharField(max_length=6)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='website.agency')),
            ],
        ),
        migrations.CreateModel(
            name='Trips',
            fields=[
                ('trip_id', models.IntegerField(primary_key=True, serialize=False)),
                ('trip_headsign', models.CharField(max_length=255)),
                ('trip_short_name', models.CharField(max_length=255)),
                ('direction_id', models.BooleanField()),
                ('block_id', models.CharField(max_length=255)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='website.routes')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='website.calendar')),
                ('shape', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='website.shapes')),
            ],
        ),
        migrations.AddField(
            model_name='shapes',
            name='unique_shape',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='website.uniqueshape'),
        ),
        migrations.CreateModel(
            name='UniqueStop',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('stop_sequence', models.IntegerField()),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='website.trips')),
            ],
        ),
        migrations.CreateModel(
            name='StopTimes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrival_time', models.TimeField()),
                ('departure_time', models.TimeField()),
                ('stop_headsign', models.CharField(max_length=255)),
                ('pickup_type', models.SmallIntegerField()),
                ('drop_off_type', models.SmallIntegerField()),
                ('timepoint', models.BooleanField()),
                ('stop', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='website.stops')),
                ('unique_stop', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='website.uniquestop')),
            ],
        ),
    ]
