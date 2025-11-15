"""Tests para las vistas de web_admin."""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .test_models import TestAdministrador
from unittest.mock import patch

class DashboardViewTest(TestCase):
    """Pruebas para la vista del Dashboard."""

    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.client = Client()
        self.User = get_user_model()
        
        # Crear usuario de prueba
        self.user = self.User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='test123'
        )
        
        # Crear administrador de prueba
        self.admin = TestAdministrador.objects.create(
            nombre='Admin Test',
            email='test@test.com',
            nivel_acceso='admin',
            uid=str(self.user.id)
        )

    def test_dashboard_requiere_login(self):
        """La vista del dashboard debe requerir inicio de sesión."""
        response = self.client.get(reverse('web_admin:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirección al login
        self.assertTrue(response.url.startswith('/admin/login/'))

    @patch('web_admin.views.get_admin_data')
    def test_dashboard_muestra_info_admin(self, mock_get_admin_data):
        """El dashboard debe mostrar la información del administrador."""
        # Simular datos del administrador
        mock_get_admin_data.return_value = {
            'id': self.admin.id,
            'nombre': 'Admin Test',
            'email': 'test@test.com',
            'nivel_acceso': 'admin',
            'permisos': {'puede_editar': True}
        }
        
        # Iniciar sesión
        self.client.login(username='test@test.com', password='test123')
        
        # Obtener la página del dashboard
        response = self.client.get(reverse('web_admin:dashboard'))
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_admin/dashboard.html')
        
        # Verificar contexto
        self.assertIn('admin_data', response.context)
        self.assertEqual(response.context['admin_data']['nombre'], 'Admin Test')
        self.assertEqual(response.context['admin_data']['nivel_acceso'], 'admin')
        
    @patch('web_admin.views.get_admin_data')
    def test_dashboard_sin_admin(self, mock_get_admin_data):
        """El dashboard debe manejar el caso de usuario sin admin asociado."""
        # Simular que no hay admin asociado
        mock_get_admin_data.return_value = None
        
        # Iniciar sesión
        self.client.login(username='test@test.com', password='test123')
        
        # Obtener la página del dashboard
        response = self.client.get(reverse('web_admin:dashboard'))
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_admin/dashboard.html')
        
        # Verificar mensaje de error
        self.assertIn('error', response.context)
        self.assertEqual(
            response.context['error'],
            'No se encontró el administrador asociado a tu cuenta.'
        )