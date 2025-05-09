# Generated by Django 5.2 on 2025-04-16 16:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_arquivo', models.CharField(max_length=255)),
                ('tipo_arquivo', models.CharField(max_length=50)),
                ('tamanho_arquivo', models.PositiveIntegerField()),
                ('data_upload', models.DateTimeField(auto_now_add=True)),
                ('tipo_usuario', models.CharField(choices=[('medico', 'Médico'), ('paciente', 'Paciente')], max_length=10)),
                ('arquivo', models.FileField(upload_to='documentos/')),
                ('enviado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos_enviados', to=settings.AUTH_USER_MODEL)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos_recebidos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
