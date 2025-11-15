"""Utilidades para mapeo entre auth.User y modelos de la aplicación."""

from django.core.exceptions import ObjectDoesNotExist
from .models import Administrador


def get_administrador_by_user(user):
    """
    Obtiene el objeto Administrador asociado a un auth.User.
    
    Args:
        user: Usuario de Django (auth.User)
    
    Returns:
        Administrador: instancia del modelo Administrador si existe
        None: si no existe un administrador con el email del usuario
    
    Example:
        >>> admin = get_administrador_by_user(request.user)
        >>> if admin:
        ...     print(f"Nivel de acceso: {admin.nivel_acceso}")
    """
    if not user or not user.email:
        return None
    
    try:
        return Administrador.objects.get(email=user.email)
    except ObjectDoesNotExist:
        return None


def get_admin_data(user):
    """
    Obtiene un diccionario con datos relevantes del administrador para el dashboard.
    
    Args:
        user: Usuario de Django (auth.User)
    
    Returns:
        tuple: (dict con datos del administrador, True) si se encuentra.
        tuple: (dict con datos por defecto, False) si NO se encuentra el administrador.
    
    """
    
    # 🚨 Es fundamental que 'get_administrador_by_user' maneje la excepción.
    # Si retorna None, lo capturamos aquí.
    admin = get_administrador_by_user(user)
    
    if not admin:
        # 🚨 CORRECCIÓN: Devolvemos un objeto iterable con datos por defecto.
        default_data = {
            'id': 'N/A',
            'nombre': 'Administrador Desconocido',
            'email': 'N/A',
            'nivel_acceso': 'N/A',
            'permisos': {},
            'reportes_pendientes': 0,
            'reportes_totales': 0,
        }
        # Devolvemos la tupla requerida por la desestructuración segura en la vista
        return (default_data, False)
    
    # Caso exitoso: Devolvemos la tupla (datos, True)
    data = {
        'id': admin.id,
        'nombre': admin.nombre,
        'email': admin.email,
        'nivel_acceso': admin.nivel_acceso,
        'permisos': admin.permisos or {},
        # Se asume que existe la relación 'reportes_asignados'
        'reportes_pendientes': admin.reportes_asignados.filter(
            estado='pendiente'
        ).count(),
        'reportes_totales': admin.reportes_asignados.count(),
    }
    return (data, True)
