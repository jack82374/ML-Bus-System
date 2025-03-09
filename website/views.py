#from django.shortcuts import render
from collections import defaultdict
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template import loader
import requests
from .models import Stops, Trips, VehiclePosition, Shapes


def index(request):
    template = loader.get_template("website/index.html")
    return HttpResponse(template.render(None, request))

def get_stops(request):
    relevant_route_ids = ['4497_87337', '4497_87340']
    stops = Stops.objects.filter(
        stoptimes__trip__route_id__in=relevant_route_ids
    ).distinct().values('stop_name', 'stop_desc', 'stop_lat', 'stop_lon')
    return JsonResponse(list(stops), safe=False)

def get_locations(request):
    relevant_route_ids = ['4497_87337', '4497_87340']
    positions = VehiclePosition.objects.filter(
        trip_id__in=Trips.objects.filter(route_id__in=relevant_route_ids).values_list('trip_id', flat=True)
    ).values('trip_id', 'direction_id', 'latitude', 'longitude', 'timestamp', 'route_id', 'vehicle_id')
    return JsonResponse(list(positions), safe=False)

def get_shapes(request):
    relevant_route_ids = ['4497_87337', '4497_87340']
    shape_route_mapping = Trips.objects.filter(
        route_id__in=relevant_route_ids
    ).values_list('shape_id', 'route_id').distinct()

    shape_to_route = {shape_id: route_id for shape_id, route_id in shape_route_mapping}

    shapes_data = Shapes.objects.filter(
        shape_id__in=shape_to_route.keys()
    ).values('shape_id', 'shape_pt_lat', 'shape_pt_lon')

    shapes_dict = defaultdict(list)
    for shape in shapes_data:
        shapes_dict[shape['shape_id']].append({
            'lat': shape['shape_pt_lat'],
            'lon': shape['shape_pt_lon']
        })

    shapes_list = [
        {'shape_id': shape_id, 'route_id': shape_to_route[shape_id], 'coordinates': coords}
        for shape_id, coords in shapes_dict.items()
    ]
    return JsonResponse(shapes_list, safe=False)