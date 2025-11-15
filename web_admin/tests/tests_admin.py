"""Tests para la personalización del admin de Django."""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from ..admin import AdministradorAdmin
from .test_models import TestAdministrador
from .test_utils import get_test_admin_data
from unittest.mock import patch


class MockSuperUser:
    """Usuario simulado con permisos de superusuario."""
    def __init__(self):
        self.is_superuser = True
        self.is_active = True
        self.is_staff = True


class AdministradorAdminTest(TestCase):
    """Pruebas para la personalización del ModelAdmin de Administrador."""
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = AdministradorAdmin(TestAdministrador, self.site)
        
        # Crear usuarios de prueba
        self.User = get_user_model()
        self.superuser = self.User.objects.create_superuser(
            username='super@test.com',
            email='super@test.com',
            password='test123'
        )
        
        self.normal_user = self.User.objects.create_user(
            username='normal@test.com',
            email='normal@test.com',
            password='test123'
        )
        
        # Crear administradores de prueba usando el modelo de prueba
        self.admin1 = TestAdministrador.objects.create(
            nombre='Admin Uno',
            email='admin1@test.com',
            nivel_acceso='superadmin',
            uid=str(self.normal_user.id)
        )
        
        self.admin2 = TestAdministrador.objects.create(
            nombre='Admin Dos',
            email='admin2@test.com',
            nivel_acceso='admin'
        )

    def _create_request(self, user):
        """Crear una request simulada con un usuario específico."""
        request = self.factory.get('/')
        request.user = user
        # Agregar storage para mensajes
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))
        return request

    def test_queryset_superuser(self):
        """Superusuario debe ver todos los administradores."""
        request = self._create_request(self.superuser)
        qs = self.admin.get_queryset(request)
        self.assertEqual(qs.count(), 2)  # Debe ver ambos administradores

    @patch('web_admin.tests.test_utils.get_test_admin_data')
    def test_queryset_normal_admin(self, mock_get_admin_data):
        """Admin normal solo debe verse a sí mismo."""
        mock_get_admin_data.return_value = {
            'id': self.admin1.id,
            'nivel_acceso': 'admin',
            'email': self.normal_user.email
        }
        request = self._create_request(self.normal_user)
        qs = self.admin.get_queryset(request)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.admin1)

    def test_has_change_permission_superuser(self):
        """Superusuario debe poder editar cualquier administrador."""
        request = self._create_request(self.superuser)
        self.assertTrue(self.admin.has_change_permission(request, self.admin1))
        self.assertTrue(self.admin.has_change_permission(request, self.admin2))

    @patch('web_admin.tests.test_utils.get_test_admin_data')
    def test_has_change_permission_normal_admin(self, mock_get_admin_data):
        """Admin normal solo debe poder editar su propio perfil."""
        mock_get_admin_data.return_value = {
            'id': self.admin1.id,
            'nivel_acceso': 'admin',
            'email': self.normal_user.email
        }
        request = self._create_request(self.normal_user)
        # Puede editar su propio perfil
        self.assertTrue(self.admin.has_change_permission(request, self.admin1))
        # No puede editar otros perfiles
        self.assertFalse(self.admin.has_change_permission(request, self.admin2))

    def test_has_delete_permission(self):
        """Solo superusuarios y superadmins pueden eliminar."""
        request_super = self._create_request(self.superuser)
        request_normal = self._create_request(self.normal_user)
        
        # Superusuario puede eliminar
        self.assertTrue(self.admin.has_delete_permission(request_super))
        # Admin normal no puede eliminar
        self.assertFalse(self.admin.has_delete_permission(request_normal))

    @patch('web_admin.tests.test_utils.get_test_admin_data')
    def test_save_model_restrictions(self, mock_get_admin_data):
        """Probar restricciones al guardar administradores."""
        mock_get_admin_data.return_value = {
            'id': self.admin1.id,
            'nivel_acceso': 'admin',
            'email': self.normal_user.email
        }
        
        request = self._create_request(self.normal_user)
        
        # Intentar crear nuevo admin (no debería poder)
        new_admin = TestAdministrador(
            nombre='Nuevo Admin',
            email='nuevo@test.com',
            nivel_acceso='admin'
        )
        
        with self.assertRaises(PermissionDenied):
            self.admin.save_model(request, new_admin, None, False)
        
        # Intentar editar otro admin (no debería poder)
        with self.assertRaises(PermissionDenied):
            self.admin.save_model(request, self.admin2, None, True)
        
        # Debería poder editar su propio perfil
        try:
            self.admin.save_model(request, self.admin1, None, True)
        except PermissionDenied:
            self.fail("No debería levantar PermissionDenied al editar su propio perfil")