from django import forms
from .models import Documento

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['arquivo', 'nome_arquivo', 'tipo_arquivo', 'tipo_usuario', 'paciente']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.tamanho_arquivo = instance.arquivo.size  # pega o tamanho real do arquivo
        if commit:
            instance.save()
        return instance
