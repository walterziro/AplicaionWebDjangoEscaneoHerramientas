from django.apps import AppConfig


class WebAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web_admin'

    def ready(self):
        # Importar señales y setup de grupos
        import web_admin.signals
        from web_admin.groups_setup import setup_groups_on_start

        # Crear grupos automáticamente al iniciar
        setup_groups_on_start()
