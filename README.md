# Filtro de Enfoque - Control de Bloqueo Parental

Esta es una aplicación de escritorio premium para Windows que te ayuda a mantener la concentración bloqueando el acceso a sitios web que distraen (ej. redes sociales) durante horarios de enfoque específicos.

## Características
- **Interfaz Gráfica Premium**: Diseñada con `customtkinter` con soporte nativo para modo oscuro y diseño minimalista.
- **Acceso Restringido (Seguro)**: Primera configuración requiere registrar un usuario y contraseña administrador. Los accesos siguientes se encuentran bloqueados detrás de una pantalla de login para evitar que se desactive el bloqueo sin autorización.
- **Intercepción HTTP/HTTPS Local**: Redirige los sitios bloqueados a una página web local de "Sitio Bloqueado" estéticamente pulida con citas motivacionales aleatorias sobre productividad.
- **Horario Flexible**: Configuración de horas de inicio y fin (ej. 09:00 a 18:00), con soporte completo para rangos que cruzan la medianoche (ej. de 22:00 a 06:00 del día siguiente).
- **Control UAC Integrado**: Solicita privilegios de Administrador automáticamente al iniciar para poder interactuar con el archivo de sistema `hosts` de Windows.

---

## Estructura del Código

- `main.py`: Punto de entrada que maneja la validación de privilegios de Administrador y la elevación automática mediante UAC.
- `src/gui.py`: Contiene el diseño y la lógica de las tres pantallas de la interfaz: Registro Inicial, Login y Panel de Control.
- `src/scheduler.py`: Servicio en segundo plano que vigila el reloj del sistema y aplica o retira el bloqueo de forma dinámica en base al horario establecido.
- `src/hosts_manager.py`: Módulo para la manipulación segura del archivo de hosts de Windows (`C:\Windows\System32\drivers\etc\hosts`).
- `src/local_server.py`: Servidor web dual (HTTP en puerto 80 y HTTPS en puerto 443 con SSL autofirmado) que sirve la plantilla bloqueada.
- `src/cert_generator.py`: Genera automáticamente en el primer arranque los certificados y llaves SSL locales (`server.crt` y `server.key`).
- `src/auth.py`: Control de seguridad que gestiona el registro y verificación de credenciales con cifrado SHA-256 más sal (salt).
- `templates/bloqueado.html`: Plantilla HTML/CSS responsiva con temática de Glassmorphism y citas motivacionales.

---

## Cómo Ejecutar la Aplicación

Para ejecutar la aplicación, abre una terminal (PowerShell o CMD) como usuario normal o Administrador, ve al directorio del proyecto y ejecuta:

```powershell
# Usando el ejecutable de Python 3.11 instalado
& "C:\Users\richa\AppData\Local\Programs\Python\Python311\python.exe" main.py
```

### Qué esperar durante la ejecución:
1. **Elevación de privilegios (UAC)**: Aparecerá la ventana de Windows pidiendo confirmación para ejecutar el programa como Administrador. Haz clic en **Sí** (es obligatorio para modificar el archivo `hosts` y poder escuchar en los puertos de red 80 y 443).
2. **Pantalla de Registro (Primer Inicio)**: Crea una cuenta con un nombre de usuario y contraseña administrador de tu preferencia.
3. **Inicio de Sesión**: Ingresa los datos que acabas de registrar.
4. **Panel de Control**: 
   - Añade páginas a bloquear escribiendo el dominio (ej: `youtube.com`).
   - Define el horario de inicio y fin (ej: `08:00` a `17:00`).
   - Activa el interruptor **Activo** arriba a la derecha.

---

## Cómo Probar el Bloqueo

1. Agrega una web de prueba, por ejemplo `example.com`.
2. Establece un horario de bloqueo que coincida con tu hora actual (ej. si son las 13:10, pon de `13:00` a `15:00`).
3. Enciende el interruptor **Activo**.
4. Abre tu navegador web e ingresa a `http://example.com` o `https://example.com`.
   - *Nota sobre HTTPS:* Para conexiones seguras (HTTPS), verás una advertencia de seguridad indicando que la conexión no es privada (debido a nuestro certificado autofirmado local). Al hacer clic en **Configuración Avanzada** -> **Acceder a example.com (no seguro)**, verás la tarjeta motivacional de enfoque.
5. Apaga el interruptor o cambia la hora de bloqueo para que quede fuera del rango actual. Verás que al recargar la página en el navegador, esta vuelve a cargar con normalidad y el archivo `hosts` vuelve a su estado limpio original.

---

## Ejecutar Pruebas Unitarias

Para asegurar que todo funciona a nivel lógico sin fallas de regresión:

```powershell
& "C:\Users\richa\AppData\Local\Programs\Python\Python311\python.exe" -m unittest tests/test_logic.py
```
