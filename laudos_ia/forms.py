from django import forms
from .models import LaudoMedico

class LaudoMedicoEditForm(forms.ModelForm):
    class Meta:
        model = LaudoMedico
        fields = ['laudo_final_editado'] # o campo que o médico vai editar
        widgets = {
            'laudo_final_editado': forms.Textarea(attrs={'rows': 20, 'cols': 80, 'class': 'form-control'}),
        }
        labels = {
            'laudo_final_editado': 'Laudo Médico Finalizado',
        }
        help_texts = {
            'laudo_final_editado': 'Revise e edite o laudo abaixo. Este será o texto final salvo.',
        }