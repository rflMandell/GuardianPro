import openai
from django.conf import settings
from .models import LaudoMedico
from chamadas.models import Chamada


try:
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    openai.api_key = settings.OPENAI_API_KEY
except AttributeError:
    print("AVISO: OPENAI_API_KEY não configurada nas settings. O cliente OpenAI não foi inicializado.")
    client = None
except Exception as e:
    print(f"AVISO: Erro ao inicializar cliente OpenAI: {e}. Verifique sua instalação e API Key.")
    client = None


def transcrever_audio_com_whisper(laudo_id):
    """
    Transcreve o áudio associado a um LaudoMedico usando a API Whisper da OpenAI.
    Atualiza o LaudoMedico com a transcrição ou status de erro.
    """
    if not client:
        print(f"Laudo ID {laudo_id}: Cliente OpenAI não inicializado. Transcrição abortada.")
        try:
            laudo = LaudoMedico.objects.get(id=laudo_id)
            laudo.status = 'ERRO_TRANSCRICAO'
            laudo.transcricao_texto = "Erro: Cliente OpenAI não configurado."
            laudo.save()
        except LaudoMedico.DoesNotExist:
            pass # Laudo não existe, não há o que fazer
        return None

    try:
        laudo = LaudoMedico.objects.get(id=laudo_id)
    except LaudoMedico.DoesNotExist:
        print(f"Erro: LaudoMedico com ID {laudo_id} não encontrado para transcrição.")
        return None

    if not laudo.chamada or not laudo.chamada.arquivo_audio_gravado:
        print(f"Erro: LaudoMedico ID {laudo_id} não tem áudio associado para transcrever.")
        laudo.status = 'ERRO_TRANSCRICAO'
        laudo.transcricao_texto = "Erro: Arquivo de áudio não encontrado."
        laudo.save()
        return None

    audio_file_path = laudo.chamada.arquivo_audio_gravado.path
    laudo.status = 'TRANSCREVENDO'
    laudo.save()

    try:
        with open(audio_file_path, "rb") as audio_file:
            transcription_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text" # Pode ser 'json', 'text', 'srt', 'verbose_json', ou 'vtt'
            )
        transcricao = transcription_response if isinstance(transcription_response, str) else transcription_response.text

        laudo.transcricao_texto = transcricao
        laudo.status = 'PENDENTE_GERACAO_IA' # Próximo passo
        laudo.save()
        print(f"Laudo ID {laudo.id}: Transcrição concluída com sucesso.")
        return transcricao
    except openai.APIError as e:
        print(f"Erro da API OpenAI (Whisper) para Laudo ID {laudo.id}: {e}")
        laudo.status = 'ERRO_TRANSCRICAO'
        laudo.transcricao_texto = f"Erro na API Whisper: {e}"
        laudo.save()
    except FileNotFoundError:
        print(f"Erro: Arquivo de áudio não encontrado em {audio_file_path} para Laudo ID {laudo.id}.")
        laudo.status = 'ERRO_TRANSCRICAO'
        laudo.transcricao_texto = "Erro: Arquivo de áudio não encontrado no servidor."
        laudo.save()
    except Exception as e:
        print(f"Erro inesperado durante a transcrição para Laudo ID {laudo.id}: {e}")
        laudo.status = 'ERRO_TRANSCRICAO'
        laudo.transcricao_texto = f"Erro inesperado: {e}"
        laudo.save()
    return None


