"""
Comando para poblar la base de datos con datos iniciales.
Uso: python manage.py populate_initial_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from web_admin.models import Administrador, ModeloIA, Herramienta, Usuario


class Command(BaseCommand):
    help = 'Populate the database with initial data (admin user, tools, etc.)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # 1. Crear superusuario Django si no existe
        self.create_admin_user()

        # 2. Crear modelo IA por defecto
        self.create_default_model_ia()

        # 3. Crear herramientas iniciales
        self.create_initial_tools()

        # 4. Crear administrador inicial
        self.create_initial_admin()

        self.stdout.write(self.style.SUCCESS('\n✅ Data population completed successfully!'))

    def create_admin_user(self):
        """Crear superusuario Django"""
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('  ⚠️  Admin user already exists'))
            return

        admin = User.objects.create_superuser(
            username='admin',
            email='admin@escanerherramientas.com',
            password='admin123'
        )
        self.stdout.write(self.style.SUCCESS('  ✅ Admin user created: admin / admin123'))

    def create_default_model_ia(self):
        """Crear modelo IA por defecto"""
        if ModeloIA.objects.filter(version='1.0').exists():
            self.stdout.write(self.style.WARNING('  ⚠️  Default AI model already exists'))
            return

        modelo = ModeloIA.objects.create(
            version='1.0',
            descripcion_cambios='Modelo inicial de reconocimiento de herramientas',
            activo=True,
            total_herramientas=0,
        )
        self.stdout.write(self.style.SUCCESS(f'  ✅ AI Model created: {modelo.version}'))

    def create_initial_tools(self):
        """Crear herramientas iniciales"""
        modelo_ia = ModeloIA.objects.filter(activo=True).first()
        
        herramientas_data = [
            {
                'nombre': 'Martillo',
                'categoria': 'Percusión',
                'descripcion_tecnica': 'Herramienta de percusión para clavar y golpear',
                'instrucciones_uso': 'Usar para clavar clavos o golpear objetos',
            },
            {
                'nombre': 'Destornillador',
                'categoria': 'Ajuste',
                'descripcion_tecnica': 'Herramienta para atornillar/desatornillar',
                'instrucciones_uso': 'Insertar en la cabeza del tornillo y girar',
            },
            {
                'nombre': 'Llave Inglesa',
                'categoria': 'Ajuste',
                'descripcion_tecnica': 'Llave ajustable para tuercas y pernos',
                'instrucciones_uso': 'Colocar sobre la tuerca y girar',
            },
            {
                'nombre': 'Alicates',
                'categoria': 'Sujeción',
                'descripcion_tecnica': 'Herramienta para sujetar y cortar alambres',
                'instrucciones_uso': 'Usar para sujetar o cortar materiales',
            },
            {
                'nombre': 'Taladro',
                'categoria': 'Perforación',
                'descripcion_tecnica': 'Máquina para perforar agujeros',
                'instrucciones_uso': 'Colocar broca, posicionar y activar',
            },
        ]

        for tool_data in herramientas_data:
            if not Herramienta.objects.filter(nombre=tool_data['nombre']).exists():
                herramienta = Herramienta.objects.create(
                    nombre=tool_data['nombre'],
                    categoria=tool_data['categoria'],
                    descripcion_tecnica=tool_data['descripcion_tecnica'],
                    instrucciones_uso=tool_data['instrucciones_uso'],
                    activa=True,
                    fecha_registro=timezone.now(),
                    modelo_ia=modelo_ia,
                )
                self.stdout.write(self.style.SUCCESS(f'  ✅ Tool created: {herramienta.nombre}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Tool already exists: {tool_data["nombre"]}'))

    def create_initial_admin(self):
        """Crear administrador inicial vinculado al user admin"""
        if Administrador.objects.filter(email='admin@escanerherramientas.com').exists():
            self.stdout.write(self.style.WARNING('  ⚠️  Initial admin already exists'))
            return

        try:
            django_user = User.objects.get(username='admin')
            admin = Administrador.objects.create(
                uid='admin-001',
                email='admin@escanerherramientas.com',
                nombre='Administrador Sistema',
                fecha_registro=timezone.now(),
                nivel_acceso='superadmin',
                permisos={
                    'can_view_reports': True,
                    'can_manage_tools': True,
                    'can_manage_users': True,
                    'can_manage_admins': True,
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  ✅ Admin user created: {admin.nombre}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ❌ Django admin user not found'))
