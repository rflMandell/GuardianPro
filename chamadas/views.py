import time 
import random
import requests
import json
import base64
import os #para os path.basename do os

from django.conf import settings
from django.http import JsonResponse, HttpRequest, HttpResponseForbidden, Http404
from django.shortcuts import render, get_list_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone #para timestamp_fim
from django.core.files.base import ContentFile

# from django.contrib.auth.decorators import login_required # em breve

from agora_token_builder import RtcTokenBuilder
from .models import Chamada
from laudos_ia.models import LaudoMedico #para criar o laudo apos a gravacao

# import os servicos de IA
from laudos_ia.services import iniciar_processamento_laudo_async

# configuracoes da apirest da AGORA
AGORA_API_BASE_URL = "https://api.agora.io"

def get_agora_rest_api_auth_headers():
    customer_id = settings.AGORA_CUSTOMER_ID
    customer_secret = settings.AGORA_CUSTOMER_SECRET
    
    if not customer_id or not customer_secret:
        #log error or raise exception - critical for API calls
        print("ERRO CRITICO: AGORA_CUSTOMER_ID ou AGORA_CUSTOMER_SECRET nao configurado")
        return None
    cedentials = f"{customer_id}:{customer_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return{
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'aplication/json'
    }

# -- Views de Chamada e Token RTC --

@csrf_exempt #para simplificar

def get_agora_rtc_token(request):
    app_id = settings.AGORA_APP_ID