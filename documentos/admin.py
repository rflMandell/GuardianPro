from django.contrib import admin
from .models import Documento

# Register your models here.

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nome_arquivo', 'tipo_arquivo', 'tamanho_arquivo', 'data_upload', 'enviado_por', 'tipo_usuario', 'paciente')
    list_filter = ('tipo_usuario', 'data_upload')
    search_fields = ('nome_arquivo', 'enviado_por__username', 'paciente__username')
    date_hierarchy = 'data_upload'