from datetime import datetime, timezone
import hashlib
import traceback
import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings  # Import settings for API key
from website.models import TripUpdate, StopUpdate, VehiclePosition, ArchiveTripUpdate, ArchiveStopUpdate, ArchiveVehiclePosition, Trips, Stops, Routes, SiteSettings

class Command(BaseCommand):
    help = 'Fetches GTFS Realtime data'

    def handle(self, *args, **options):
        maintence_settings = SiteSettings.objects.first()
        if (maintence_settings.maintenance_mode == False):
            try:
                # Construct the API URL
                api_url = settings.GTFS_REALTIME_API_URL  # Store URL in settings
                if not api_url:
                    raise ValueError("GTFS_REALTIME_API_URL not set in settings.py")
                headers = {}
                if hasattr(settings, 'GTFS_REALTIME_API_KEY') and settings.GTFS_REALTIME_API_KEY:
                    headers['x-api-key'] = f'{settings.GTFS_REALTIME_API_KEY}'
                    headers['Cache-Control'] = 'no-cache'
                    #headers['format'] = 'json'

                trip_updates_request = requests.get(api_url, headers=headers, timeout=10) # Timeout after 10 seconds

                trip_updates_request.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

                locations_url = settings.GTFS_REALTIME_LOCATIONS_URL
                if not locations_url:
                    raise ValueError("GTFS_REALTIME_LOCATIONS_URL not set in settings.py")
                headers = {}
                if hasattr(settings, 'GTFS_REALTIME_API_KEY') and settings.GTFS_REALTIME_API_KEY:
                    headers['x-api-key'] = f'{settings.GTFS_REALTIME_API_KEY}'
                    headers['Cache-Control'] = 'no-cache'
                    #headers['format'] = 'json'

                locations_request = requests.get(locations_url, headers=headers, timeout=10) # Timeout after 10 seconds
                locations_request.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                trip_updates = trip_updates_request.json()
                locations = locations_request.json()
                # Process the JSON data
                #print(trip_updates)
                #print(locations)
                now = datetime.now()
                trip_id_mapping = {} # Map new trip_id's from Vehicles to TripUpdates (WHY NOT HAVE THEM IN BOTH!?)
                VehiclePosition.objects.all().delete()
                #self.stdout.write(self.style.SUCCESS(f'Cleared all previous locations'))
                for location in locations.get('entity', []):
                    location_trip_data = location['vehicle']['trip']
                    location_unique_key = f"{location_trip_data['start_time']}_{location_trip_data['start_date']}_{location_trip_data['route_id']}_{location_trip_data['direction_id']}"
                    start_full = str(location['vehicle']['trip']['start_time'])
                    start_hour, start_minute, start_second = map(int, start_full.split(":"))
                    start_total_seconds = (start_hour*60*60) + (start_minute*60) + start_second
                    location_timestamp = datetime.fromtimestamp(int(location['vehicle']['timestamp']), tz=timezone.utc)
                    if (location['vehicle']['trip']['schedule_relationship'] == 'ADDED' and
                        (location['vehicle']['trip']['route_id'] == '4497_87337' or location['vehicle']['trip']['route_id'] == '4497_87340')):
                        trip_id_mapping[location_unique_key] = location['vehicle']['trip']['trip_id']
                        trip_id, created = Trips.objects.get_or_create(
                            trip_id = location['vehicle']['trip']['trip_id'],
                            defaults={
                                #'start_time': start_total_seconds,
                                #'start_date': location['vehicle']['trip']['start_date'],
                                #'schedule_relationship': location['vehicle']['trip']['schedule_relationship'],
                                'route': Routes.objects.get(route_id=location['vehicle']['trip']['route_id']),
                                'direction_id': location['vehicle']['trip']['direction_id']
                        }
                        )
                    elif location['vehicle']['trip']['route_id'] == '4497_87337' or location['vehicle']['trip']['route_id'] == '4497_87340':
                        trip_id = Trips.objects.get(trip_id=location['vehicle']['trip']['trip_id'])
                    else:
                        continue
                    #print(location['vehicle']['trip']['start_time'])
                    #VehiclePosition.objects.delete(timestamp<)
                    #print(location)
                    #if (location['vehicle']['vehicle']['id'] != 1893 and location['vehicle']['trip']['schedule_relationship'] != 'ADDED'):
                    if (location['vehicle']['trip']['route_id'] == '4497_87337' or location['vehicle']['trip']['route_id'] == '4497_87340'):
                        #print(location)
                        '''VehiclePosition.objects.update_or_create(
                            trip = trip_id,
                            defaults={
                            'start_time': start_total_seconds,
                            'start_date': location['vehicle']['trip']['start_date'],
                            'schedule_relationship': location['vehicle']['trip']['schedule_relationship'],
                            'route': Routes.objects.get(route_id=location['vehicle']['trip']['route_id']),
                            'direction_id': location['vehicle']['trip']['direction_id'],
                            'latitude': location['vehicle']['position']['latitude'],
                            'longitude': location['vehicle']['position']['longitude'],
                            'timestamp': location_timestamp,
                            'vehicle_id': location['vehicle']['vehicle']['id']
                            }
                        )'''
                        #print(trip_id.trip_id)
                        VehiclePosition.objects.create(
                            trip = trip_id,
                            start_time = start_total_seconds,
                            start_date = location['vehicle']['trip']['start_date'],
                            schedule_relationship = location['vehicle']['trip']['schedule_relationship'],
                            route = Routes.objects.get(route_id=location['vehicle']['trip']['route_id']),
                            direction_id = location['vehicle']['trip']['direction_id'],
                            latitude = location['vehicle']['position']['latitude'],
                            longitude = location['vehicle']['position']['longitude'],
                            timestamp = location_timestamp,
                            vehicle_id = location['vehicle']['vehicle']['id']
                        )
                    # ADD CHECK FOR OLD ENTRIES HERE, USE THE TIMESTAMP
                    #VehiclePosition.objects.filter(timestamp__lt=location_timestamp).delete()

                for update in trip_updates.get('entity', []):
                    #print(update['trip_update']['trip']['trip_id'])
                    update_trip_data = update['trip_update']['trip']
                    update_unique_key = f"{update_trip_data['start_time']}_{update_trip_data['start_date']}_{update_trip_data['route_id']}_{update_trip_data['direction_id']}"
                    if update['trip_update']['trip']['schedule_relationship'] == 'ADDED' and (update['trip_update']['trip']['route_id'] == '4497_87337' or update['trip_update']['trip']['route_id'] == '4497_87340'):
                        #print(update)
                        #print(trip_id_mapping)
                        try:
                            trip_id = trip_id_mapping[update_unique_key]
                        except KeyError as key:
                            self.stdout.write(self.style.WARNING(f'No Matching entry for {update_unique_key} in trip_id mapping, skipping'))
                            continue
                    elif (update['trip_update']['trip']['route_id'] == '4497_87337' or update['trip_update']['trip']['route_id'] == '4497_87340'):
                        trip_id=update['trip_update']['trip']['trip_id']
                    else:
                        continue
                    #print(trip_id)
                    trip = Trips.objects.get(trip_id=trip_id)
                    route = Routes.objects.get(route_id=update['trip_update']['trip']['route_id'])
                    start_trip_full = str(update['trip_update']['trip']['start_time'])
                    start_trip_hour, start_trip_minute, start_trip_second = map(int, start_trip_full.split(":"))
                    start_trip_total_seconds = (start_trip_hour*60*60) + (start_trip_minute*60) + start_trip_second
                    update_timestamp = datetime.fromtimestamp(int(update['trip_update']['timestamp']), tz=timezone.utc)
                    vehicle_id = update['trip_update'].get('vehicle', {}).get('vehicle_id')
                    if (update['trip_update']['trip']['route_id'] == '4497_87337' or update['trip_update']['trip']['route_id'] == '4497_87340'):
                        TripUpdate.objects.update_or_create(trip = trip,
                                                            defaults={ 
                                                'start_time': start_trip_total_seconds,
                                                'start_date': update['trip_update']['trip']['start_date'],
                                                'schedule_relationship': update['trip_update']['trip']['schedule_relationship'],
                                                'route': route,
                                                'direction_id': update['trip_update']['trip']['direction_id'],
                                                'vehicle_id': vehicle_id,
                                                'timestamp':  update_timestamp,
                                                'day': now.weekday()
                                                }
                                                )
                        ArchiveTripUpdate.objects.create(trip_id = trip.trip_id, 
                                                start_time = start_trip_total_seconds,
                                                start_date = update['trip_update']['trip']['start_date'],
                                                schedule_relationship = update['trip_update']['trip']['schedule_relationship'],
                                                route_id = route.route_id,
                                                direction_id = update['trip_update']['trip']['direction_id'],
                                                vehicle_id = vehicle_id,
                                                timestamp = update_timestamp,
                                                day = now.weekday()
                                                )
                        i = 0
                        for stop in update['trip_update'].get('stop_time_update', []):
                            stop_id = Stops.objects.get(stop_id=stop['stop_id'])
                            #update['trip_update'].get('vehicle', {}).get('vehicle_id')
                            #arrival_uncert = stop['arrival'].get('uncertainty')
                            arrival_dict = stop.get('arrival')
                            if arrival_dict is not None:
                                arrival_uncert = arrival_dict.get('uncertainty')
                                stop_full = arrival_dict.get('time')
                                arrival_delay = arrival_dict.get('delay')
                            else:
                                arrival_uncert = None
                                stop_full = None
                                arrival_delay = None
                            depart_dict = stop.get('departure')
                            if depart_dict is not None:
                                depart_delay = depart_dict.get('delay')
                            else:
                                depart_delay = None
                            #stop_full = stop['arrival'].get('time')
                            #print(stop_full)
                            #print(type(stop_full))
                            if stop_full is not None:
                                stop_full = str(stop_full)
                                stop_hour, stop_minute, stop_second = map(int, stop_full.split(":"))
                                stop_total_seconds = (stop_hour*60*60) + (stop_minute*60) + stop_second
                            else:
                                stop_total_seconds = None
                            relation = stop.get('schedule_relationship')
                            #print(stop)
                            StopUpdate.objects.update_or_create(trip = trip,
                                                                stop_sequence = stop['stop_sequence'],
                                                                defaults={
                                                    #'stop_sequence': stop['stop_sequence'],
                                                    'arrival_time': stop_total_seconds,
                                                    'arrival_uncertainty': arrival_uncert,
                                                    'arrival_delay': arrival_delay,
                                                    'departure_delay': depart_delay,
                                                    'stop_id': stop_id,
                                                    'schedule_relationship': relation
                                                                }
                                                    )
                            ArchiveStopUpdate.objects.create(trip_id = trip.trip_id, 
                                                    stop_sequence = stop['stop_sequence'],
                                                    arrival_time = stop_total_seconds,
                                                    arrival_uncertainty = arrival_uncert,
                                                    arrival_delay = arrival_delay,
                                                    departure_delay = depart_delay,
                                                    stop_id = stop_id.stop_id,
                                                    schedule_relationship = relation
                                                    )
                            if i == 0:
                                StopUpdate.objects.filter(trip=trip, stop_sequence__lt=stop['stop_sequence']).delete()
                            # Deleting older stop updates. Find a better way to do this, this is terrible
                            i = i + 1

                
                

                print(f"Location updates saved to models and DB")
            except requests.exceptions.RequestException as e:
                self.stderr.write(self.style.ERROR(f'Error fetching GTFS data: {e}'))
            except json.JSONDecodeError as e:
                self.stderr.write(self.style.ERROR(f'Error decoding JSON: {e} - Response Text: {trip_updates_request.text}, {locations_request.text}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}, {traceback.format_exc()}'))
        else:
            print(f"Currently in maintence mode, exiting")