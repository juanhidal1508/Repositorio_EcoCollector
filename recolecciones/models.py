from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class CategoriaChatarra(models.Model):
    nombre_categoria = models.CharField(max_length=50, unique=True)
    descripcion_material = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoría de Chatarra"
        verbose_name_plural = "Categorías de Chatarra"

    def __str__(self):
        return self.nombre_categoria


class SolicitudRetiro(models.Model):
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('PUBLICADA', 'Publicada'),
        ('ASIGNADA', 'Asignada'),
        ('EN_RUTA', 'En Ruta'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADA', 'Completada'),
        ('RECHAZADA', 'Rechazada'),
        ('CANCELADA', 'Cancelada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes')
    recolector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='retiros_asignados')
    categoria = models.ForeignKey(CategoriaChatarra, on_delete=models.PROTECT, related_name='solicitudes')
    estado_actual = models.CharField(max_length=20, choices=ESTADOS, default='PUBLICADA')
    notas_adicionales = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Solicitud de Retiro"
        verbose_name_plural = "Solicitudes de Retiro"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Solicitud #{self.id} - {self.categoria.nombre_categoria} ({self.estado_actual})"


class Ubicacion(models.Model):
    solicitud = models.OneToOneField(SolicitudRetiro, on_delete=models.CASCADE, related_name='ubicacion')
    latitud = models.DecimalField(max_digits=10, decimal_places=8)
    longitud = models.DecimalField(max_digits=11, decimal_places=8)
    direccion_formateada = models.CharField(max_length=255)

    def __str__(self):
        return f"Ubicación Solicitud #{self.solicitud.id}"


class Fotografia(models.Model):
    solicitud = models.ForeignKey(SolicitudRetiro, on_delete=models.CASCADE, related_name='fotografias')
    imagen = models.ImageField(upload_to='chatarra_fotos/%Y/%m/')
    fecha_captura = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto #{self.id} - Solicitud #{self.solicitud.id}"


class Calificacion(models.Model):
    solicitud = models.OneToOneField(SolicitudRetiro, on_delete=models.CASCADE, related_name='calificacion')
    puntuacion_estrellas = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True, null=True)
    fecha_evaluacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calificación {self.puntuacion_estrellas}★ - Solicitud #{self.solicitud.id}"