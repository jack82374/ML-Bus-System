#from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def index(request):
    #return HttpResponse("Hello, world. You're at the website index.")
    template = loader.get_template("website/index.html")
    return HttpResponse(template.render(None, request))