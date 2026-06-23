# Contexto del Proyecto
Actúa como un desarrollador Senior de aplicaciones para Windows. Vamos a construir una aplicación de escritorio que bloquea el acceso a ciertas páginas web durante horarios específicos. 

La arquitectura se basará en modificar el archivo `hosts` de Windows para redirigir el tráfico a un servidor web local (`127.0.0.1`), el cual mostrará una página HTML personalizada de "Sitio Bloqueado".

# Requisitos Técnicos y Arquitectura
Por favor, propón el código dividiendo el proyecto en los siguientes 4 módulos. 

**Módulo 1: Gestor de Configuración y UI**
* Necesitamos una interfaz de usuario sencilla.
* Debe permitir al usuario: añadir/eliminar dominios (ej. facebook.com), establecer una hora de inicio y una hora de fin para el bloqueo, y un botón general de Activar/Desactivar.
* Toda esta configuración debe guardarse persistentemente en un archivo `config.json` local.

**Módulo 2: Gestor del Archivo Hosts (Requiere Permisos de Admin)**
* Una clase o módulo dedicado exclusivamente a leer y escribir en `C:\Windows\System32\drivers\etc\hosts`.
* Debe tener métodos para:
  1. Hacer una copia de seguridad del archivo hosts original.
  2. Escribir los dominios bloqueados apuntando a `127.0.0.1` (ej. `127.0.0.1 www.facebook.com`).
  3. Limpiar el archivo hosts (restaurarlo a su estado original o sin nuestras reglas).

**Módulo 3: Servidor Web Local (El Interceptor)**
* Un servidor web muy ligero que se ejecute en segundo plano escuchando en los puertos 80 (HTTP) y 443 (HTTPS).
* Independientemente de la URL que reciba, siempre debe devolver un archivo `bloqueado.html` que contenga un mensaje motivacional para seguir trabajando.
* *Nota sobre HTTPS:* Para el puerto 443, implementa un certificado autofirmado (self-signed) básico. Sé que el navegador mostrará una advertencia de "Conexión no segura" antes de mostrar el HTML, asume esto como un comportamiento aceptable por ahora.

**Módulo 4: El Bucle Principal (Scheduler)**
* Un servicio o hilo en segundo plano que lea la hora del sistema cada minuto.
* Si la hora actual entra en el rango de bloqueo configurado en el Módulo 1: activa el Módulo 3 (servidor) y ejecuta el Módulo 2 (escribir hosts).
* Si la hora sale del rango: detiene el servidor y limpia el archivo hosts.

# Instrucciones de Salida
1. Sugiere el lenguaje de programación y framework de UI más adecuado para esto (ej. Python con Tkinter/PyQt, o C# con WPF/WinForms).
2. Proporciona el código inicial paso a paso, empezando por el Módulo 2 (Gestor de Hosts), ya que es el núcleo funcional. 
3. Asegúrate de incluir el manifiesto o el código necesario para solicitar permisos de Administrador en Windows al abrir la app.