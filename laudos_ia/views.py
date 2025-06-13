from django.shortcuts import render
from .models import LaudoMedico
from .forms import LaudoMedicoEditForm 
from django.utils import timezone 
from django.urls import reverse 
from django.contrib import messages 
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404 

def listar_laudos_pendentes(request):
    print(f"DEBUG LAUDOS (SEM LOGIN): Entrando em listar_laudos_pendentes.")
    print(f"DEBUG LAUDOS (SEM LOGIN): request.user: {request.user}") # Será AnonymousUser
    print(f"DEBUG LAUDOS (SEM LOGIN): request.user.is_authenticated: {request.user.is_authenticated}") 
    
    laudos = LaudoMedico.objects.filter(status='AGUARDANDO_REVISAO').order_by('-data_criacao')
    print(f"DEBUG LAUDOS (SEM LOGIN): Quantidade de laudos pendentes encontrados: {laudos.count()}")

    context = {
        'laudos': laudos,
        'titulo_pagina': 'Laudos Pendentes de Revisão (Teste - Sem Login)'
    }
    return render(request, 'laudos_ia/listar_laudos.html', context)

def listar_todos_laudos(request):
    print(f"DEBUG LAUDOS (SEM LOGIN): Entrando em listar_todos_laudos.")
    laudos = LaudoMedico.objects.all().order_by('-data_criacao')
    context = {
        'laudos': laudos,
        'titulo_pagina': 'Todos os Laudos (Teste - Sem Login)'
    }
    return render(request, 'laudos_ia/listar_laudos.html', context)

def detalhe_laudo_medico(request, laudo_id):
    print(f"DEBUG LAUDOS (SEM LOGIN): Detalhe do laudo ID: {laudo_id}")
    laudo = get_object_or_404(LaudoMedico, id=laudo_id)
    context = {
        'laudo': laudo,
    }
    return render(request, 'laudos_ia/detalhe_laudo.html', context)

def editar_laudo_medico(request, laudo_id):
    print(f"DEBUG LAUDOS (SEM LOGIN): Editando laudo ID: {laudo_id}")
    laudo = get_object_or_404(LaudoMedico, id=laudo_id)

    # Lógica de permissão e verificação de status removida/simplificada para teste
    if laudo.status == 'REVISADO_FINALIZADO':
        messages.info(request, "Este laudo já foi finalizado e não pode ser editado novamente (Teste - Sem Login).")
        return redirect(reverse('laudos_ia:detalhe_laudo_medico', args=[laudo_id]))

    if request.method == 'POST':
        form = LaudoMedicoEditForm(request.POST, instance=laudo)
        if form.is_valid():
            laudo_editado = form.save(commit=False)
            laudo_editado.status = 'REVISADO_FINALIZADO'
            laudo_editado.data_finalizacao_revisao = timezone.now()
            laudo_editado.save()
            
            if laudo_editado.chamada:
                laudo_editado.chamada.status = 'LAUDO_CONCLUIDO'
                laudo_editado.chamada.save(update_fields=['status'])

            messages.success(request, "Laudo salvo e finalizado com sucesso! (Teste - Sem Login)")
            return redirect(reverse('laudos_ia:detalhe_laudo_medico', args=[laudo_id]))
        else:
            messages.error(request, "Houve um erro ao salvar o laudo. Verifique os campos. (Teste - Sem Login)")
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