from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistroForm, LoginForm

# Create your views here.
def registrar_usuario(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroForm()
    return redirect('autenticacao/login.html')

def login_usuario(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'autenticacao/login.html', {'form': form})

def logout_usuario(request):
    logout(request)
    return redirect('login')