from django.contrib import admin

from .models import Disease


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'plant', 'is_healthy')
    search_fields = ('name', 'plant')
