# Auth Session Audit

Módulo técnico para **Odoo 18** que registra automáticamente cada inicio de sesión exitoso, creando un historial de auditoría inmutable con información del usuario, fecha, IP y localización geográfica opcional.

---

## Qué añade al circuito de Odoo

### Flujo estándar de autenticación (sin el módulo)

```
Navegador → POST /web/session/authenticate → res.users.authenticate() → Sesión activa
```

### Flujo con `auth_session_audit`

```
Navegador → POST /web/session/authenticate
                ↓
        SessionAuditController.authenticate()   ← extiende el controlador web
                ↓
        super().authenticate()                  ← lógica original de Odoo
                ↓
        ¿Login exitoso? (session.uid existe)
                ↓ sí
        _create_session_history()               ← nuevo paso
          · Captura IP (proxy-aware)
          · Captura User-Agent
          · Captura localización GeoIP (si disponible)
          · Crea registro en session.history via sudo()
                ↓
        Respuesta al navegador (sin cambios visibles para el usuario)
```

El módulo actúa como un **observador no intrusivo**: no modifica la lógica de autenticación ni el comportamiento del usuario final. Si el registro falla por cualquier motivo, el error se captura silenciosamente en el log del servidor y el login continúa con normalidad.

---

## Componentes instalados

| Componente | Descripción |
|---|---|
| Modelo `session.history` | Almacena un registro por cada login exitoso |
| Grupo `Security Auditor` | Nuevo grupo con acceso de solo lectura al historial |
| Controlador extendido | Intercepta `/web/session/authenticate` para crear registros |
| Menú en Ajustes | Settings → Session Audit → Session History |
| Traducciones | es, ca, de, fr, pt, it |

---

## Seguridad y permisos

El modelo `session.history` es **estrictamente de solo lectura** para todos los usuarios, incluyendo administradores. Nadie puede crear, editar ni eliminar registros desde la interfaz; solo el sistema los crea internamente mediante `sudo()`.

| Grupo | Leer | Crear | Editar | Eliminar |
|---|:---:|:---:|:---:|:---:|
| Security Auditor | ✓ | — | — | — |
| Administrador (base.group_system) | ✓ | — | — | — |
| Resto de usuarios | — | — | — | — |

El usuario `base.user_admin` se añade automáticamente al grupo **Security Auditor** durante la instalación.

---

## Instalación

1. Copiar la carpeta `auth_session_audit` al directorio de addons del proyecto.
2. Actualizar la lista de aplicaciones: Settings → Apps → Update Apps List.
3. Buscar **Auth Session Audit** e instalar.

No requiere dependencias externas. La localización GeoIP es opcional y funciona automáticamente si Odoo tiene configurada la base de datos GeoIP2 (`geoip_database` en `odoo.conf`).

---

## Uso

### Ver el historial de sesiones

Navegar a **Settings → Session Audit → Session History**.

La vista se abre agrupada por día de forma predeterminada.

### Filtros disponibles

| Filtro | Descripción |
|---|---|
| Internal Users | Muestra solo sesiones de usuarios internos (`share = False`) |
| Portal Users | Muestra solo sesiones de usuarios de portal (`share = True`) |

### Agrupaciones disponibles

| Agrupar por | Descripción |
|---|---|
| By Day | Agrupa los registros por día de login |
| By User | Agrupa los registros por usuario |
| By IP | Agrupa los registros por dirección IP |

### Columnas de la lista

| Campo | Descripción |
|---|---|
| User | Usuario que inició sesión |
| Login Date | Fecha y hora exacta del login (UTC) |
| IP Address | Dirección IP del cliente (respeta cabeceras de proxy) |
| Location | Ciudad y país derivados de GeoIP (si disponible) |
| User Agent | Navegador y sistema operativo *(columna oculta por defecto)* |
| Session ID | Identificador único de sesión *(columna oculta por defecto)* |

---

## Notas técnicas

- **Detección de IP detrás de proxy**: se lee primero la cabecera `HTTP_X_FORWARDED_FOR` (tomando la primera IP de la cadena) y se cae al `remote_addr` si no está presente.
- **GeoIP**: se accede a través de `request.geoip`. Si la base de datos no está configurada, el campo `location` se deja en blanco sin producir ningún error.
- **Resiliencia**: toda la lógica de captura está envuelta en un bloque `try/except`. Un fallo en el registro de auditoría nunca interrumpe el proceso de login.
- **Rendimiento**: la creación del registro es una inserción simple en base de datos, sin cálculos adicionales, ejecutada al final del ciclo de autenticación.
