from django.contrib import admin

from .models import *

admin.site.register(Airline)
admin.site.register(Flight)
admin.site.register(CustomUser)
