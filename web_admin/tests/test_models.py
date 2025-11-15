"""Models for testing purposes."""
from django.db import models


class TestAdministrador(models.Model):
    """Versión administrada del modelo Administrador para pruebas."""
    id = models.AutoField(primary_key=True)
    uid = models.CharField(max_length=100, unique=True, null=True)
    email = models.CharField(max_length=150, unique=True)
    nombre = models.CharField(max_length=100)
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True)
    permisos = models.JSONField(blank=True, null=True)
    nivel_acceso = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        # Esta versión sí será administrada por Django
        managed = True