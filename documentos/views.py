from django.shortcuts import render, redirect
from .forms import DocumentoForm
from .models import Documento
# from django.contrib.auth.decorators import login_required # colocar depois / colocado

# Create your views here.
# @login_required(login_url='/autenticacao/login/')
def upload_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            # documento.enviado_por = request.user # nao vou usar por aogra e nem sei se vou usar ainda mas deixa ai pq vai q ne
            documento.save()
            return redirect('lista_documentos')
    else:
        form = DocumentoForm()
    return render(request, 'documentos/upload.html', {'form': form})

# @login_required(login_url='/autenticacao/login/')
def lista_documentos(request):
    documentos = Documento.objects.all()
    return render(request, 'documentos/lista.html', {'documentos': documentos})