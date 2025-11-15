from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class AdministradorAuthBackend(ModelBackend):
    """
    Backend de autenticación seguro que NO crea usuarios automáticamente.

    Comportamiento:
    - Busca un `auth.User` existente por `username` o `email`.
    - Si el usuario existe y la contraseña es válida, devuelve el usuario.
    - Si no existe o la contraseña es incorrecta, devuelve None.

    Nota: La creación/actualización masiva de usuarios desde la tabla `administrador`
    se realiza con el comando `manage.py sync_administradores`.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if not username or not password:
            return None

        # Intentar encontrar por username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Intentar por email
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None