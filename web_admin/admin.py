from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from . import models
from .utils import get_administrador_by_user, get_admin_data


# ===============================================================
# ⚙️ ACCIÓN GLOBAL: "Modificar elemento seleccionado"
# ===============================================================
def modificar_seleccionado(modeladmin, request, queryset):
    """Permite abrir el formulario de edición desde el menú Actions."""
    if queryset.count() != 1:
        modeladmin.message_user(request, "Selecciona solo un elemento para modificar.", level=messages.WARNING)
        return

    obj = queryset.first()
    app_label = modeladmin.model._meta.app_label
    model_name = modeladmin.model._meta.model_name
    edit_url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.pk])
    return redirect(edit_url)

modificar_seleccionado.short_description = "Modificar elemento seleccionado"


# ===============================================================
# 🔹 ADMINISTRADOR
# ===============================================================
@admin.register(models.Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'uid', 'nivel_acceso')
    search_fields = ('nombre', 'email', 'uid')
    list_filter = ('nivel_acceso',)
    actions = [modificar_seleccionado]

    def _get_admin_data(self, request):
        """Obtiene datos del admin."""
        if isinstance(self.model, type) and self.model.__name__ == 'TestAdministrador':
            from .tests.test_utils import get_test_admin_data
            return get_test_admin_data(request.user)
        from .utils import get_admin_data
        return get_admin_data(request.user)

    def get_queryset(self, request):
        """Filtrar administradores según el nivel de acceso del usuario actual."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            admin = get_administrador_by_user(request.user)
            if not admin:
                return qs.none()
            if admin.nivel_acceso != 'superadmin':
                return qs.filter(id=admin.id)
        return qs

    def has_change_permission(self, request, obj=None):
        """Verificar si el usuario puede modificar un administrador."""
        if request.user.is_superuser:
            return True
        admin = get_administrador_by_user(request.user)
        if not admin:
            return False
        return obj is None or (
            admin.nivel_acceso == 'superadmin' or
            admin.id == obj.id
        )

    def has_delete_permission(self, request, obj=None):
        """Solo superadmins pueden eliminar administradores."""
        if request.user.is_superuser:
            return True
        admin = get_administrador_by_user(request.user)
        return admin and admin.nivel_acceso == 'superadmin'

    def save_model(self, request, obj, form, change):
        """Validar y guardar cambios en el modelo Administrador."""
        if not request.user.is_superuser:
            admin = get_administrador_by_user(request.user)
            if not admin:
                raise PermissionDenied('No tienes permisos de administrador.')
            if change:
                if admin.nivel_acceso != 'superadmin' and obj.id != admin.id:
                    raise PermissionDenied('Solo puedes editar tu propio perfil.')
            else:
                if admin.nivel_acceso != 'superadmin':
                    raise PermissionDenied('Solo superadmins pueden crear nuevos administradores.')
        super().save_model(request, obj, form, change)
        messages.success(request, 'Administrador guardado exitosamente.')


# ===============================================================
# 🔹 MODELO IA
# ===============================================================
@admin.register(models.ModeloIA)
class ModeloIAAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'activo', 'fecha_subida')
    search_fields = ('version',)
    list_filter = ('activo',)
    actions = [modificar_seleccionado]

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        admin = get_administrador_by_user(request.user)
        return admin and admin.nivel_acceso == 'superadmin'

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        admin = get_administrador_by_user(request.user)
        return admin and admin.nivel_acceso == 'superadmin'

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        admin = get_administrador_by_user(request.user)
        return admin and admin.nivel_acceso == 'superadmin'


# ===============================================================
# 🔹 HERRAMIENTA
# ===============================================================
@admin.register(models.Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'activa', 'modelo_ia')
    search_fields = ('nombre', 'categoria')
    list_filter = ('activa', 'categoria')
    actions = [modificar_seleccionado]

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        admin = get_administrador_by_user(request.user)
        return admin and admin.nivel_acceso == 'superadmin'

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        admin = get_administrador_by_user(request.user)
        return admin and admin.nivel_acceso == 'superadmin'

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        admin = get_administrador_by_user(request.user)
        return admin and admin.nivel_acceso == 'superadmin'


# ===============================================================
# 🔹 USUARIO
# ===============================================================
@admin.register(models.Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('uid', 'activo')
    search_fields = ('uid',)
    list_filter = ('activo',)
    actions = [modificar_seleccionado]

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return get_administrador_by_user(request.user) is not None

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        admin = get_administrador_by_user(request.user)
        return admin and admin.nivel_acceso == 'superadmin'


# ===============================================================
# 🔹 REPORTE USUARIO
# ===============================================================
@admin.register(models.ReporteUsuario)
class ReporteUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'herramienta', 'administrador', 'tipo', 'estado', 'fecha_reporte')
    search_fields = ('tipo', 'descripcion')
    list_filter = ('estado', 'tipo')
    actions = ['modificar_reporte']

    def get_queryset(self, request):
        """Filtrar reportes según el nivel de acceso."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Ve todo

        admin = get_administrador_by_user(request.user)
        if not admin:
            return qs.none()

        if admin.nivel_acceso == 'superadmin':
            return qs  # Ve todo
        elif admin.nivel_acceso == 'admin':
            # Ver reportes de usuarios normales (sin campo administrador)
            return qs.filter(administrador__isnull=True) | qs.filter(administrador=admin)
        else:
            return qs.none()

    def save_model(self, request, obj, form, change):
        """Asignar automáticamente el administrador al guardar."""
        if not obj.administrador:
            admin = get_administrador_by_user(request.user)
            if admin:
                obj.administrador = admin
        super().save_model(request, obj, form, change)

    # ===============================================================
    # ⚙️ ACCIÓN PERSONALIZADA: "Modificar reporte"
    # ===============================================================
    def modificar_reporte(self, request, queryset):
        """Permite abrir el formulario de edición desde el menú Actions."""
        if queryset.count() != 1:
            self.message_user(request, "Selecciona solo un reporte para modificar.", level=messages.WARNING)
            return

        reporte = queryset.first()

        # Verificación de permisos
        if not request.user.is_superuser:
            admin = get_administrador_by_user(request.user)
            if not admin:
                raise PermissionDenied("No tienes permisos para modificar reportes.")
            if admin.nivel_acceso != 'superadmin' and reporte.administrador != admin:
                raise PermissionDenied("Solo puedes modificar tus propios reportes o los no asignados.")

        edit_url = reverse(f'admin:web_admin_reporteusuario_change', args=[reporte.id])
        return redirect(edit_url)

    modificar_reporte.short_description = "Modificar reporte seleccionado"

# ===============================================================
# 🔹 REPORTE ADMIN
# ===============================================================
@admin.register(models.ReporteAdmin)
class ReporteAdminAdmin(admin.ModelAdmin):
    list_display = ('id', 'administrador', 'tipo_reporte', 'fecha_generacion', 'periodo')
    search_fields = ('tipo_reporte',)
    list_filter = ('periodo',)
    actions = [modificar_seleccionado]
