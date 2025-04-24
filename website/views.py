#from django.shortcuts import render
from collections import defaultdict
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
import requests
from .models import Stops, Trips, VehiclePosition, Shapes, StopTimes, TripUpdate, StopUpdate, NextDelay
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import keras


def index(request):
    template = loader.get_template("website/index.html")
    return HttpResponse(template.render(None, request))

def get_stops(request):
    relevant_route_ids = ['93327', '93330']
    stops = Stops.objects.filter(
        stoptimes__trip__route_id__in=relevant_route_ids
    ).distinct().values('stop_name', 'stop_desc', 'stop_lat', 'stop_lon', 'stop_id')
    return JsonResponse(list(stops), safe=False)

def get_locations(request):
    relevant_route_ids = ['93327', '93330']
    positions = VehiclePosition.objects.filter(
        trip_id__in=Trips.objects.filter(route_id__in=relevant_route_ids).values_list('trip_id', flat=True)
    ).values('trip_id', 'direction_id', 'latitude', 'longitude', 'timestamp', 'route_id', 'vehicle_id')
    return JsonResponse(list(positions), safe=False)

def get_shapes(request):
    relevant_route_ids = ['93327', '93330']
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

def stop_entries(request, stop_id):
    #stop_name = Stops.objects.get(stop_id=stop_id).stop_name
    active_trips = TripUpdate.objects.distinct().values_list('trip_id', flat=True)
    stoptimes_to_consider = list(StopTimes.objects.filter(trip__in=active_trips, stop_id=stop_id).distinct().
                                 select_related('trip__route').values('id', 'trip_id', 'arrival_time', 'trip__route_id'))
    #active_relevant_stoptimes_json = json.dumps(stoptimes_to_consider)
    stop_updates = list(StopUpdate.objects.filter(trip__in=active_trips, stop_id=stop_id).distinct().
                        values('trip_id', 'stop_sequence', 'arrival_time', 'arrival_delay', 'departure_delay', 'stop_id', 'schedule_relationship'))
    trip_updates = list(TripUpdate.objects.filter(trip__in=active_trips).distinct().
                        values('trip_id', 'schedule_relationship'))
    delays = list(NextDelay.objects.filter(trip__in=active_trips).distinct().
                        values('trip_id', 'delay'))
    #stop_updates_json = json.dumps(stop_updates)
    context = {
        'active_relevant_stoptimes_json': stoptimes_to_consider,
        'stop_updates_json': stop_updates,
        'trip_updates_json': trip_updates,
        'delays_json' : delays
    }
    #return render(request, 'website/stop_entries.html', context)
    return JsonResponse(context)

#model = keras.models.load_model('website/ml_model/model.keras')

#@csrf_exempt
'''def predict(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        input_data = np.array(data['input'])
        predictions = model.predict(input_data)
        return JsonResponse({'predictions': predictions.tolist()})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def reload_model_view(request):
    global model
    model = keras.models.load_model('website/ml_model/model.keras')
    #return JsonResponse({'status': 'Model reloaded successfully'})'''

def stop_page(request, stop_id):
    stop_name = Stops.objects.get(stop_id=stop_id).stop_name
    context = {
        'stop_id': stop_id,
        'stop_name': stop_name
    }
    return render(request, 'website/stop_entries.html', context)

def stop_page_admin(request, stop_id):
    stop_name = Stops.objects.get(stop_id=stop_id).stop_name
    context = {
        'stop_id': stop_id,
        'stop_name': stop_name
    }
    return render(request, 'website/stop_entries_admin.html', context)

def about(request):
    template = loader.get_template("website/about.html")
    return HttpResponse(template.render(None, request))

def help(request):
    template = loader.get_template("website/help.html")
    return HttpResponse(template.render(None, request))