import sys
import os
import ctypes

# Forzar el directorio de trabajo al directorio que contiene el script
# Esto es crítico porque al elevar con UAC ('runas'), Windows resetea 
# el directorio de trabajo actual a C:\Windows\System32.
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def is_admin():
    """Verifica si el proceso actual tiene permisos de Administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

if __name__ == "__main__":
    if not is_admin():
        print("[Main] Permisos de administrador insuficientes. Solicitando UAC...")
        
        # Obtener ruta absoluta del script y sus argumentos
        script_path = os.path.abspath(sys.argv[0])
        params = f'"{script_path}"'
        
        # Añadir argumentos adicionales si existen
        if len(sys.argv) > 1:
            params += " " + " ".join(f'"{arg}"' for arg in sys.argv[1:])
            
        try:
            # Invocar el UAC de Windows usando el verbo 'runas'
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                params,
                None,
                1  # SW_SHOWNORMAL (mostrar ventana normalmente)
            )
        except Exception as e:
            print(f"[Main] Error al solicitar elevación UAC: {e}")
            
        sys.exit(0)
        
    # Si ya se es Administrador, proceder a lanzar la GUI
    print("[Main] Iniciando aplicación con permisos de Administrador...")
    from src.gui import run_gui
    run_gui()
