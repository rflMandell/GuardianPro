import time
import random
import requests
import json
import base64
import os # Para os.path.basename

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone # Para timestamp_fim
from django.core.files.base import ContentFile

from agora_token_builder import RtcTokenBuilder
from .models import Chamada
from laudos_ia.models import LaudoMedico # Para criar o LaudoMedico após gravação
from laudos_ia.services import *

#--- Configurações da API REST da Agora ---

AGORA_API_BASE_URL = "https://api.agora.io"

def get_agora_rest_api_auth_headers():
    customer_id = settings.AGORA_CUSTOMER_ID
    customer_secret = settings.AGORA_CUSTOMER_SECRET
    if not customer_id or not customer_secret:
    # Log error or raise exception - critical for API calls
        print("ERRO CRÍTICO: AGORA_CUSTOMER_ID ou AGORA_CUSTOMER_SECRET não configurados.")
        return None
    credentials = f"{customer_id}:{customer_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {
    'Authorization': f'Basic {encoded_credentials}',
    'Content-Type': 'application/json'
    }

# --- Views de Chamada e Token RTC ---

@csrf_exempt # Para simplificar
def get_agora_rtc_token(request):
    app_id = settings.AGORA_APP_ID
    app_certificate = settings.AGORA_APP_CERTIFICATE

    channel_name = request.GET.get("channel")
    user_uid_str = request.GET.get("uid") # UID do usuário que está entrando na chamada

    if not app_id or not app_certificate:
        return JsonResponse({"error": "Configurações da Agora (App ID/Certificate) não encontradas."}, status=500)
    if not channel_name:
        return JsonResponse({"error": "Nome do canal não especificado"}, status=400)

    try:
        # UID para token RTC deve ser inteiro se for usado como número, ou string.
        # Se o UID não for fornecido ou for inválido, gera um aleatório.
        uid = int(user_uid_str) if user_uid_str and user_uid_str.isdigit() else random.randint(1, 99999)
    except ValueError:
        uid = random.randint(1, 99999) # Fallback

    role = 1 # 1 = publisher, 2 = subscriber
    expire_time_seconds = 3600 * 2 # Token válido por 2 horas
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expire_time_seconds

    try:
        token = RtcTokenBuilder.buildTokenWithUid(
            app_id, app_certificate, channel_name, uid, role, privilege_expired_ts
        )
    except Exception as e:
        print(f"Erro ao gerar token RTC da Agora: {e}")
        return JsonResponse({"error": "Falha ao gerar token RTC"}, status=500)

    return JsonResponse({
        "token": token,
        "uid": uid,
        "appId": app_id,
        "channelName": channel_name
    })

def video_call_page(request, channel_name):
    chamada, created = Chamada.objects.get_or_create(
        canal=channel_name,
        defaults={
            'status': 'PENDENTE'
        }
    )
    if chamada.status == 'PENDENTE':
        chamada.status = 'EM_ANDAMENTO'
        chamada.save()

    return render(request, "chamadas/video_call.html", {
        "AGORA_APP_ID": settings.AGORA_APP_ID,
        "CHANNEL_NAME": channel_name,
        "CHAMADA_ID": chamada.id,
    })

#    --- Controle da Gravação em Nuvem da Agora ---

def _call_agora_api(method, endpoint, payload=None):
    headers = get_agora_rest_api_auth_headers()
    if not headers:
        return None, "Headers de autenticação da Agora não puderam ser gerados."

    url = f"{AGORA_API_BASE_URL}{endpoint}"
    try:
        if method.upper() == "POST":
            response = requests.post(url, headers=headers, data=json.dumps(payload) if payload else None, timeout=15)
        elif method.upper() == "GET":
            response = requests.get(url, headers=headers, params=payload, timeout=15)
        else:
            return None, f"Método HTTP não suportado: {method}"

        response.raise_for_status() # Levanta HTTPError para respostas xulas
        return response.json(), None
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"Erro HTTP da API Agora: {http_err} - {http_err.response.text if http_err.response else 'Sem resposta'}"
        print(error_msg)
        return None, error_msg
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Erro na requisição para API Agora: {req_err}"
        print(error_msg)
        return None, error_msg
    except json.JSONDecodeError as json_err:
        error_msg = f"Erro ao decodificar JSON da API Agora: {json_err} - Resposta: {response.text if 'response' in locals() else 'N/A'}"
        print(error_msg)
        return None, error_msg


