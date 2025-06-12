from django.urls import path
from . import views

app_name = 'chamadas'

urlpatterns = [
    path('get_rtc_token/', views.get_agora_rtc_token, name='get_agora_rtc_token'),
    path('call/<str:channel_name>/', views.video_call_page, name='video_call_page'), # Página da chamada

    # API para controle de gravação
    path('api/start_recording/', views.iniciar_gravacao_nuvem, name='api_start_recording'),
    path('api/stop_recording/', views.parar_gravacao_nuvem, name='api_stop_recording'),
    
    # Webhook da Agora
    path('agora_recording_webhook/', views.agora_recording_webhook, name='agora_recording_webhook'),
]