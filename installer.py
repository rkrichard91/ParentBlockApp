import os
import sys
import shutil
import subprocess
import ctypes
import customtkinter as ctk

# Configuración del tema visual
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

INSTALL_DIR = "C:\\ParentBlockApp"
EXE_NAME = "FiltroEnfoque.exe"
SHORTCUT_NAME = "FiltroEnfoque.lnk"

def is_admin():
    """Verifica si el proceso actual tiene permisos de Administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

class InstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Instalador - Filtro de Enfoque")
        self.geometry("460x320")
        self.resizable(False, False)
        
        # Configurar icono de la ventana
        try:
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(sys._MEIPASS, "ico.ico")
            else:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"[Installer] No se pudo cargar el icono de la ventana: {e}")
            
        # Centrar la ventana
        self.eval('tk::PlaceWindow . center')
        
        # Contenedor principal
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Pantalla de bienvenida
        self.show_welcome_screen()
        
    def show_welcome_screen(self):
        self.clear_container()
        
        # Título
        title_label = ctk.CTkLabel(
            self.container, 
            text="Instalar Filtro de Enfoque", 
            font=ctk.CTkFont(family="Inter", size=22, weight="bold")
        )
        title_label.pack(pady=(10, 10))
        
        desc_text = (
            "Este asistente instalará el Filtro de Enfoque (Control Parental) en tu computadora.\n\n"
            f"• Carpeta de instalación: {INSTALL_DIR}\n"
            "• Se creará un acceso directo en tu Escritorio."
        )
        
        desc_label = ctk.CTkLabel(
            self.container,
            text=desc_text,
            justify="left",
            wraplength=400,
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#cbd5e1"
        )
        desc_label.pack(pady=(10, 20))
        
        # Botones
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")
        
        cancel_btn = ctk.CTkButton(
            btn_frame, 
            text="Cancelar", 
            fg_color="#334155", 
            hover_color="#475569",
            command=self.destroy,
            width=100
        )
        cancel_btn.pack(side="left")
        
        install_btn = ctk.CTkButton(
            btn_frame, 
            text="Instalar", 
            command=self.start_installation,
            width=120,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold")
        )
        install_btn.pack(side="right")
        
    def start_installation(self):
        self.clear_container()
        
        # Título de progreso
        self.progress_title = ctk.CTkLabel(
            self.container, 
            text="Instalando archivos...", 
            font=ctk.CTkFont(family="Inter", size=18, weight="bold")
        )
        self.progress_title.pack(pady=(30, 10))
        
        self.progress_detail = ctk.CTkLabel(
            self.container, 
            text="Preparando el entorno...", 
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#94a3b8"
        )
        self.progress_detail.pack(pady=(0, 15))
        
        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(self.container, width=350)
        self.progress_bar.set(0.1)
        self.progress_bar.pack(pady=10)
        
        self.after(500, self.perform_copy)
        
    def perform_copy(self):
        try:
            # 1. Crear directorio
            self.progress_detail.configure(text=f"Creando directorio {INSTALL_DIR}...")
            self.progress_bar.set(0.3)
            os.makedirs(INSTALL_DIR, exist_ok=True)
            
            # 2. Copiar ejecutable principal
            self.progress_detail.configure(text="Extrayendo ejecutable principal...")
            self.progress_bar.set(0.6)
            
            # Ruta de origen (en sys._MEIPASS de este instalador)
            if getattr(sys, 'frozen', False):
                src_path = os.path.join(sys._MEIPASS, EXE_NAME)
            else:
                src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", EXE_NAME)
                
            dest_path = os.path.join(INSTALL_DIR, EXE_NAME)
            
            # Copiar el archivo
            shutil.copy2(src_path, dest_path)
            
            # 3. Crear acceso directo
            self.progress_detail.configure(text="Creando acceso directo en el escritorio...")
            self.progress_bar.set(0.8)
            self.create_desktop_shortcut(dest_path)
            
            self.progress_bar.set(1.0)
            self.after(500, self.show_success_screen)
            
        except Exception as e:
            self.show_error_screen(str(e))
            
    def create_desktop_shortcut(self, target_exe):
        try:
            # Comando PowerShell para generar el acceso directo de manera limpia
            ps_command = (
                f'$desktop = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop); '
                f'$WshShell = New-Object -ComObject WScript.Shell; '
                f'$Shortcut = $WshShell.CreateShortcut("$desktop\\FiltroEnfoque.lnk"); '
                f'$Shortcut.TargetPath = "{target_exe}"; '
                f'$Shortcut.WorkingDirectory = "{INSTALL_DIR}"; '
                f'$Shortcut.IconLocation = "{target_exe},0"; '
                f'$Shortcut.Save();'
            )
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True, check=True)
        except Exception as e:
            print(f"[Installer] Error creando acceso directo: {e}")
            raise RuntimeError(f"No se pudo crear el acceso directo en el escritorio: {e}")
            
    def show_success_screen(self):
        self.clear_container()
        
        title_label = ctk.CTkLabel(
            self.container, 
            text="¡Instalación Completada!", 
            font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
            text_color="#22c55e"
        )
        title_label.pack(pady=(15, 10))
        
        desc_label = ctk.CTkLabel(
            self.container, 
            text="Filtro de Enfoque se ha instalado con éxito en tu computadora.\n\nPuedes abrir la aplicación usando el acceso directo creado en tu escritorio.",
            wraplength=380,
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#cbd5e1"
        )
        desc_label.pack(pady=(10, 20))
        
        # Botones finales
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")
        
        finish_btn = ctk.CTkButton(
            btn_frame, 
            text="Finalizar", 
            command=self.destroy,
            width=100
        )
        finish_btn.pack(side="left")
        
        launch_btn = ctk.CTkButton(
            btn_frame, 
            text="Iniciar Aplicación", 
            command=self.launch_app,
            width=150,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold")
        )
        launch_btn.pack(side="right")
        
    def show_error_screen(self, error_msg):
        self.clear_container()
        
        title_label = ctk.CTkLabel(
            self.container, 
            text="Error en la Instalación", 
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="#ef4444"
        )
        title_label.pack(pady=(15, 10))
        
        desc_label = ctk.CTkLabel(
            self.container, 
            text=f"Ocurrió un problema al instalar el programa:\n\n{error_msg}\n\nAsegúrate de no tener la aplicación ejecutándose en segundo plano e inténtalo de nuevo.",
            wraplength=380,
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#cbd5e1"
        )
        desc_label.pack(pady=(10, 20))
        
        exit_btn = ctk.CTkButton(
            self.container, 
            text="Salir", 
            command=self.destroy,
            width=120
        )
        exit_btn.pack(side="bottom", pady=10)
        
    def launch_app(self):
        try:
            exe_path = os.path.join(INSTALL_DIR, EXE_NAME)
            # Ejecutar de forma asíncrona desasociando el proceso
            subprocess.Popen([exe_path], close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
        except Exception as e:
            print(f"[Installer] Error iniciando app: {e}")
        self.destroy()
        
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    # 1. Asegurar elevación UAC (es obligatorio para escribir en C:\)
    if not is_admin():
        print("[Installer] Solicitando privilegios de Administrador...")
        
        if getattr(sys, 'frozen', False):
            executable = sys.executable
            params = " ".join(f'"{arg}"' for arg in sys.argv[1:])
        else:
            executable = sys.executable
            params = f'"{os.path.abspath(sys.argv[0])}"'
            if len(sys.argv) > 1:
                params += " " + " ".join(f'"{arg}"' for arg in sys.argv[1:])
                
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                executable,
                params,
                None,
                1
            )
        except Exception as e:
            print(f"[Installer] Error al elevar UAC: {e}")
        sys.exit(0)
        
    # Lanzar interfaz del instalador
    app = InstallerApp()
    app.mainloop()
