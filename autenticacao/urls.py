from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_usuario, name='login'),
    path('registro/', views.registrar_usuario, name='registro'),
    path('logout/', views.logout_usuario, name='logout'),
]

