from django.contrib import admin
'''Register models for admin panel'''

from .models import Student

admin.site.register(Student)

