from django.shortcuts import render, redirect
from .forms import DocumentoForm
from .models import Documento
from django.contrib.auth.decorators import login_required # colocar depois

# Create your views here.
# @login_required colocar depois
def upload_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.enviado_por = request.user
            documento.save()
            return redirect('lista_documentos')
    else:
        form = DocumentoForm()
    return render(request, 'documentos/upload.html', {'form': form})

# @login_required colocar depois 
def lista_documentos(request):
    documentos = Documento.objects.all()
    return render(request, 'documentos/lista.html', {'documentos': documentos})