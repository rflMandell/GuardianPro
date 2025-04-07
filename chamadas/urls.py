from django.urls import path 
from .views import gerar_token, video_call_view

urlpatterns = [
    path("token/", gerar_token, name="gerar_token"),
    path("video/", video_call_view, name="video_call"),
]
