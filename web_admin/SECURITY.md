Flujo de autenticación seguro (Autenticación híbrida)

Resumen:
- Fuente de datos maestros: la tabla `administrador` (managed=False).
- Sistema de autenticación: tabla `auth_user` de Django.

Recomendación (flujo seguro):
1. Ejecutar el comando de sincronización:
   ```bash
   python manage.py sync_administradores
   ```
   - Esto crea/actualiza usuarios en `auth_user` para cada registro en `administrador`.
   - Por defecto las cuentas creadas tendrán contraseña no usable. Para asignar contraseñas aleatorias:
   ```bash
   python manage.py sync_administradores --set-random-password
   ```
2. Notificar a los administradores que se requiere cambiar la contraseña o usar "Olvidé mi contraseña".
3. Los administradores inician sesión en `/admin/` con el usuario creado.

Implementación actual:
- `web_admin/auth.py` ahora NO crea usuarios automáticamente durante el login.
- Debes usar `sync_administradores` para provisionar cuentas controladamente.

Seguridad:
- Evita la creación de cuentas por cualquier persona que conozca un email en `administrador`.
- Mantén el comando de sincronización accesible solo a administradores de confianza.

Siguientes mejoras posibles:
- Implementar notificaciones por email durante `--set-random-password`.
- Forzar renovación de contraseña en primer inicio.
- Registrar auditoría cuando se sincronizan administradores.
