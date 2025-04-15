from django.contrib import admin
from .models import Chamada

@admin.register(Chamada)
class ChamadaAdmin(admin.ModelAdmin):
    list_display = ('canal', 'uid_medico', 'uid_paciente', 'inicio', 'fim')
    search_fields = ('canal', 'uid_medico', 'uid_paciente')
    list_filter = ('inicio', 'fim')