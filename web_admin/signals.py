from django.db import transaction, IntegrityError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User, Group
from .models import Administrador


# ============================================================
# 🔄 CREACIÓN / SINCRONIZACIÓN AUTOMÁTICA DE ADMINISTRADOR
# ============================================================
@receiver(post_save, sender=User)
def sync_user_to_administrador(sender, instance, created, **kwargs):
    """
    Sincroniza automáticamente los objetos User → Administrador.
    Si el Administrador ya existe (por email o uid), lo actualiza.
    También asigna grupo según tipo (superadmin/admin).
    Protege la transacción con atomic().
    """
    email = instance.email or f"{instance.username}@sin_email.com"
    uid = f"auto-{instance.id}"

    try:
        with transaction.atomic():
            # Buscar si ya existe el administrador
            admin_existente = (
                Administrador.objects.filter(email=email).first()
                or Administrador.objects.filter(uid=uid).first()
            )

            if admin_existente:
                admin_existente.nombre = f"{instance.first_name} {instance.last_name}".strip() or instance.username
                admin_existente.email = email
                admin_existente.uid = uid
                admin_existente.nivel_acceso = 'superadmin' if instance.is_superuser else 'admin'
                admin_existente.save(update_fields=["nombre", "email", "uid", "nivel_acceso"])
            else:
                Administrador.objects.create(
                    uid=uid,
                    email=email,
                    nombre=f"{instance.first_name} {instance.last_name}".strip() or instance.username,
                    fecha_registro=timezone.now(),
                    nivel_acceso='superadmin' if instance.is_superuser else 'admin'
                )

            # Asignar grupo automáticamente
            group_name = "SuperAdministradores" if instance.is_superuser else "Administradores"
            group, _ = Group.objects.get_or_create(name=group_name)
            instance.groups.clear()
            instance.groups.add(group)
            instance.save()

    except IntegrityError as e:
        print(f"⚠️ [SYNC ADMIN ERROR] Error de integridad para usuario {instance.username}: {e}")
    except Exception as e:
        print(f"⚠️ [SYNC ADMIN ERROR] Error inesperado para usuario {instance.username}: {e}")


# ============================================================
# 🗑 ELIMINACIÓN AUTOMÁTICA DE ADMINISTRADOR
# ============================================================
@receiver(post_delete, sender=User)
def delete_administrador_on_user_delete(sender, instance, **kwargs):
    """
    Si se elimina un User, borra el Administrador vinculado.
    """
    try:
        with transaction.atomic():
            email = instance.email or f"{instance.username}@sin_email.com"
            uid = f"auto-{instance.id}"
            Administrador.objects.filter(email=email).delete()
            Administrador.objects.filter(uid=uid).delete()
    except Exception as e:
        print(f"⚠️ [DELETE ADMIN ERROR] No se pudo eliminar el administrador vinculado a {instance.username}: {e}")
