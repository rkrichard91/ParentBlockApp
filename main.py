import sys
import os
import ctypes

# Forzar el directorio de trabajo al directorio que contiene el script o ejecutable
# Esto es crítico porque al elevar con UAC ('runas'), Windows resetea 
# el directorio de trabajo actual a C:\Windows\System32.
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
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
        
        if getattr(sys, 'frozen', False):
            # En ejecutable compilado, el ejecutable es el propio programa
            executable = sys.executable
            params = " ".join(f'"{arg}"' for arg in sys.argv[1:])
        else:
            # En script de desarrollo, el ejecutable es python.exe y pasamos el script como argumento
            executable = sys.executable
            params = f'"{os.path.abspath(sys.argv[0])}"'
            if len(sys.argv) > 1:
                params += " " + " ".join(f'"{arg}"' for arg in sys.argv[1:])
            
        try:
            # Invocar el UAC de Windows usando el verbo 'runas'
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                executable,
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
