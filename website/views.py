#from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .models import Stops, Agency, Routes


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