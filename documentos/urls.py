from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_documento, name='upload_documento'),
    path('lista/', views.lista_documentos, name='lista_documentos'),
]
