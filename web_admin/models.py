from django.db import models
from django.contrib.auth.models import User


# ==============================================================
# MODELO: ADMINISTRADOR
# ==============================================================
class Administrador(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=150, unique=True)
    nombre = models.CharField(max_length=100)
    fecha_registro = models.DateTimeField(auto_now_add=False, null=True)
    permisos = models.JSONField(blank=True, null=True)
    nivel_acceso = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'administrador'
        managed = True

    def __str__(self):
        return f"{self.nombre} <{self.email}>"

    @property
    def is_superuser(self):
        return self.nivel_acceso == 'superadmin'

    @property
    def is_staff(self):
        return True  # Todos los administradores pueden acceder al admin

    def get_django_user(self):
        try:
            return User.objects.get(email=self.email)
        except User.DoesNotExist:
            return None


# ==============================================================
# MODELO: MODELO IA
# ==============================================================
class ModeloIA(models.Model):
    id = models.AutoField(primary_key=True)
    version = models.CharField(max_length=50)
    archivo_iafile_url = models.TextField(blank=True, null=True)  
    fecha_subida = models.DateTimeField(auto_now_add=False, null=True)
    descripcion_cambios = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    total_herramientas = models.IntegerField(default=0)
    archivo_binario = models.BinaryField(blank=True, null=True) 

    class Meta:
        db_table = 'modelo_ia'
        managed = True

    def __str__(self):
        return f"Modelo {self.version} ({'activo' if self.activo else 'inactivo'})"


# ==============================================================
# MODELO: HERRAMIENTA
# ==============================================================
class Herramienta(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    descripcion_tecnica = models.TextField(blank=True, null=True)
    instrucciones_uso = models.TextField(blank=True, null=True)
    imagen_referencia_url = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=False, null=True)
    modelo_ia = models.ForeignKey(
        ModeloIA,
        db_column='modelo_ia_id',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='herramientas'
    )

    class Meta:
        db_table = 'herramienta'
        managed = True

    def __str__(self):
        return self.nombre


# ==============================================================
# MODELO: USUARIO
# ==============================================================
class Usuario(models.Model):
    uid = models.CharField(max_length=100, primary_key=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'usuario'
        managed = True

    def __str__(self):
        return self.uid


# ==============================================================
# MODELO: REPORTE USUARIO
# ==============================================================
class ReporteUsuario(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        db_column='usuario_uid',
        to_field='uid',
        on_delete=models.CASCADE,
        related_name='reportes'
    )
    herramienta = models.ForeignKey(
        Herramienta,
        db_column='herramienta_id',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reportes_usuario'
    )
    administrador = models.ForeignKey(
        Administrador,
        db_column='administrador_id',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reportes_asignados'
    )
    tipo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_reporte = models.DateTimeField(auto_now_add=False, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'reporte_usuario'
        managed = True

    def __str__(self):
        return f"Reporte {self.id} - {self.tipo} ({self.estado})"


# ==============================================================
# MODELO: REPORTE ADMIN
# ==============================================================
class ReporteAdmin(models.Model):
    id = models.AutoField(primary_key=True)
    administrador = models.ForeignKey(
        Administrador,
        db_column='administrador_id',
        on_delete=models.CASCADE,
        related_name='reportes_generados'
    )
    tipo_reporte = models.CharField(max_length=100, blank=True, null=True)
    fecha_generacion = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    parametros_filtro = models.JSONField(blank=True, null=True)
    url_descarga = models.TextField(blank=True, null=True)
    periodo = models.CharField(max_length=50, blank=True, null=True, default='actual')
    
    # Campo binario para guardar archivos (PDF o CSV)
    archivo_binario = models.BinaryField(blank=True, null=True)

    class Meta:
        db_table = 'reporte_admin'
        managed = True  

    def __str__(self):
        return f"ReporteAdmin {self.id} - {self.tipo_reporte}"
