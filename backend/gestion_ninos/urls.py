from django.urls import path
from . import views

urlpatterns = [
    path('ninos/', views.ninos_list_create, name='ninos-list-create'),
    path('ninos/export/', views.ninos_export_excel, name='ninos-export'),
    path('ninos/<int:nino_id>/', views.nino_detail, name='nino-detail'),
    path('asistencia/dashboard/', views.dashboard_asistencia, name='dashboard-asistencia'),
    path('aula/estudiantes/', views.aula_estudiantes, name='aula-estudiantes'),
    path('aula/asistencia/bulk/', views.aula_asistencia_bulk, name='aula-asistencia-bulk'),
    path('aula/asistencia/dia/', views.aula_asistencia_dia, name='aula-asistencia-dia'),
    path('aula/evaluacion/bulk/', views.aula_evaluacion_bulk, name='aula-evaluacion-bulk'),
    path('aula/evaluacion/dia/', views.aula_evaluacion_dia, name='aula-evaluacion-dia'),
    path('aula/anotaciones/', views.aula_anotaciones, name='aula-anotaciones'),
    path('aula/planificaciones/', views.aula_planificaciones, name='aula-planificaciones'),
    path('asistencia/por-curso/', views.asistencia_por_curso, name='asistencia-por-curso'),
    path('finanzas/dashboard/', views.finanzas_dashboard, name='finanzas-dashboard'),
    path('configuracion/perfil/', views.configuracion_perfil, name='configuracion-perfil'),
    path('configuracion/personal/', views.configuracion_personal, name='configuracion-personal'),
    path('configuracion/personal/<int:personal_id>/', views.configuracion_personal_detail, name='configuracion-personal-detail'),
    path('dashboard/contexto/', views.dashboard_contexto, name='dashboard-contexto'),
]
