from django.urls import path
from . import views

app_name = 'laudos_ia' 

urlpatterns = [
    path('', views.listar_laudos_pendentes, name='listar_laudos_pendentes'),
    path('todos/', views.listar_todos_laudos, name='listar_todos_laudos'),
    path('<int:laudo_id>/', views.detalhe_laudo_medico, name='detalhe_laudo_medico'),
    path('<int:laudo_id>/editar/', views.editar_laudo_medico, name='editar_laudo_medico'),
]