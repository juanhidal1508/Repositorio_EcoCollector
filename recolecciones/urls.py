from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('solicitudes/nueva/', views.crear_solicitud_view, name='crear_solicitud'),
    path('solicitudes/historial/', views.historial_solicitudes_view, name='historial_solicitudes'),
    path('solicitudes/<int:pk>/cancelar/', views.cancelar_solicitud_view, name='cancelar_solicitud'),
    path('solicitudes/<int:pk>/modificar/', views.modificar_solicitud_view, name='modificar_solicitud'),
    path('recolector/solicitudes/', views.solicitudes_disponibles_view, name='solicitudes_disponibles'),
]