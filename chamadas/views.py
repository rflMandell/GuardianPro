import time 
import random

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from agora_token_builder import RtcTokenBuilder

# Create your views here.
@csrf_exempt
def get_agora_token(request):
    app_id = settings.AGORA_APP_ID
    app_certificate = settings.AGORA_APP_CERTIFICATE
    
    channel_name = request.GET.get("channel")
    if not channel_name:
        return JsonResponse({"error": "Canal nao especificado"}, status=400)
    
    uid = random.randint(1, 9999)
    role = 1 #1 = publisher
    expire_time_seconds = 3600
    
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expire_time_seconds
    
    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channel_name, uid, role, privilege_expired_ts
    )


    return JsonResponse({
        "token": token,
        "uid": uid,
        "appID": app_id
    })

def video_call_view(request):
    return render(request, "chamadas/video_call.html", {
        "AGORA_APP_ID": settings.AGORA_APP_ID
    })