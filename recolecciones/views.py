from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CategoriaChatarra, SolicitudRetiro, Ubicacion, Fotografia

def home_view(request):
    """Vista principal / Dashboard inicial"""
    return render(request, 'recolecciones/home.html')

def crear_solicitud_view(request):
    """Módulo transaccional principal: Crear solicitud con foto y GPS"""
    # Si no hay usuarios autenticados para la prueba, asignamos el primer usuario disponible
    from django.contrib.auth.models import User
    usuario_demo = request.user if request.user.is_authenticated else User.objects.first()

    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        notas = request.POST.get('notas_adicionales')
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        direccion = request.POST.get('direccion', 'Ubicación GPS seleccionada')
        foto_file = request.FILES.get('fotografia')

        # Validación básica de datos obligatorios
        if not categoria_id or not foto_file:
            messages.error(request, "Debe seleccionar una categoría e incluir una fotografía.")
            return redirect('crear_solicitud')

        # 1. Crear la solicitud
        categoria = get_object_or_404(CategoriaChatarra, id=categoria_id)
        solicitud = SolicitudRetiro.objects.create(
            usuario=usuario_demo,
            categoria=categoria,
            notas_adicionales=notas,
            estado_actual='PUBLICADA'
        )

        # 2. Guardar la fotografía adjunta
        Fotografia.objects.create(
            solicitud=solicitud,
            imagen=foto_file
        )

        # 3. Guardar las coordenadas GPS
        if latitud and longitud:
            Ubicacion.objects.create(
                solicitud=solicitud,
                latitud=float(latitud),
                longitud=float(longitud),
                direccion_formateada=direccion
            )

        messages.success(request, f"¡Solicitud #{solicitud.id} creada e ingresada al sistema con éxito!")
        return redirect('historial_solicitudes')

    categorias = CategoriaChatarra.objects.all()
    return render(request, 'recolecciones/crear_solicitud.html', {'categorias': categorias})

def historial_solicitudes_view(request):
    """Vista de consulta con filtros simples y múltiples"""
    solicitudes = SolicitudRetiro.objects.all().select_related('categoria', 'ubicacion').prefetch_related('fotografias')

    # Filtros de búsqueda (Pantalla de consultas)
    categoria_id = request.GET.get('categoria')
    estado = request.GET.get('estado')

    if categoria_id:
        solicitudes = solicitudes.filter(categoria_id=categoria_id)
    if estado:
        solicitudes = solicitudes.filter(estado_actual=estado)

    categorias = CategoriaChatarra.objects.all()
    estados = SolicitudRetiro.ESTADOS

    context = {
        'solicitudes': solicitudes,
        'categorias': categorias,
        'estados': estados,
        'categoria_selected': categoria_id,
        'estado_selected': estado,
    }
    return render(request, 'recolecciones/historial.html', context)

def cancelar_solicitud_view(request, pk):
    """Acción de eliminación / cancelación de CRUD"""
    solicitud = get_object_or_404(SolicitudRetiro, pk=pk)
    if request.method == 'POST':
        solicitud.estado_actual = 'CANCELADA'
        solicitud.save()
        messages.info(request, f"La solicitud #{solicitud.id} ha sido cancelada.")
    return redirect('historial_solicitudes')

@login_required
def solicitudes_disponibles_view(request):
    """Muestra las solicitudes publicadas disponibles para los recolectores."""
    solicitudes = SolicitudRetiro.objects.filter(
        estado_actual='PUBLICADA',
        recolector_isnull=True
    ).select_related(
        'categoria',
        'ubicacion'
    ).prefetch_related(
        'fotografias'
    )

    return render(
        request,
        'recolecciones/solicitudes_disponibles.html',
        {'solicitudes': solicitudes}
    )