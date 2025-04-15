from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Gravacao(models.Model)Ç
    canal = models.CharField(max_length=100)
    uid_medico = models.CharField(max_length=100)
    uid_paciente = models.CharField(max_length=100)
    timestamp_incio = models.DateTimeField()
    timestamp_fim = models.DateTimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    
    medico = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='gravacoes_medico'
    )
    paciente = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='gravacoes_paciente'
    )
    
    def __str__(self):
        return f"Chamada {self.canal} - {self.timestamp_inicio.strtime('%d/%m/%Y %H:%M')}"