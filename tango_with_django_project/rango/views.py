from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says hello world!<br> \
    	                 <a href='/rango/about/'>About</a>")


def about(request):
    response = HttpResponse()
    response.write("Rango says: Here is the about page.<br>")
    response.write("<a href='/rango/'>Index</a>")

    return response
