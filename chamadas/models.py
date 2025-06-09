from django.db import models
from django.conf import settings
import os


class Chamada(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', "Pendente"),
        ('EM_ANDAMENTO', "Em Andamento"),
        ('GRAVANDO', 'Gravando'),
        ('PROCESSANDO_GRAVACAO', 'Processando Gravacao'),
        ('GRAVADA_AGUARDANDO_LAUDO', 'Gravada - Aguardando Laudo'),
        ('LAUDO_EM_PROCESSAMENTO', 'Laudo em Processamento'),
        ('CANCELADA', 'Cancelada'),
        ('ERRO_GRAVACAO', 'Erro na Gravacao'),
    ]
    
    canal = models.CharField(max_length=255, unique=True, help_text="Nome unico do canal de chamada")
    # token = models.TextField() #nao preciso mais (eu acho) salvar o token por ser de pouca duracao
    timestamp_inicio = models.DateTimeField(auto_now_add=True)
    timestamp_fim = models.DateTimeField(blank=True, null=True)
    duracao_segundos = models.PositiveIntegerField(blank=True, null=True)
    
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='chamadas_como_medico',
        on_delete=models.CASCADE,
        null=True
    )
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='chamadas_como_paciente',
        on_delete=models.CASCADE,
        blank=True
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDENTE')
    
    #campos para gravacao da AGORA.IO
    agora_resource_id = models.CharField(max_length=255, blank=True, null=True, help_text="Resourse ID da gravacao AGORA")
    agora_recording_sid = models.CharField(max_length=255, blank=True, null=True, help_text="SID da gravacao AGORA")
    agora_recording_uid = models.CharField(max_length=255, blank=True, null=True, help_text="UID usado para o bot de gravacao AGORA")
    
    arquivo_audio_gravado = models.FileField(
        upload_to='gravacoes_chamada/%Y/%m/%d/', #teoricamente vai salvar na MEDIA_ROOT/gravacoes_chamadas/ANO/MES/DIA
        blank= True,
        null= True,
    )

    def __str__(self):
        return f"Chamada {self.canal} ({self.get_status_display()})- {self.timestamp_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *arg, **kwargs):
        #logica para limpar arquivos antigos se um novo for salvo
        try:
            if self.id: #vai ver se o arquivo ja existe
                old_obj = Chamada.objects.get(id=self.id)
                if old_obj.arquivo_audio_gravado and self.arquivo_audio_gravado != old_obj:
                    if os.path.isfile(old_obj.arquivo_audio_gravado.path):
                        os.remove(old_obj.arquivo_audio_gravado.path)
        except Chamada.DoesNotExist:
            pass #obj e novo
        super().save(*arg, **kwargs)
        
    def delete(self, *arg, **kwargs):
        if self.arquivo_audio_gravado:
            if os.path.isfile(self.arquivo_audio_gravado.path):
                os.remove(self.arquivo_audio_gravado.path)
        super().delete(*arg, **kwargs)
