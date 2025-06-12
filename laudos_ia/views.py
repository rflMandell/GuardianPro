from django.shortcuts import render, get_object_or_404, redirect
#from django.contrib.auth.decorators import login_required # Importante para proteger as views
from django.utils import timezone
from django.urls import reverse
from .models import LaudoMedico
from .forms import LaudoMedicoEditForm
from django.contrib import messages 

def listar_laudos_pendentes(request):

    laudos = LaudoMedico.objects.filter(
        status='AGUARDANDO_REVISAO',
        medico_responsavel=request.user
    ).order_by('-data_criacao')

    context = {
        'laudos': laudos,
        'titulo_pagina': 'Laudos Pendentes de Revisão'
    }
    return render(request, 'laudos_ia/listar_laudos.html', context)

def listar_todos_laudos(request):
    # Lista todos os laudos associados ao médico logado ou todos para admin
    if request.user.is_superuser:
        laudos = LaudoMedico.objects.all().order_by('-data_criacao')
    else:
        laudos = LaudoMedico.objects.filter(
            medico_responsavel=request.user
        ).order_by('-data_criacao')
    
    context = {
        'laudos': laudos,
        'titulo_pagina': 'Todos os Meus Laudos'
    }
    return render(request, 'laudos_ia/listar_laudos.html', context)


def detalhe_laudo_medico(request, laudo_id):
    laudo = get_object_or_404(LaudoMedico, id=laudo_id)

    context = {
        'laudo': laudo,
    }
    return render(request, 'laudos_ia/detalhe_laudo.html', context)


def editar_laudo_medico(request, laudo_id):
    laudo = get_object_or_404(LaudoMedico, id=laudo_id)

    if laudo.status == 'REVISADO_FINALIZADO':
        messages.info(request, "Este laudo já foi finalizado e não pode ser editado novamente.")
        return redirect(reverse('laudos_ia:detalhe_laudo_medico', args=[laudo_id]))

    if request.method == 'POST':
        form = LaudoMedicoEditForm(request.POST, instance=laudo)
        if form.is_valid():
            laudo_editado = form.save(commit=False)
            laudo_editado.status = 'REVISADO_FINALIZADO'
            laudo_editado.data_finalizacao_revisao = timezone.now()
            # O médico que edita/salva pode ser diferente do 'medico_responsavel' inicial
            laudo_editado.save()
            
            if laudo_editado.chamada:
                laudo_editado.chamada.status = 'LAUDO_CONCLUIDO'
                laudo_editado.chamada.save(update_fields=['status'])

            messages.success(request, "Laudo salvo e finalizado com sucesso!")
            return redirect(reverse('laudos_ia:detalhe_laudo_medico', args=[laudo_id]))
        else:
            messages.error(request, "Houve um erro ao salvar o laudo. Verifique os campos.")
    else:
        initial_data = {}
        if not laudo.laudo_final_editado and laudo.laudo_preliminar_ia:
            initial_data['laudo_final_editado'] = laudo.laudo_preliminar_ia
        
        form = LaudoMedicoEditForm(instance=laudo, initial=initial_data)

    context = {
        'form': form,
        'laudo': laudo,
    }
    return render(request, 'laudos_ia/editar_laudo.html', context)