from django.db import models
from django.conf import settings


class Chamada(models.Model):
    canal = models.CharField(max_length=255)
    token = models.TextField()
    timestamp_inicio = models.DateTimeField()
    timestamp_fim = models.DateTimeField(blank=True, null=True)
    duracao_segundos = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=50)
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='chamadas_como_medico',
        on_delete=models.CASCADE
    )
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='chamadas_como_paciente',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Chamada {self.canal} - {self.timestamp_inicio.strftime('%d/%m/%Y %H:%M')}"
