from django.db import models
from django.conf import settings

class Documento(models.Model):
    MEDICO = 'medico'
    PACIENTE = 'paciente'

    TIPO_USUARIO_CHOICES = [
        (MEDICO, 'Médico'),
        (PACIENTE, 'Paciente'),
    ]

    nome_arquivo = models.CharField(max_length=255)
    tipo_arquivo = models.CharField(max_length=50)
    tamanho_arquivo = models.PositiveIntegerField()
    data_upload = models.DateTimeField(auto_now_add=True)

    # Campo opcional, se quiser usar depois
    # enviado_por = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name='documentos_enviados'
    # )

    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES)

    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documentos_recebidos'
    )

    arquivo = models.FileField(upload_to='documentos/')

    def __str__(self):
        return f"{self.nome_arquivo} - {self.data_upload.strftime('%d/%m/%Y %H:%M')}"
