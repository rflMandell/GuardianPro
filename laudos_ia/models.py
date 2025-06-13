from django.db import models
from django.conf import settings
# from chamadas.models import Chamada #tentando prevenir circularidade

# Create your models here.
class LaudoMedico(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE_TRANSCRICAO', 'Pendente Transcrição'),
        ('TRANSCREVENDO', 'Transcrevendo'),
        ('ERRO_TRANSCRICAO', 'Erro na Transcrição'),
        ('PENDENTE_GERACAO_IA', 'Pendente Geração IA'),
        ('GERANDO_IA', 'Gerando Laudo IA'),
        ('ERRO_GERACAO_IA', 'Erro na Geração IA'),
        ('AGUARDANDO_REVISAO', 'Aguardando Revisão Médica'),
        ('REVISADO_FINALIZADO', 'Revisado e Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    chamada = models.OneToOneField(
        'chamadas.Chamada',
        on_delete=models.CASCADE, #se a chamada for deletada o laudo tbm e // talvez eu mude isso pq n faz muito sentido
        related_name = 'laudo_medico',
        help_text="Chamada associada a este laudo"
        )
    medico_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='laudos_sob_resposabilidade',
        help_text='Medico que revisou ou e responsavel pelo laudo'
    )
    
    transcricao_texto = models.TextField(blank=True, null=True, help_text="Texto transcrito do audio")
    laudo_preliminar_ia = models.TextField(blank=True, null=True, help_text="Laudo gerado por Inteligencia Artificial antes de revisao humana")
    laudo_final_editado = models.TextField(blank=True, null=True, help_text="Laudo final apos edicao do medico responsavel")
    
    prompt_utilizado_ia = models.TextField(blank=True, null=True, help_text="Prompt exato enviado para a IA gerar o laudo")
    modelo_ia_utilizado = models.CharField(max_length=100, blank=True, null=True, help_text="Modelo de IA utilizado gpt-3.5-turbo")
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_ultima_modificacao = models.DateTimeField(auto_now_add=True)
    data_finalizacao_revisao = models.DateTimeField(blank=True, null=True)
    
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='PENDENTE_TRANSCRICAO'
    )
    
    def __str__(self):
        return f"Laudo para Chamada ID {self.chamada.id} (Canal: {self.chamada.canal}) - Status: {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.medico_responsavel and self.chamada and self.chamada.medico:
            self.medico_responsavel = self.chamada.medico
        super().save(*args, **kwargs)