from django.urls import path 
from . import views

urlpatterns = [
    path("video/", views.video_call_view, name="video_call"),
    path("get-token/", views.get_agora_token, name="get_agora_token"),
]
