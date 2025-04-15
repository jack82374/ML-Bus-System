from datetime import datetime, timezone
import traceback
import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings  # Import settings for API key
from website.models import TripUpdate, StopUpdate, VehiclePosition, ArchiveTripUpdate, ArchiveStopUpdate, Trips, Stops, Routes, SiteSettings, StopTimes
from django.core.management import call_command
from django.db.models import Max

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
                trip_updates = trip_updates_request.json()

                locations_url = settings.GTFS_REALTIME_LOCATIONS_URL
                if not locations_url:
                    raise ValueError("GTFS_REALTIME_LOCATIONS_URL not set in settings.py")
                headers = {}
                if hasattr(settings, 'GTFS_REALTIME_API_KEY') and settings.GTFS_REALTIME_API_KEY:
                    headers['x-api-key'] = f'{settings.GTFS_REALTIME_API_KEY}'
                    headers['Cache-Control'] = 'no-cache'
                    #headers['format'] = 'json'
                now = datetime.now()
                midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
                seconds_since_midnight = (now - midnight).total_seconds()
                trip_id_mapping = {} # Map new trip_id's from Vehicles to TripUpdates (WHY NOT HAVE THEM IN BOTH!?)
                try:
                    locations_request = requests.get(locations_url, headers=headers, timeout=10) # Timeout after 10 seconds
                    locations_request.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                    locations = locations_request.json()
                    # Process the JSON data
                    #print(trip_updates)
                    #print(locations)
                    VehiclePosition.objects.all().delete()
                    #self.stdout.write(self.style.SUCCESS(f'Cleared all previous locations'))
                    for location in locations.get('entity', []):
                        try:
                            location['vehicle']['trip']['route_id'] = location['vehicle']['trip']['route_id'].split('_')[1]
                        except KeyError as no_routeid:
                            print(f"Location update {location['vehicle']['trip']['trip_id']} has no route_id, skipping")
                            continue
                        location_trip_data = location['vehicle']['trip']
                        location_unique_key = f"{location_trip_data['start_time']}_{location_trip_data['start_date']}_{location_trip_data['route_id']}_{location_trip_data['direction_id']}"
                        start_full = str(location['vehicle']['trip']['start_time'])
                        start_hour, start_minute, start_second = map(int, start_full.split(":"))
                        start_total_seconds = (start_hour*60*60) + (start_minute*60) + start_second
                        location_timestamp = datetime.fromtimestamp(int(location['vehicle']['timestamp']), tz=timezone.utc)
                        if (location['vehicle']['trip']['schedule_relationship'] == 'ADDED' and
                            (location['vehicle']['trip']['route_id'] == '93327' or location['vehicle']['trip']['route_id'] == '93330')):
                            # Should probably change this and every other check for the route_ids to be if route_id in list of relevant ids, like in the view
                            # It'd look better
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
                        elif location['vehicle']['trip']['route_id'] == '93327' or location['vehicle']['trip']['route_id'] == '93330':
                            trip_id = Trips.objects.get(trip_id=location['vehicle']['trip']['trip_id'])
                        else:
                            continue
                        #print(location['vehicle']['trip']['start_time'])
                        #VehiclePosition.objects.delete(timestamp<)
                        #print(location)
                        #if (location['vehicle']['vehicle']['id'] != 1893 and location['vehicle']['trip']['schedule_relationship'] != 'ADDED'):
                        if (location['vehicle']['trip']['route_id'] == '93327' or location['vehicle']['trip']['route_id'] == '93330'):
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
                except requests.exceptions.RequestException as e:
                    self.stdout.write(self.style.WARNING(f'Excedded request quota for vehicle locations, skipping'))
                    # This really doesn't make sense, refreshing every minute should keep me inside the 5000 requests per day limit
                    # Maybe vehicles have a different lower quota but that doesn't seem to be documented anywhere
                active_trip_list = []
                for update in trip_updates.get('entity', []):
                    update['trip_update']['trip']['route_id'] = update['trip_update']['trip']['route_id'].split('_')[1]
                    #print(update['trip_update']['trip']['trip_id'])
                    update_trip_data = update['trip_update']['trip']
                    update_unique_key = f"{update_trip_data['start_time']}_{update_trip_data['start_date']}_{update_trip_data['route_id']}_{update_trip_data['direction_id']}"
                    if update['trip_update']['trip']['schedule_relationship'] == 'ADDED' and (update['trip_update']['trip']['route_id'] == '93327' or update['trip_update']['trip']['route_id'] == '93330'):
                        #print(update)
                        #print(trip_id_mapping)
                        try:
                            trip_id = trip_id_mapping[update_unique_key]
                        except KeyError as key:
                            self.stdout.write(self.style.WARNING(f'No Matching entry for {update_unique_key} in trip_id mapping, skipping'))
                            continue
                    elif (update['trip_update']['trip']['route_id'] == '93327' or update['trip_update']['trip']['route_id'] == '93330'):
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
                    if (update['trip_update']['trip']['route_id'] == '93327' or update['trip_update']['trip']['route_id'] == '93330'):
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
                        ArchiveTripUpdate.objects.update_or_create(trip_id = trip.trip_id,
                                                            defaults={ 
                                                'start_time': start_trip_total_seconds,
                                                'start_date': update['trip_update']['trip']['start_date'],
                                                'schedule_relationship': update['trip_update']['trip']['schedule_relationship'],
                                                'route_id': route.route_id,
                                                'direction_id': update['trip_update']['trip']['direction_id'],
                                                'vehicle_id': vehicle_id,
                                                'timestamp':  update_timestamp,
                                                'day': now.weekday()
                                                }
                                                )
                        active_trip_list.append(trip_id)

                        #i = 0
                        stop_updates = update['trip_update'].get('stop_time_update', [])
                        for stop in update['trip_update'].get('stop_time_update', []):
                        #if stop_updates:
                            #stop = stop_updates[-1]
                            stop_indv = Stops.objects.get(stop_id=stop['stop_id'])
                            #update['trip_update'].get('vehicle', {}).get('vehicle_id')
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
                            #print(stop_full)
                            #print(type(stop_full))
                            try:
                                if stop_full is not None:
                                    stop_full = str(stop_full)
                                    stop_hour, stop_minute, stop_second = map(int, stop_full.split(":"))
                                    stop_total_seconds = (stop_hour*60*60) + (stop_minute*60) + stop_second
                                else:
                                    stop_total_seconds = None
                            except ValueError as wierd_times:
                                #print(f"{wierd_times} error was caused by {stop}")
                                stop_total_seconds = int(stop_full)
                            if stop_total_seconds is not None and stop_total_seconds > seconds_since_midnight:
                                print("The arrival time can't be in the future, ignoring!")
                                stop_total_seconds = None
                            # Sanity check to prevent arrival times in the future. Pretty bad but oh well.
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
                                                    'stop': stop_indv,
                                                    'schedule_relationship': relation
                                                                }
                                                    )
                            ArchiveStopUpdate.objects.update_or_create(trip_id = trip.trip_id,
                                                                stop_sequence = stop['stop_sequence'],
                                                                defaults={
                                                    #'stop_sequence': stop['stop_sequence'],
                                                    'arrival_time': stop_total_seconds,
                                                    'arrival_uncertainty': arrival_uncert,
                                                    'arrival_delay': arrival_delay,
                                                    'departure_delay': depart_delay,
                                                    'stop_id': stop_indv.stop_id,
                                                    'schedule_relationship': relation
                                                                }
                                                    )
                            
                        stop_sequences_this_trip = StopTimes.objects.filter(trip_id=trip_id)
                        if (stop_sequences_this_trip is not None):
                            #max_stop_seq_lookup = stop_sequences_this_trip.aggregate(Max('stop_sequence'))
                            try:
                                last_stop = update['trip_update'].get('stop_time_update', [])[-1]
                                #max_stop_value = max_stop_seq_lookup['stop_sequence__max']
                                max_stop_value = last_stop['stop_sequence']
                                for i in range(1, max_stop_value+1):
                                    update_exists = StopUpdate.objects.filter(trip_id=trip_id, stop_sequence=i).exists()
                                    if (update_exists == False):
                                        stop_id_this_seq = StopTimes.objects.get(trip_id=trip_id, stop_sequence=i).stop_id
                                        stop_instance = Stops.objects.get(stop_id=stop_id_this_seq)
                                        StopUpdate.objects.create(trip=trip, stop_sequence=i, stop=stop_instance, schedule_relationship="SKIPPED")
                            except IndexError as strangeList:
                                print(f"Could not access StopUpdates for trip {trip_id} so could not handle skips, continuing")

                    #print(trip_id)
                    call_command('predict', trip_id)
                    '''generated_delay = call_command('predict', trip_id)
                    print(type(generated_delay))
                    print(f"The predicted next delay is {generated_delay}.")
                    NextDelay.objects.update_or_create(trip_id = trip_id,
                                                       defaults={
                                                           'delay': generated_delay
                                                       }
                                                    )'''
                    
                #TripUpdate.objects.filter(trip not in active_trip_list).delete()
                #StopUpdate.objects.filter(trip not in active_trip_list).delete()
                TripUpdate.objects.exclude(trip__in=active_trip_list).delete()
                #StopUpdate.objects.exclude(trip__in=active_trip_list).delete()
                print(f"Location updates saved to models and DB")
            except requests.exceptions.RequestException as e:
                self.stderr.write(self.style.ERROR(f'Error fetching GTFS data: {e}'))
            except json.JSONDecodeError as e:
                self.stderr.write(self.style.ERROR(f'Error decoding JSON: {e} - Response Text: {trip_updates_request.text}, {locations_request.text}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}, {traceback.format_exc()}'))
        else:
            print(f"Currently in maintence mode, exiting")