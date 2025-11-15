# web_admin/groups_setup.py
from django.contrib.auth.models import Group, Permission
from django.apps import apps


def create_default_groups():
    """
    Crea los grupos de permisos base para SuperAdministradores y Administradores.
    Se ejecuta automáticamente al iniciar el servidor si no existen.
    """

    # 1️⃣ Grupo SuperAdministradores (tiene todos los permisos)
    superadmin_group, _ = Group.objects.get_or_create(name="SuperAdministradores")
    all_permissions = Permission.objects.all()
    superadmin_group.permissions.set(all_permissions)

    # 2️⃣ Grupo Administradores (solo lectura/modificación básica)
    admin_group, _ = Group.objects.get_or_create(name="Administradores")

    # Permitir modificar modelos principales excepto Administrador y User
    allowed_models = [
        "modeloia",
        "herramienta",
        "usuario",
        "reporteusuario",
        "reporteadmin",
    ]

    # Filtrar permisos solo de esos modelos
    filtered_permissions = Permission.objects.filter(content_type__model__in=allowed_models)
    admin_group.permissions.set(filtered_permissions)

    print("Grupos de permisos creados o actualizados correctamente.")


# Este hook se puede llamar automáticamente desde AppConfig.ready()
def setup_groups_on_start():
    try:
        create_default_groups()
    except Exception as e:
        print(f"Error creando grupos: {e}")
