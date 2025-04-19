from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='/autenticacao/login/')
def home_view(request):
    return render(request, 'home/home.html')