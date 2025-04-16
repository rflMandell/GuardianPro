from django.shortcuts import render, redirect
from .forms import DocumentoForm
from .models import Documento
from django.contrib.auth.decorators import login_required

# Create your views here.
