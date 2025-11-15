from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from web_admin import models as web_models
import secrets


class Command(BaseCommand):
    help = 'Sincroniza la tabla administrador con los usuarios de Django (auth.User)'

    def add_arguments(self, parser):
        parser.add_argument('--set-random-password', action='store_true', help='Asigna una contraseña aleatoria a los usuarios creados/actualizados y la muestra en salida')

    def handle(self, *args, **options):
        User = get_user_model()
        set_random = options.get('set_random_password', False)
        total = 0

        for admin in web_models.Administrador.objects.all():
            email = getattr(admin, 'email', None)
            if not email:
                self.stdout.write(self.style.WARNING(f"Omitido administrador id={getattr(admin,'id', '?')} sin email"))
                continue

            user, created = User.objects.get_or_create(email=email, defaults={'username': email})
            # Aseguramos que el username exista (en caso de usar email como username)
            if not user.username:
                user.username = email

            # Todos los administradores serán staff
            user.is_staff = True
            user.is_superuser = getattr(admin, 'nivel_acceso', '') == 'superadmin'

            if set_random:
                pwd = secrets.token_urlsafe(12)
                user.set_password(pwd)
                self.stdout.write(f"Contraseña aleatoria establecida para {email}: {pwd}")
            else:
                user.set_unusable_password()

            user.save()
            total += 1

        self.stdout.write(self.style.SUCCESS(f"Sincronizados {total} administradores"))