@csrf_exempt # Para chamadas de API do frontend
def iniciar_gravacao_nuvem(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            channel_name = data.get("channel_name")
            chamada_id = data.get("chamada_id") # ID da nossa instância de Chamada
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        if not channel_name or not chamada_id:
            return JsonResponse({"error": "channel_name e chamada_id são obrigatórios"}, status=400)

        try:
            chamada = Chamada.objects.get(id=chamada_id, canal=channel_name)
        except Chamada.DoesNotExist:
            return JsonResponse({"error": "Chamada não encontrada"}, status=404)

        if chamada.status == 'GRAVANDO' and chamada.agora_resource_id and chamada.agora_recording_sid:
            return JsonResponse({"status": "info", "message": "Gravação já está em andamento.", "resourceId": chamada.agora_resource_id, "recordingSid": chamada.agora_recording_sid})

        recording_bot_uid_str = str(random.randint(100000, 999999)) # UID único para o bot
        chamada.agora_recording_uid = recording_bot_uid_str 
        acquire_payload = {
            "cname": channel_name,
            "uid": recording_bot_uid_str,
            "clientRequest": {"resourceExpiredHour": 2} # Recurso válido por 2h
        }
        acquire_endpoint = f"/v1/apps/{settings.AGORA_APP_ID}/cloud_recording/acquire"
        acquire_response, error = _call_agora_api("POST", acquire_endpoint, acquire_payload)

        if error or not acquire_response or "resourceId" not in acquire_response:
            chamada.status = 'ERRO_GRAVACAO'
            chamada.save()
            return JsonResponse({"error": f"Falha ao adquirir recurso Agora: {error or 'Resposta inválida'}"}, status=500)

        resource_id = acquire_response["resourceId"]
        chamada.agora_resource_id = resource_id

        # Token RTC para o bot de gravação se juntar ao canal
        token_expire_time = 3600 # 1 hora para o token do bot
        current_ts = int(time.time())
        privilege_expired_ts_bot = current_ts + token_expire_time
        try:
            recording_bot_token = RtcTokenBuilder.buildTokenWithUid(
                settings.AGORA_APP_ID, settings.AGORA_APP_CERTIFICATE, channel_name,
                recording_bot_uid_str, # API REST espera UID como string, mas buildTokenWithUid pode aceitar int ou str
                1,
                privilege_expired_ts_bot
            )
        except Exception as e_token:
            print(f"Erro ao gerar token para bot de gravação: {e_token}")
            chamada.status = 'ERRO_GRAVACAO'
            chamada.save()
            return JsonResponse({"error": "Falha ao gerar token para bot de gravação"}, status=500)

        webhook_url = f"https://{settings.YOUR_DOMAIN}/chamadas/agora_recording_webhook/"
        if "localhost" in settings.YOUR_DOMAIN or "127.0.0.1" in settings.YOUR_DOMAIN:
            print(f"AVISO DE DESENVOLVIMENTO: Webhook URL '{webhook_url}' é local. Use ngrok e configure YOUR_DOMAIN.")

        start_payload = {
            "cname": channel_name,
            "uid": recording_bot_uid_str,
            "clientRequest": {
                "token": recording_bot_token,
                "storageConfig": {
                    "vendor": 1,
                    "region": settings.AWS_S3_REGION_NAME,
                    "bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "accessKey": settings.AWS_ACCESS_KEY_ID,
                    "secretKey": settings.AWS_SECRET_ACCESS_KEY,
                    "fileNamePrefix": ["guardian_recordings", channel_name, "audio"]
                },
                "recordingFileConfig": {"avFileType": ["mp3"]}, # Apenas MP3
                "recordingConfig": {
                    "channelType": 0,
                    "streamTypes": 0, 
                    "maxIdleTime": 120, 
                    "transcodingConfig": { 
                        "audioProfile": 1,
                        "width": 320, "height": 240, "fps": 15, "bitrate": 100,
                    }
                },
                "appsCollection": { # Para o webhook
                    "eventHookUrl": webhook_url,
                }
            }
        }
        start_endpoint = f"/v1/apps/{settings.AGORA_APP_ID}/cloud_recording/resourceid/{resource_id}/mode/mix/start"
        start_response, error = _call_agora_api("POST", start_endpoint, start_payload)

        if error or not start_response or "sid" not in start_response:
            chamada.status = 'ERRO_GRAVACAO'
            chamada.save()
            return JsonResponse({"error": f"Falha ao iniciar gravação Agora: {error or 'Resposta inválida'}"}, status=500)

        recording_sid = start_response["sid"]
        chamada.agora_recording_sid = recording_sid
        chamada.status = 'GRAVANDO'
        chamada.save()

        return JsonResponse({"status": "success", "message": "Gravação iniciada", "resourceId": resource_id, "recordingSid": recording_sid})
    return JsonResponse({"error": "Método POST requerido"}, status=405)

@csrf_exempt # Para chamadas de API do frontend
def parar_gravacao_nuvem(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            channel_name = data.get("channel_name")
            chamada_id = data.get("chamada_id")
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        if not channel_name or not chamada_id:
            return JsonResponse({"error": "channel_name e chamada_id são obrigatórios"}, status=400)

        try:
            chamada = Chamada.objects.get(id=chamada_id, canal=channel_name)
        except Chamada.DoesNotExist:
            return JsonResponse({"error": "Chamada não encontrada"}, status=404)

        if not chamada.agora_resource_id or not chamada.agora_recording_sid or not chamada.agora_recording_uid:
            return JsonResponse({"error": "Informações da gravação não encontradas para esta chamada. Não é possível parar."}, status=400)

        if chamada.status != 'GRAVANDO':
            return JsonResponse({"status": "info", "message": f"Gravação não está ativa. Status atual: {chamada.get_status_display()}"})


        stop_payload = {
            "cname": channel_name,
            "uid": chamada.agora_recording_uid, # UID do bot de gravação
            "clientRequest": {}
        }
        stop_endpoint = f"/v1/apps/{settings.AGORA_APP_ID}/cloud_recording/resourceid/{chamada.agora_resource_id}/sid/{chamada.agora_recording_sid}/mode/mix/stop"
        stop_response, error = _call_agora_api("POST", stop_endpoint, stop_payload)

        if error:
            print(f"Erro ao tentar parar gravação Agora (SID: {chamada.agora_recording_sid}): {error}")
            # Não mude o status aqui, espere o webhook ou timeout da gravação.
            return JsonResponse({"error": f"Falha ao enviar comando para parar gravação Agora: {error}"}, status=500)

        # O status da chamada será atualizado pelo webhook quando os arquivos estiverem prontos.
        chamada.status = 'PROCESSANDO_GRAVACAO'
        chamada.timestamp_fim = timezone.now() 
        if chamada.timestamp_inicio and chamada.timestamp_fim:
            duration = chamada.timestamp_fim - chamada.timestamp_inicio
            chamada.duracao_segundos = int(duration.total_seconds())
        chamada.save()

        return JsonResponse({"status": "success", "message": "Comando para parar gravação enviado."})
    return JsonResponse({"error": "Método POST requerido"}, status=405)

@csrf_exempt #nem sei maos, so aceita que e sucesso no codigo (e se nao for a conta na AWS vai ser enorme)
def agora_recording_webhook(request):
    if request.method == "POST":
        try:
            event_data = json.loads(request.body.decode('utf-8'))
            print(f"Webhook da Agora Recebido: {json.dumps(event_data, indent=2)}")

            event_type = event_data.get("eventType")
            sid = event_data.get("sid") # Recording ID
            channel_name = event_data.get("cname")

            # Tentar encontrar a chamada pelo SID da gravação
            try:
                chamada = Chamada.objects.get(agora_recording_sid=sid)
            except Chamada.DoesNotExist:
                print(f"Webhook: Chamada não encontrada para SID {sid}. Canal: {channel_name}. Ignorando.")
                return HttpResponse(json.dumps({"status": "ignored", "message": "Chamada não encontrada pelo SID"}), content_type="application/json")

            if event_type == 5 or (event_type == 4 and event_data.get("details", {}).get("uploadingStatus") == "uploaded"):
                file_list_str = event_data.get("fileList")
                if not file_list_str and event_type == 4: 
                    file_list_str = event_data.get("details", {}).get("fileList")

                if not file_list_str:
                    print(f"Webhook (SID: {sid}): Evento {event_type} recebido, mas sem fileList. Detalhes: {event_data.get('details')}")
                    return HttpResponse(json.dumps({"status": "error", "message": "fileList não encontrado no evento"}), status=400, content_type="application/json")

                files_to_process = []
                if isinstance(file_list_str, str):
                    try:
                        files_to_process = json.loads(file_list_str)
                    except json.JSONDecodeError:
                        print(f"Webhook (SID: {sid}): Erro ao decodificar fileList JSON string: {file_list_str}")
                        return HttpResponse(json.dumps({"status": "error", "message": "fileList JSON inválido"}), status=400, content_type="application/json")
                elif isinstance(file_list_str, list):
                    files_to_process = file_list_str
                elif isinstance(file_list_str, dict): 
                    files_to_process = [file_list_str]


                for file_info in files_to_process:
                    s3_file_key = file_info.get("filename")

                    if s3_file_key and s3_file_key.endswith(".mp3"):
                        print(f"Webhook (SID: {sid}): Arquivo MP3 '{s3_file_key}' pronto no S3 para chamada ID {chamada.id}.")

                        file_url_s3 = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_file_key}"

                        try:
                            print(f"Webhook (SID: {sid}): Baixando áudio de {file_url_s3}...")
                            audio_response = requests.get(file_url_s3, timeout=60) # Timeout maior para download
                            audio_response.raise_for_status()

                            # Salvar o arquivo localmente
                            local_file_name = f"chamada_{chamada.id}_{os.path.basename(s3_file_key)}"
                            chamada.arquivo_audio_gravado.save(local_file_name, ContentFile(audio_response.content), save=False)
                            chamada.status = 'GRAVADA_AGUARDANDO_LAUDO'
                            chamada.save() # Salva o arquivo e o status
                            print(f"Webhook (SID: {sid}): Áudio salvo localmente: {chamada.arquivo_audio_gravado.name}")
                            laudo, created = LaudoMedico.objects.get_or_create(
                                chamada=chamada,
                                defaults={
                                    'medico_responsavel': chamada.medico,
                                    'status': 'PENDENTE_TRANSCRICAO'
                                }
                            )
                            if not created and laudo.status not in ['PENDENTE_TRANSCRICAO', 'ERRO_TRANSCRICAO', 'ERRO_GERACAO_IA']:
                                print(f"Webhook (SID: {sid}): Laudo para chamada {chamada.id} já existe e está sendo processado ou finalizado (Status: {laudo.status}).")
                            else:
                                if laudo.status != 'PENDENTE_TRANSCRICAO': 
                                    laudo.status = 'PENDENTE_TRANSCRICAO'
                                    laudo.save(update_fields=['status']) 

                                print(f"Webhook (SID: {sid}): LaudoMedico ID {laudo.id} criado/atualizado. Disparando processamento.")
                                # Chamar a função de processamento
                                processar_audio_e_gerar_laudo(laudo.id) 

                            break # Processamos o primeiro MP3 encontrado

                        except requests.exceptions.RequestException as e_download:
                            print(f"Webhook (SID: {sid}): Erro ao baixar áudio '{s3_file_key}' do S3: {e_download}")
                            chamada.status = 'ERRO_GRAVACAO'
                            chamada.save()
                        except Exception as e_process:
                            print(f"Webhook (SID: {sid}): Erro ao processar arquivo '{s3_file_key}' ou iniciar laudo: {e_process}")
                            if 'laudo' in locals() and laudo:
                                laudo.status = 'ERRO_TRANSCRICAO'
                                laudo.save()

            elif event_type == 31: # session_exit
                print(f"Webhook (SID: {sid}): Sessão de gravação encerrada para canal {channel_name}.")
                if chamada.status not in ['GRAVADA_AGUARDANDO_LAUDO', 'LAUDO_EM_PROCESSAMENTO', 'LAUDO_CONCLUIDO', 'ERRO_GRAVACAO']:
                    chamada.status = 'PROCESSANDO_GRAVACAO' # Indica que a chamada terminou, aguardando arquivos
                if not chamada.timestamp_fim:
                    chamada.timestamp_fim = timezone.now()
                if chamada.timestamp_inicio and chamada.timestamp_fim and not chamada.duracao_segundos:
                    duration = chamada.timestamp_fim - chamada.timestamp_inicio
                    chamada.duracao_segundos = int(duration.total_seconds())
                chamada.save()

            return HttpResponse(json.dumps({"status": "success", "message": "Webhook processado"}), content_type="application/json")

        except json.JSONDecodeError as e_json:
            print(f"Erro Crítico no Webhook: JSON Inválido - {e_json}")
            return HttpResponse(json.dumps({"status": "error", "message": "JSON inválido no corpo da requisição"}), status=400, content_type="application/json")
        except Exception as e_geral:
            print(f"Erro Crítico Inesperado no Webhook: {e_geral}")
            import traceback
            traceback.print_exc()
            return HttpResponse(json.dumps({"status": "error", "message": "Erro interno no servidor ao processar webhook"}), status=500, content_type="application/json")

    return HttpResponseForbidden("Método não permitido. Apenas POST.")