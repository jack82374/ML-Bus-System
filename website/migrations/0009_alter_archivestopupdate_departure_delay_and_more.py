# Generated by Django 5.1.5 on 2025-02-17 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0008_alter_archivestopupdate_arrival_delay_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="archivestopupdate",
            name="departure_delay",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="stopupdate",
            name="departure_delay",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
