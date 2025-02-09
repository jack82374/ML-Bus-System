import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings  # Import settings for API key

class Command(BaseCommand):
    help = 'Fetches GTFS Realtime data'

    def handle(self, *args, **options):
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

            response = requests.get(api_url, headers=headers, timeout=10) # Timeout after 10 seconds

            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            locations_url = settings.GTFS_REALTIME_LOCATIONS_URL
            if not locations_url:
                raise ValueError("GTFS_REALTIME_LOCATIONS_URL not set in settings.py")
            headers = {}
            if hasattr(settings, 'GTFS_REALTIME_API_KEY') and settings.GTFS_REALTIME_API_KEY:
                headers['x-api-key'] = f'{settings.GTFS_REALTIME_API_KEY}'
                headers['Cache-Control'] = 'no-cache'
                #headers['format'] = 'json'

            locations = requests.get(api_url, headers=headers, timeout=10) # Timeout after 10 seconds

            locations.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            # Handle different data formats (JSON, Protocol Buffer)
            '''if response.headers.get('Content-Type') == 'application/x-protobuf':
               from gtfs_realtime_pb2 import FeedMessage
               feed = FeedMessage()
               feed.ParseFromString(response.content)
               # process protobuf message
               for entity in feed.entity:
                   if entity.HasField('trip_update'):
                       # Process trip update data
                       trip_id = entity.trip_update.trip.trip_id
                       # ... other data
                       self.stdout.write(self.style.SUCCESS(f'Fetched trip update: {trip_id}'))'''
            #else: #Default to json
            data = response.json()
            location_json = locations.json()
            # Process the JSON data
            '''for item in data['entity']: #Adapt to your data
                if 'trip_update' in item:
                    trip_update = item['trip_update']
                    trip = trip_update.get('trip') # Use get to avoid key errors
                    if trip:
                        trip_id = trip.get('trip_id')
                        route_id = trip.get('route_id')
                        if trip_id:
                            print(f'Trip ID: {trip_id}')
                        if route_id:
                            if isinstance(route_id, dict): # Check if it's a dict
                                route_id = route_id.get('id') # Extract the id from the dict
                            if isinstance(route_id, str) and route_id.endswith('456'):
                                print('Found route 456')'''
            i = 0
            for update in data['entity']:
                print(f'{update}\n')
                i = i+1
            print(f"There are {i} updates per API call")

            j = 0
            for location in location_json['entity']:
                print(f'{location}\n')
                j = j+1
            print(f"There are {j} location updates per API call")

        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Error fetching GTFS data: {e}'))
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f'Error decoding JSON: {e} - Response Text: {response.text}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}'))