"""Utilidades para pruebas."""

from ..test_models import TestAdministrador


def get_test_admin_data(user):
    """Versión de prueba de get_admin_data."""
    try:
        admin = TestAdministrador.objects.get(email=user.email)
        return {
            'id': admin.id,
            'nombre': admin.nombre,
            'email': admin.email,
            'nivel_acceso': admin.nivel_acceso,
            'permisos': admin.permisos or {},
        }
    except TestAdministrador.DoesNotExist:
        return None