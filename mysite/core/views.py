"""Where request logic lives
Functions or classes that return responses"""
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    context = {
        'name': 'Shweta',
        'role': 'Django Learner'
    }
    return render(request, 'core/home.html', context) 
#render(request, template_name, context): Loads template, Injects data (context), Returns HttpResponse automatically

'''Let’s break this down:
URL → View → render() → HttpResponse → Browser

Request
An object containing:
    HTTP method (GET/POST)
    headers
    user data
HttpResponse
  Django’s way of sending text back to the browser

This function:
  takes a request
  returns a response
That’s a Django view'''