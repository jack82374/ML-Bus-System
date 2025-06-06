import os
import requests
import zipfile
import csv
import io
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from website.models import Routes, Stops, Trips, StopTimes, Calendar, CalendarDates, \
    Agency, Shapes, FeedInfo, GTFSDataInfo, SiteSettings, TripUpdate, VehiclePosition, StopUpdate, NextDelay

#import hashlib

class Command(BaseCommand):
    help = 'Checks for GTFS updates and imports data'

    def handle(self, *args, **options):
        try:
            gtfs_info = GTFSDataInfo.objects.get()
        except GTFSDataInfo.DoesNotExist:
            gtfs_info = GTFSDataInfo.objects.create()
        try:
            url = settings.GTFS_ZIP_URL
            response = requests.head(url)  # Efficiently check for changes
            response.raise_for_status()

            last_modified = response.headers.get('Last-Modified')
            if last_modified:
                last_modified_date = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
                last_modified_date = timezone.make_aware(last_modified_date, timezone.get_current_timezone())
                self.stdout.write(self.style.SUCCESS(f'Last Modified: {last_modified_date}'))

            '''if hasattr(settings, 'GTFS_HASH_URL') and settings.GTFS_HASH_URL:
                hash_response = requests.get(settings.GTFS_HASH_URL)
                hash_response.raise_for_status()
                remote_hash = hash_response.text.strip()
                if local_hash != remote_hash:
                    self.stdout.write(self.style.WARNING('GTFS data has changed. Updating...'))
                    settings.GTFS_LOCAL_HASH = remote_hash
                    self.import_gtfs_data(url)
                else:
                    self.stdout.write(self.style.SUCCESS('GTFS data is up to date.'))
            else:'''
            #self.stdout.write(self.style.WARNING('No hash URL provided, relying on last modified.'))
            #if hasattr(settings, 'GTFS_STATIC_MOD_DATE') and settings.GTFS_STATIC_MOD_DATE:
            if last_modified_date and (gtfs_info.last_modified is None or last_modified_date > gtfs_info.last_modified):
                self.stdout.write(self.style.NOTICE(f'GTFS Static Files Update Detected'))
                try:
                    maintence_settings = SiteSettings.objects.get()
                except SiteSettings.DoesNotExist:
                    maintence_settings = SiteSettings.objects.create()
                maintence_settings.maintenance_mode = True
                maintence_settings.save() # Enable maintence mode
                self.import_gtfs_data(url)
                gtfs_info.last_modified = last_modified_date
                gtfs_info.save()
                maintence_settings.maintenance_mode = False
                maintence_settings.save() # Disable maintence mode
            else:
                self.stdout.write(self.style.NOTICE(f'No GTFS Static Files Update Detected'))
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Error checking for GTFS updates: {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}'))

    def import_gtfs_data(self, url):
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                #Process files in correct order
                models_to_delete = [StopTimes, Trips, Routes, CalendarDates, Calendar, Stops, Agency, Shapes,\
                                    TripUpdate, VehiclePosition, StopUpdate, NextDelay] 
                # Order is important as the ones at the start depend on the ones at the end
                for model in models_to_delete:
                    deleted_count, _ = model.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} {model.__name__} objects'))
                # Examine trips first

                relevant_trips_list = []
                relevant_service_ids_list = []
                relevant_shape_ids_list = []
                with zip_file.open('trips.txt') as trips_file:
                    trips_reader = csv.DictReader(io.TextIOWrapper(trips_file, 'utf-8'))
                    for row in trips_reader:
                        if (row.get('route_id').split('_')[1] == '97732' or row.get('route_id').split('_')[1] == '97735'):
                            relevant_trips_list.append(row.get('trip_id'))
                            relevant_service_ids_list.append(row.get('service_id'))
                            relevant_shape_ids_list.append(row.get('shape_id'))

                file_order = ['feed_info.txt', 'agency.txt', 'stops.txt', 'shapes.txt', 'routes.txt', 'calendar.txt', 'calendar_dates.txt', 'trips.txt', 'stop_times.txt']
                for filename in file_order:
                    if filename in zip_file.namelist():
                        with zip_file.open(filename) as txt_file:
                            reader = csv.DictReader(io.TextIOWrapper(txt_file, 'utf-8'))
                            model_name = filename[:-4]
                            self.import_csv_data(reader, model_name, relevant_trips_list, relevant_service_ids_list, relevant_shape_ids_list)
                            # Put in something here to go through all the trips first and get their service_id and shape_id, while also
                            # Saving the trip_id for stop_times
            self.stdout.write(self.style.SUCCESS('GTFS data imported successfully.'))

        except zipfile.BadZipFile as e:
            self.stderr.write(self.style.ERROR(f"Error with zip file: {e}"))
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Error downloading GTFS data: {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred during import: {e}'))

    def import_csv_data(self, reader, model_name, relevant_trips_list, relevant_service_ids_list, relevant_shape_ids_list):
        model_map = {
            'feed_info': FeedInfo,
            'agency': Agency,
            'stops': Stops,
            'routes': Routes,
            'trips': Trips,
            'stop_times': StopTimes,
            'calendar': Calendar,
            'calendar_dates': CalendarDates,
            'shapes': Shapes
        }
        model = model_map.get(model_name)
        if model:
            model.objects.all().delete()
            objs = []
            for row in reader:
                try:
                    #print(model_name)
                    # Consider limiting this to just the 208 and 205
                    if model_name == 'routes' and (row.get('route_id').split('_')[1] == '97732' or row.get('route_id').split('_')[1] == '97735'):
                        #print(row)
                        #print(row.get('route_id'))
                        #print(row.get('route_id').split('_')[1])
                        agency_id = row.get('agency_id')
                        route_id = row.get('route_id').split('_')[1]
                        #print(route_id)
                        #print(type(route_id))
                        agency_instance = Agency.objects.get(agency_id=agency_id) if agency_id else None
                        #model.objects.create(agency = agency_instance, **{k: v for k, v in row.items() if k != 'agency_id'})
                        objs.append(model(agency = agency_instance, route_id=route_id, **{k: v for k, v in row.items() if k not in ['route_id', 'agency_id']}))
                    elif model_name == 'trips' and (row.get('trip_id') in relevant_trips_list) and (row.get('route_id').split('_')[1] == '97732' or row.get('route_id').split('_')[1] == '97735'):
                        route_id = row.get('route_id').split('_')[1]
                        service_id = row.get('service_id')
                        #shape_id = row.get('shape_id')
                        route_instance = Routes.objects.get(route_id=route_id) if route_id else None
                        calendar_instance = Calendar.objects.get(service_id=service_id) if service_id else None
                        #shape_instance = Shapes.objects.get(shape_id=shape_id) if shape_id else None
                        #model.objects.create(route=route_instance, calendar = calendar_instance, shape = shape_instance, **{k: v for k, v in row.items() if k not in ['route_id', 'service_id', 'shape_id']})
                        objs.append(model(route=route_instance, service=calendar_instance, **{k: v for k, v in row.items() if k not in ['route_id', 'service_id']}))
                    elif model_name == 'stop_times' and (row.get('trip_id') in relevant_trips_list):
                        trip_id = row.get('trip_id')
                        stop_id = row.get('stop_id')
                        #stop_seq = row.get('stop_sequence')
                        trip_instance = Trips.objects.get(trip_id=trip_id) if trip_id else None
                        stop_instance = Stops.objects.get(stop_id=stop_id) if stop_id else None
                        arrival_full = str(row.get("arrival_time"))
                        depart_full = str(row.get("departure_time"))
                        arrival_hour, arrival_minute, arrival_second = map(int, arrival_full.split(":"))
                        arrival_total_seconds = (arrival_hour*60*60) + (arrival_minute*60) + arrival_second
                        depart_hour, depart_minute, depart_second = map(int, depart_full.split(":"))
                        depart_total_seconds = (depart_hour*60*60) + (depart_minute*60) + depart_second
                        #model.objects.create(trip = trip_instance, stop = stop_instance, **{k: v for k, v in row.items() if k not in ['trip_id', 'stop_id']})
                        #print_mod = model(trip=trip_instance, stop=stop_instance, arrival_time=arrival_total_seconds, departure_time=depart_total_seconds,
                        #                  **{k: v for k, v in row.items() if k not in ['trip_id', 'stop_id', 'arrival_time', 'departure_time']})
                        objs.append(model(trip=trip_instance, stop=stop_instance, arrival_time=arrival_total_seconds, departure_time=depart_total_seconds,
                                          **{k: v for k, v in row.items() if k not in ['trip_id', 'stop_id', 'arrival_time', 'departure_time']}))
                        #self.stdout.write(self.style.SUCCESS(f"Arrival Time: {print_mod.arrival_time} Departure Time: {print_mod.departure_time}"))
                        #objs.append(model(**{k: v for k, v in row.items() if k not in ['trip_id', 'stop_id', 'stop_sequence']}, stop=stop_instance, unique_stop_instance=objs.pop()))
                    elif model_name == 'calendar_dates':
                        service_id = row.get('service_id')
                        calendar_instance = Calendar.objects.get(service_id=service_id) if service_id else None
                        #model.objects.create(calendar = calendar_instance, **{k: v for k, v in row.items() if k != 'service_id'})
                        objs.append(model(service=calendar_instance, **{k: v for k, v in row.items() if k != 'service_id'}))
                    elif model_name == 'stops':
                        # Types must be converted here
                        zone_id_str = row.get('zone_id')
                        zone_id = None if not zone_id_str else int(zone_id_str) if zone_id_str.isdigit() else None
                        row['zone_id'] = zone_id
                        stop_code_str = row.get('stop_code')
                        stop_code = None if not stop_code_str else int(stop_code_str) if stop_code_str.isdigit() else None
                        row['stop_code'] = stop_code
                        location_type_str = row.get('location_type')
                        location_type = None if not location_type_str else int(location_type_str) if location_type_str.isdigit() else None
                        row['location_type'] = location_type
                        #model.objects.create(**row)
                        objs.append(model(**row))
                    elif model_name == 'agency':
                        if (int(row.get('agency_id')) == 7778020):
                            objs.append(model(**row))
                    elif model_name == 'shapes' and (row.get('shape_id') in relevant_shape_ids_list):
                        objs.append(model(**row))
                    elif model_name == 'calendar' and (row.get('service_id') in relevant_service_ids_list):
                        objs.append(model(**row))
                    elif model_name == 'feed_info':
                        #model.objects.create(**row)
                        objs.append(model(**row))
                    #self.stdout.write(self.style.SUCCESS(f'{model_name} data imported succesfully!'))
                except ObjectDoesNotExist as e:
                    #self.stderr.write(self.style.ERROR(f"Error importing row: {row} into {model_name}: {e} of type {e.__class__.__name__}"))
                    pass
            if objs:
                    model.objects.bulk_create(objs, batch_size=100000)
                    self.stdout.write(self.style.SUCCESS(f'{model_name} data imported succesfully!'))
            else:
                self.stdout.write(self.style.WARNING(f'No data found for {model_name}'))
        else:
            self.stdout.write(self.style.WARNING(f"No model found for {model_name}"))