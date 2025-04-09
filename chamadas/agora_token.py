from agora_token_builder import RtcTokenBuilder
from django.conf import settings
import time

def generate_agora_token(channel_name, uid=0):
    expiration = 3600
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration
    
    token = RtcTokenBuilder.buildTokenWithUid(
        settings.AGORA_APP_ID,
        settings.AGORA_APP_CERTIFICATE,
        channel_name,
        uid,
        1,
        privilege_expired_ts
    )
    return token