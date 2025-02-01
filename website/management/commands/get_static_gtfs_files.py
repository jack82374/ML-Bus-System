import os
import requests
import zipfile
import csv
import io
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand
from website.models import Routes, Stops, Trips, StopTimes, Calendar, CalendarDates, Agency, Shapes, UniqueStop, FeedInfo, GTFSDataInfo

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
            local_hash = settings.GTFS_LOCAL_HASH
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
            gtfs_info.last_modified = None #Get rid of this
            gtfs_info.save() #And this afterwards
            if last_modified_date and (gtfs_info.last_modified is None or last_modified_date > gtfs_info.last_modified):
                self.stdout.write(self.style.NOTICE(f'GTFS Static Files Update Detected'))
                self.import_gtfs_data(url)
                gtfs_info.last_modified = last_modified_date
                gtfs_info.save()
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
                models_to_delete = [UniqueStop, StopTimes, Trips, Routes, CalendarDates, Calendar, Stops, Agency, Shapes] #Order is important as the ones at the start depend on the ones at the end
                for model in models_to_delete:
                    deleted_count, _ = model.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} {model.__name__} objects'))
                file_order = ['feed_info.txt', 'agency.txt', 'stops.txt', 'shapes.txt', 'routes.txt', 'calendar.txt', 'calendar_dates.txt', 'trips.txt', 'stop_times.txt']
                for filename in file_order:
                    if filename in zip_file.namelist():
                        with zip_file.open(filename) as txt_file:
                            reader = csv.DictReader(io.TextIOWrapper(txt_file, 'utf-8'))
                            model_name = filename[:-4]
                            self.import_csv_data(reader, model_name)
            self.stdout.write(self.style.SUCCESS('GTFS data imported successfully.'))

        except zipfile.BadZipFile as e:
            self.stderr.write(self.style.ERROR(f"Error with zip file: {e}"))
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Error downloading GTFS data: {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred during import: {e}'))

    def import_csv_data(self, reader, model_name):
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
            sub_objs = []
            for row in reader:
                try:
                    
                    if model_name == 'routes':
                        agency_id = row.get('agency_id')
                        agency_instance = Agency.objects.get(agency_id=agency_id) if agency_id else None
                        #model.objects.create(agency = agency_instance, **{k: v for k, v in row.items() if k != 'agency_id'})
                        objs.append(model(agency = agency_instance, **{k: v for k, v in row.items() if k != 'agency_id'}))
                    elif model_name == 'trips':
                        route_id = row.get('route_id')
                        service_id = row.get('service_id')
                        #shape_id = row.get('shape_id')
                        route_instance = Routes.objects.get(route_id=route_id) if route_id else None
                        calendar_instance = Calendar.objects.get(service_id=service_id) if service_id else None
                        #shape_instance = Shapes.objects.get(shape_id=shape_id) if shape_id else None
                        #model.objects.create(route=route_instance, calendar = calendar_instance, shape = shape_instance, **{k: v for k, v in row.items() if k not in ['route_id', 'service_id', 'shape_id']})
                        objs.append(model(route=route_instance, service=calendar_instance, **{k: v for k, v in row.items() if k not in ['route_id', 'service_id']}))
                    elif model_name == 'stop_times':
                        trip_id = row.get('trip_id')
                        stop_id = row.get('stop_id')
                        stop_seq = row.get('stop_sequence')
                        trip_instance = Trips.objects.get(trip_id=trip_id) if trip_id else None
                        stop_instance = Stops.objects.get(stop_id=stop_id) if stop_id else None
                        #unique_stop_instance, created = UniqueShape.objects.get_or_create(trip=trip_instance, stop_sequence = stop_seq)
                        uniq_stop = UniqueStop(trip=trip_instance, stop_sequence=stop_seq)
                        #objs.append(UniqueStop(trip=trip_instance, stop_sequence=stop_seq))
                        sub_objs.append(uniq_stop)
                        #model.objects.create(trip = trip_instance, stop = stop_instance, **{k: v for k, v in row.items() if k not in ['trip_id', 'stop_id']})
                        objs.append(model(unique_stop=uniq_stop, stop=stop_instance, **{k: v for k, v in row.items() if k not in ['trip_id', 'stop_id', 'stop_sequence']}))
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
                    elif model_name == 'shapes':
                        #shape_id = row.get('shape_id')
                        #unique_shape_instance, created = UniqueShape.objects.get_or_create(shape_id=shape_id)
                        #new_uniq = UniqueShape(shape_id=shape_id)
                        #objs.append(UniqueShape(shape_id=shape_id))
                        #sub_objs.append(new_uniq)
                        #model.objects.create(unique_shape=unique_shape_instance, **{k: v for k, v in row.items() if k != 'shape_id'})
                        #objs.append(model(unique_shape=unique_shape_instance, **{k: v for k, v in row.items() if k != 'shape_id'}))
                        #objs.append(model(unique_shape=new_uniq, **{k: v for k, v in row.items() if k != 'shape_id'}))
                        #objs.append(model(**{k: v for k, v in row.items() if k != 'shape_id'}, objs.pop()))
                        objs.append(model(**row))
                    else:
                        #model.objects.create(**row)
                        objs.append(model(**row))
                    #self.stdout.write(self.style.SUCCESS(f'{model_name} data imported succesfully!'))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error importing row: {row} into {model_name}: {e}"))
            if objs:
                    if model_name == 'stop_times':
                        #UniqueStop.objects.bulk_create(sub_objs, batch_size=200000)
                        UniqueStop.objects.bulk_create(sub_objs, batch_size=100000)
                        self.stdout.write(self.style.SUCCESS(f'unique_stop data imported succesfully!'))
                    '''elif model_name == 'shapes':
                        UniqueShape.objects.bulk_create(sub_objs, batch_size=200000)
                        self.stdout.write(self.style.SUCCESS(f'unique_shape data imported succesfully!'))'''
                    model.objects.bulk_create(objs, batch_size=100000)
                    self.stdout.write(self.style.SUCCESS(f'{model_name} data imported succesfully!'))
            else:
                self.stdout.write(self.style.WARNING(f'No data found for {model_name}'))
        else:
            self.stdout.write(self.style.WARNING(f"No model found for {model_name}"))