def gerar_laudo_com_gpt(laudo_id, modelo_gpt="gpt-3.5-turbo"):
    """
    Gera um laudo médico preliminar usando a API da OpenAI com base na transcrição.
    Atualiza o LaudoMedico com o laudo gerado ou status de erro.
    """
    if not client:
        print(f"Laudo ID {laudo_id}: Cliente OpenAI não inicializado. Geração de laudo abortada.")
        try:
            laudo = LaudoMedico.objects.get(id=laudo_id)
            laudo.status = 'ERRO_GERACAO_IA'
            laudo.laudo_preliminar_ia = "Erro: Cliente OpenAI não configurado."
            laudo.save()
        except LaudoMedico.DoesNotExist:
            pass
        return None

    try:
        laudo = LaudoMedico.objects.get(id=laudo_id)
    except LaudoMedico.DoesNotExist:
        print(f"Erro: LaudoMedico com ID {laudo_id} não encontrado para geração de laudo.")
        return None

    if not laudo.transcricao_texto:
        print(f"Erro: LaudoMedico ID {laudo.id} não tem transcrição para gerar laudo.")
        laudo.status = 'ERRO_GERACAO_IA'
        laudo.laudo_preliminar_ia = "Erro: Transcrição não disponível."
        laudo.save()
        return None

    laudo.status = 'GERANDO_IA'
    laudo.save()

    # Prompt para o GPT
    prompt_template = f"""
    Você é um assistente médico especializado em gerar laudos concisos a partir de transcrições de consultas.
    A seguir, a transcrição de uma consulta médica:

    --- INÍCIO DA TRANSCRIÇÃO ---
    {laudo.transcricao_texto}
    --- FIM DA TRANSCRIÇÃO ---

    Com base nesta transcrição, gere um laudo médico preliminar. O laudo deve incluir, se possível:
    1.  Queixa Principal do Paciente.
    2.  Breve Histórico da Doença Atual.
    3.  Observações Relevantes do Exame (se mencionado).
    4.  Hipóteses Diagnósticas (se discutido).
    5.  Plano de Conduta ou Recomendações (se mencionado).

    Seja objetivo e use terminologia médica apropriada, mas de forma clara.
    Evite informações especulativas não presentes na transcrição.
    Formate o laudo de maneira organizada. Não inclua saudações ou despedidas.
    Comece diretamente com o conteúdo do laudo.
    """
    laudo.prompt_utilizado_ia = prompt_template # Salva o prompt exato

    try:
        completion_response = client.chat.completions.create(
            model=modelo_gpt,
            messages=[
                {"role": "system", "content": "Você é um assistente médico especializado em gerar laudos concisos a partir de transcrições de consultas."},
                {"role": "user", "content": prompt_template}
            ],
            temperature=0.5, # Ajuste para mais criatividade ou mais determinismo
            # max_tokens=1000 # Defina um limite se necessário
        )
        laudo_gerado = completion_response.choices[0].message.content.strip()

        # Para openai v0.x.x
        # completion_response = openai.ChatCompletion.create(
        #     model=modelo_gpt,
        #     messages=[
        #         {"role": "system", "content": "Você é um assistente médico especializado em gerar laudos concisos a partir de transcrições de consultas."},
        #         {"role": "user", "content": prompt_template}
        #     ]
        # )
        # laudo_gerado = completion_response.choices[0].message.content.strip()

        laudo.laudo_preliminar_ia = laudo_gerado
        laudo.modelo_ia_utilizado = modelo_gpt
        laudo.status = 'AGUARDANDO_REVISAO'
        laudo.save()
        print(f"Laudo ID {laudo.id}: Laudo preliminar gerado com sucesso usando {modelo_gpt}.")
        return laudo_gerado
    except openai.APIError as e:
        print(f"Erro da API OpenAI (GPT) para Laudo ID {laudo.id}: {e}")
        laudo.status = 'ERRO_GERACAO_IA'
        laudo.laudo_preliminar_ia = f"Erro na API GPT: {e}"
        laudo.save()
    except Exception as e:
        print(f"Erro inesperado durante a geração do laudo para Laudo ID {laudo.id}: {e}")
        laudo.status = 'ERRO_GERACAO_IA'
        laudo.laudo_preliminar_ia = f"Erro inesperado: {e}"
        laudo.save()
    return None


def processar_audio_e_gerar_laudo(laudo_id):
    """
    processo de transcrição de áudio e geração de laudo para um LaudoMedico.
    """
    print(f"Iniciando processamento completo para Laudo ID: {laudo_id}")
    try:
        laudo = LaudoMedico.objects.get(id=laudo_id)
    except LaudoMedico.DoesNotExist:
        print(f"Processamento abortado: LaudoMedico com ID {laudo_id} não encontrado.")
        return

    if laudo.status in ['PENDENTE_TRANSCRICAO', 'ERRO_TRANSCRICAO']:
        print(f"Laudo ID {laudo_id}: Iniciando etapa de transcrição...")
        transcricao = transcrever_audio_com_whisper(laudo_id)
        if not transcricao:
            print(f"Laudo ID {laudo_id}: Falha na transcrição. Processo interrompido.")
            return
        # Atualiza o status da chamada principal
        laudo.chamada.status = 'LAUDO_EM_PROCESSAMENTO'
        laudo.chamada.save()
    elif not laudo.transcricao_texto:
        print(f"Laudo ID {laudo_id}: Transcrição não disponível, mas status não é pendente/erro. Verifique.")
        laudo.status = 'ERRO_TRANSCRICAO' # Força um erro para reprocessar se necessário
        laudo.save()
        return

    # Recarrega o laudo para pegar o status atualizado pela transcrição
    laudo.refresh_from_db()
    if laudo.status in ['PENDENTE_GERACAO_IA', 'ERRO_GERACAO_IA']:
        print(f"Laudo ID {laudo.id}: Iniciando etapa de geração de laudo com GPT...")
        laudo_gerado = gerar_laudo_com_gpt(laudo_id) # Pode especificar o modelo aqui se quiser
        if not laudo_gerado:
            print(f"Laudo ID {laudo.id}: Falha na geração do laudo com GPT. Processo interrompido.")
            return
        # Atualiza o status da chamada principal
        laudo.chamada.status = 'LAUDO_CONCLUIDO'
        laudo.chamada.save()

    print(f"Laudo ID {laudo_id}: Processamento concluído. Status final do laudo: {laudo.get_status_display()}")