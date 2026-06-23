import os
import shutil

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
BACKUP_PATH = r"C:\Windows\System32\drivers\etc\hosts.bak"
START_MARKER = "# --- PARENTAL BLOCK START ---"
END_MARKER = "# --- PARENTAL BLOCK END ---"

def backup_hosts():
    """Crea una copia de seguridad de seguridad en hosts.bak si no existe."""
    try:
        if not os.path.exists(BACKUP_PATH) and os.path.exists(HOSTS_PATH):
            shutil.copy2(HOSTS_PATH, BACKUP_PATH)
            print(f"[HostsManager] Copia de seguridad del archivo hosts creada en: {BACKUP_PATH}")
            return True
        return False
    except Exception as e:
        print(f"[HostsManager] Error al respaldar el archivo hosts: {e}")
        return False

def clean_hosts_content(content_lines):
    """Remueve todas las líneas que estén entre los marcadores de bloqueo parental."""
    new_lines = []
    in_block = False
    for line in content_lines:
        stripped = line.strip()
        if stripped == START_MARKER:
            in_block = True
            continue
        if stripped == END_MARKER:
            in_block = False
            continue
        if not in_block:
            new_lines.append(line)
    return new_lines

def write_domains(domains):
    """Escribe los dominios bloqueados mapeados a 127.0.0.1 en el archivo hosts."""
    backup_hosts()  # Asegurar copia de respaldo antes de cualquier escritura
    try:
        # Leer el hosts actual
        if os.path.exists(HOSTS_PATH):
            with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        else:
            lines = []

        # Remover bloques anteriores de nuestra app
        clean_lines = clean_hosts_content(lines)

        # Asegurar un fin de línea si el archivo no termina en salto de línea
        if clean_lines and not clean_lines[-1].endswith("\n"):
            clean_lines[-1] += "\n"

        # Escribir el nuevo bloque de redirecciones si hay dominios a bloquear
        if domains:
            block_lines = [START_MARKER + "\n"]
            for domain in domains:
                domain = domain.strip().lower()
                if not domain:
                    continue
                # Escribir tanto el dominio limpio como con www.
                block_lines.append(f"127.0.0.1 {domain}\n")
                if not domain.startswith("www."):
                    block_lines.append(f"127.0.0.1 www.{domain}\n")
            block_lines.append(END_MARKER + "\n")
            clean_lines.extend(block_lines)

        # Guardar en el archivo hosts original
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.writelines(clean_lines)
            
        print("[HostsManager] Archivo hosts actualizado exitosamente.")
        return True
    except PermissionError as e:
        print("[HostsManager] Error de Permisos al escribir en hosts. ¿Se ejecuta como Administrador?")
        raise e
    except Exception as e:
        print(f"[HostsManager] Error al modificar archivo hosts: {e}")
        return False

def restore_hosts():
    """Limpia todos los dominios bloqueados por nuestra app en el archivo hosts."""
    try:
        if not os.path.exists(HOSTS_PATH):
            return True
            
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        clean_lines = clean_hosts_content(lines)

        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.writelines(clean_lines)
            
        print("[HostsManager] Filtro de hosts restaurado (limpio).")
        return True
    except PermissionError as e:
        print("[HostsManager] Error de Permisos al limpiar hosts. ¿Se ejecuta como Administrador?")
        raise e
    except Exception as e:
        print(f"[HostsManager] Error al restaurar archivo hosts: {e}")
        return False
