from django.contrib import admin
from .models import Documento

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome_arquivo', 'tipo_arquivo', 'tamanho_arquivo', 'data_upload', 'tipo_usuario', 'paciente')
    list_filter = ('tipo_usuario', 'data_upload')
    search_fields = ('nome_arquivo', 'paciente__username')
    date_hierarchy = 'data_upload'
