#from django.shortcuts import render
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
import requests
from .models import Stops, Agency, Routes, VehiclePosition


def index(request):
    #return HttpResponse("Hello, world. You're at the website index.")
    template = loader.get_template("website/index.html")
    return HttpResponse(template.render(None, request))

def get_stops(request):
    stops = Stops.objects.all().values('stop_name', 'stop_desc', 'stop_lat', 'stop_lon')
    #luas_agency = Agency.objects.get(agency_name="LUAS")
    #luas_routes = Routes.objects.filter(agency=luas_agency)
    #stops = Stops.objects.filter(stoptimes__route__agency_trip_route=luas_routes).distinct().values('stop_name', 'stop_desc', 'stop_lat', 'stop_lon')
    return JsonResponse(list(stops), safe=False)

def get_locations(request):
    positions = VehiclePosition.objects.all()
    return JsonResponse(list(positions), safe=False)
'''
    #try:
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

            locations = requests.get(locations_url, headers=headers, timeout=10) # Timeout after 10 seconds

            locations.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()
            location_json = locations.json()
            #return location_json
            return JsonResponse(location_json, safe=False)
            # Process the JSON data
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
        print(f'Error fetching GTFS data: {e}')
    except json.JSONDecodeError as e:
        print(f'Error decoding JSON: {e} - Response Text: {response.text}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')'''