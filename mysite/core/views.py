"""Where request logic lives
Functions or classes that return responses"""

from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello, Django!")

'''Let’s break this down:
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