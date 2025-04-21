from django.contrib import admin
from .models import Chamada

@admin.register(Chamada)
class ChamadaAdmin(admin.ModelAdmin):
    list_display = ('id', 'canal', 'timestamp_inicio', 'timestamp_fim')  # corrige aqui
    list_filter = ('timestamp_inicio', 'timestamp_fim')  # corrige aqui
    search_fields = ('canal',)
