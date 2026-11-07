from django.contrib import admin

from .models import DairyCategory, DairyProduct, DairyService

admin.site.register((DairyCategory, DairyProduct, DairyService))
