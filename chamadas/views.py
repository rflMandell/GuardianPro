from django.shortcuts import render
import time 
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from agora_token_builder import RtcTokenBuilder
from .agora_token import generate_agora_token
from django.conf import settings
from django.shortcuts import render

# Create your views here.
@csrf_exempt
def gerar_token(request):
    app_id = settings.AGORA_APP_ID
    app_certificate = settings.AGORA_APP_CERTIFICATE
    channel_name = request.GET.get('channel')
    uid = random.randint(1,230)
    role = 1 # 1 = publisher (medico)
    expire_time = 3600
    
    current_time = int(time.time())
    privilege_expired_ts = current_time + expire_time
    
    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channel_name, uid, role, privilege_expired_ts
    )
    
    return JsonResponse({'token': token, 'uid': uid, 'appID': app_id})

def video_call_view(request):
    return render(request, 'chamadas/video_call.html', {"AGORA_APP_ID": settings.AGORA_APP_ID})

def get_agora_token(request):
    channel_name = request.GET.get("channel")
    if not channel_name:
        return JsonResponse({"error": "Canal nao especificado"}, status=400)

    token = generate_agora_token(channel_name)
    return JsonResponse({"token": token})