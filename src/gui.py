import re
import customtkinter as ctk
from src import auth, config_manager, scheduler

# Establecer la apariencia por defecto
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RegisterFrame(ctk.CTkFrame):
    """Pantalla para registrar las credenciales de administrador por primera vez."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Título
        title_label = ctk.CTkLabel(
            self, 
            text="Configuración Inicial", 
            font=ctk.CTkFont(family="Inter", size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        desc_label = ctk.CTkLabel(
            self, 
            text="Define un usuario y contraseña para restringir el acceso a la configuración del bloqueo parental.",
            wraplength=380,
            text_color="#94a3b8",
            font=ctk.CTkFont(family="Inter", size=13)
        )
        desc_label.pack(pady=(0, 20))
        
        # Formulario
        self.username_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Nombre de usuario administrador", 
            width=320,
            height=40
        )
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Contraseña", 
            show="*", 
            width=320,
            height=40
        )
        self.password_entry.pack(pady=10)
        
        self.confirm_password_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Confirmar contraseña", 
            show="*", 
            width=320,
            height=40
        )
        self.confirm_password_entry.pack(pady=10)
        
        # Etiqueta de error/información
        self.info_label = ctk.CTkLabel(self, text="", text_color="#ef4444", font=ctk.CTkFont(family="Inter", size=12))
        self.info_label.pack(pady=5)
        
        # Botón guardar
        save_btn = ctk.CTkButton(
            self, 
            text="Crear Cuenta y Continuar", 
            command=self.register, 
            width=320,
            height=45,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold")
        )
        save_btn.pack(pady=20)
        
    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_password_entry.get()
        
        if not username:
            self.info_label.configure(text="El usuario no puede estar vacío.", text_color="#ef4444")
            return
        if len(password) < 4:
            self.info_label.configure(text="La contraseña debe tener al menos 4 caracteres.", text_color="#ef4444")
            return
        if password != confirm:
            self.info_label.configure(text="Las contraseñas no coinciden.", text_color="#ef4444")
            return
            
        success = auth.register_user(username, password)
        if success:
            self.info_label.configure(text="¡Registro exitoso! Iniciando...", text_color="#22c55e")
            self.after(1000, self.controller.show_appropriate_frame)
        else:
            self.info_label.configure(text="Error al guardar la configuración.", text_color="#ef4444")


class LoginFrame(ctk.CTkFrame):
    """Pantalla de inicio de sesión."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Título
        title_label = ctk.CTkLabel(
            self, 
            text="Acceso de Administrador", 
            font=ctk.CTkFont(family="Inter", size=24, weight="bold")
        )
        title_label.pack(pady=(40, 10))
        
        desc_label = ctk.CTkLabel(
            self, 
            text="Introduce tus credenciales para acceder al Panel de Control.",
            text_color="#94a3b8",
            font=ctk.CTkFont(family="Inter", size=13)
        )
        desc_label.pack(pady=(0, 30))
        
        # Inputs
        self.username_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Usuario", 
            width=320,
            height=40
        )
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Contraseña", 
            show="*", 
            width=320,
            height=40
        )
        self.password_entry.pack(pady=10)
        
        self.error_label = ctk.CTkLabel(self, text="", text_color="#ef4444", font=ctk.CTkFont(family="Inter", size=12))
        self.error_label.pack(pady=5)
        
        # Botón de Login
        login_btn = ctk.CTkButton(
            self, 
            text="Iniciar Sesión", 
            command=self.login, 
            width=320,
            height=45,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold")
        )
        login_btn.pack(pady=20)
        
        # Permitir hacer submit con Enter
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.username_entry.bind("<Return>", lambda e: self.login())
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if auth.verify_login(username, password):
            self.error_label.configure(text="Acceso concedido.", text_color="#22c55e")
            self.after(500, self.controller.login_success)
        else:
            self.error_label.configure(text="Usuario o contraseña incorrectos.", text_color="#ef4444")
            self.password_entry.delete(0, 'end')


class DashboardFrame(ctk.CTkFrame):
    """Panel de Control principal de la aplicación de bloqueo."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Cargar configuración actual
        self.config = config_manager.load_config()
        
        # Cabecera
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 15))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Filtro de Enfoque", 
            font=ctk.CTkFont(family="Inter", size=22, weight="bold")
        )
        title_label.pack(side="left")
        
        # Switch de encendido
        self.switch_var = ctk.StringVar(value="on" if self.config.get("active", False) else "off")
        self.active_switch = ctk.CTkSwitch(
            header_frame, 
            text="Activo", 
            command=self.toggle_active,
            variable=self.switch_var,
            onvalue="on",
            offvalue="off",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold")
        )
        self.active_switch.pack(side="right")
        
        # Sección 1: Horario de Bloqueo
        time_frame = ctk.CTkLabel(self, text="Horario de Bloqueo", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), anchor="w")
        time_frame.pack(fill="x", pady=(5, 5))
        
        inputs_time_frame = ctk.CTkFrame(self, fg_color="#202020", border_width=1, border_color="#2d2d2d", corner_radius=10)
        inputs_time_frame.pack(fill="x", pady=(0, 15), padx=2)
        
        # Inputs de hora
        inner_time_frame = ctk.CTkFrame(inputs_time_frame, fg_color="transparent")
        inner_time_frame.pack(pady=10, padx=15, fill="x")
        
        ctk.CTkLabel(inner_time_frame, text="Inicio (HH:MM):", font=ctk.CTkFont(family="Inter", size=12)).grid(row=0, column=0, padx=(0,5), sticky="w")
        self.start_entry = ctk.CTkEntry(inner_time_frame, width=70, height=28)
        self.start_entry.insert(0, self.config.get("start_time", "08:00"))
        self.start_entry.grid(row=0, column=1, padx=(0,15))
        
        ctk.CTkLabel(inner_time_frame, text="Fin (HH:MM):", font=ctk.CTkFont(family="Inter", size=12)).grid(row=0, column=2, padx=(0,5), sticky="w")
        self.end_entry = ctk.CTkEntry(inner_time_frame, width=70, height=28)
        self.end_entry.insert(0, self.config.get("end_time", "17:00"))
        self.end_entry.grid(row=0, column=3, padx=(0,15))
        
        self.save_time_btn = ctk.CTkButton(
            inner_time_frame, 
            text="Guardar", 
            command=self.save_schedule,
            width=80,
            height=28,
            font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        )
        self.save_time_btn.grid(row=0, column=4, sticky="e")
        
        # Configurar grid resizing
        inner_time_frame.columnconfigure(4, weight=1)
        
        # Mensaje de error para horario
        self.time_error_label = ctk.CTkLabel(inputs_time_frame, text="", text_color="#ef4444", font=ctk.CTkFont(family="Inter", size=11))
        self.time_error_label.pack(pady=(0, 5))
        
        # Sección 2: Dominios Bloqueados
        ctk.CTkLabel(self, text="Dominios a Bloquear", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), anchor="w").pack(fill="x", pady=(5, 5))
        
        # Input para agregar dominio
        add_domain_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_domain_frame.pack(fill="x", pady=(0, 10))
        
        self.domain_entry = ctk.CTkEntry(
            add_domain_frame, 
            placeholder_text="ej: facebook.com o youtube.com", 
            height=35
        )
        self.domain_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.domain_entry.bind("<Return>", lambda e: self.add_domain())
        
        add_domain_btn = ctk.CTkButton(
            add_domain_frame, 
            text="Añadir", 
            command=self.add_domain,
            width=90,
            height=35,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold")
        )
        add_domain_btn.pack(side="right")
        
        self.domain_error_label = ctk.CTkLabel(self, text="", text_color="#ef4444", font=ctk.CTkFont(family="Inter", size=11))
        self.domain_error_label.pack(pady=(0, 5))
        
        # Lista scrollable de dominios
        self.domains_list_frame = ctk.CTkScrollableFrame(
            self, 
            height=120, 
            fg_color="#1b1b1b",
            border_width=1,
            border_color="#2d2d2d"
        )
        self.domains_list_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Rellenar lista de dominios al inicializar
        self.populate_domains_list()
        
        # Sección 3: Mensaje de Bloqueo Personalizado
        ctk.CTkLabel(self, text="Mensaje de Bloqueo Personalizado", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), anchor="w").pack(fill="x", pady=(5, 5))
        
        custom_msg_frame = ctk.CTkFrame(self, fg_color="transparent")
        custom_msg_frame.pack(fill="x", pady=(0, 10))
        
        self.custom_msg_entry = ctk.CTkEntry(
            custom_msg_frame, 
            placeholder_text="ej: ¡Hora de estudiar! Este sitio está bloqueado.", 
            height=35
        )
        self.custom_msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.custom_msg_entry.insert(0, self.config.get("custom_message", "Este sitio ha sido bloqueado temporalmente por tu filtro de enfoque para ayudarte a mantener la concentración."))
        
        save_msg_btn = ctk.CTkButton(
            custom_msg_frame, 
            text="Guardar", 
            command=self.save_custom_message,
            width=90,
            height=35,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold")
        )
        save_msg_btn.pack(side="right")
        
        self.msg_status_label = ctk.CTkLabel(self, text="", text_color="#22c55e", font=ctk.CTkFont(family="Inter", size=11))
        self.msg_status_label.pack(pady=(0, 5))
        
        # Barra de estado inferior
        status_container = ctk.CTkFrame(self, fg_color="#202020", height=40, corner_radius=8)
        status_container.pack(fill="x", side="bottom")
        
        self.status_label = ctk.CTkLabel(
            status_container, 
            text="Iniciando servicio...", 
            text_color="#94a3b8",
            font=ctk.CTkFont(family="Inter", size=12, weight="normal")
        )
        self.status_label.pack(padx=15, pady=8, side="left")
        
    def toggle_active(self):
        is_active = (self.switch_var.get() == "on")
        self.config["active"] = is_active
        config_manager.save_config(self.config)
        print(f"[GUI] Bloqueo parental general: {'ENCENDIDO' if is_active else 'APAGADO'}")
        
    def save_schedule(self):
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        
        # Validar formato HH:MM
        time_regex = re.compile(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
        if not time_regex.match(start) or not time_regex.match(end):
            self.time_error_label.configure(text="Formato de hora incorrecto. Debe ser HH:MM (00:00 - 23:59)", text_color="#ef4444")
            return
            
        self.config["start_time"] = start
        self.config["end_time"] = end
        config_manager.save_config(self.config)
        self.time_error_label.configure(text="¡Horario guardado correctamente!", text_color="#22c55e")
        self.after(2000, lambda: self.time_error_label.configure(text=""))
        
    def save_custom_message(self):
        message = self.custom_msg_entry.get().strip()
        if not message:
            message = "Este sitio ha sido bloqueado temporalmente por tu filtro de enfoque para ayudarte a mantener la concentración."
        self.config["custom_message"] = message
        config_manager.save_config(self.config)
        self.msg_status_label.configure(text="¡Mensaje guardado correctamente!", text_color="#22c55e")
        self.after(2000, lambda: self.msg_status_label.configure(text=""))
        
    def add_domain(self):
        domain = self.domain_entry.get().strip().lower()
        if not domain:
            return
            
        # Remover protocolos o www si el usuario los escribió
        domain = re.sub(r"^https?://", "", domain)
        domain = re.sub(r"^www\.", "", domain)
        domain = domain.split("/")[0] # Tomar solo el host
        
        # Validación básica de dominios
        domain_regex = re.compile(r"^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$")
        if not domain_regex.match(domain):
            self.domain_error_label.configure(text="El dominio ingresado no es válido.")
            return
            
        self.domain_error_label.configure(text="")
        
        if domain not in self.config["domains"]:
            self.config["domains"].append(domain)
            config_manager.save_config(self.config)
            self.populate_domains_list()
            self.domain_entry.delete(0, 'end')
            
            # Recargar el planificador inmediatamente
            self.controller.scheduler.force_reload()
        else:
            self.domain_error_label.configure(text="El dominio ya está en la lista.")
            
    def remove_domain(self, domain):
        if domain in self.config["domains"]:
            self.config["domains"].remove(domain)
            config_manager.save_config(self.config)
            self.populate_domains_list()
            
            # Recargar el planificador inmediatamente
            self.controller.scheduler.force_reload()
            
    def populate_domains_list(self):
        # Limpiar elementos actuales en la lista scrollable
        for widget in self.domains_list_frame.winfo_children():
            widget.destroy()
            
        domains = self.config.get("domains", [])
        if not domains:
            no_domains_label = ctk.CTkLabel(
                self.domains_list_frame, 
                text="No hay páginas bloqueadas todavía.", 
                text_color="#64748b",
                font=ctk.CTkFont(family="Inter", size=12, slant="italic")
            )
            no_domains_label.pack(pady=40)
            return
            
        for domain in domains:
            item_frame = ctk.CTkFrame(self.domains_list_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=4, padx=5)
            
            domain_lbl = ctk.CTkLabel(
                item_frame, 
                text=domain, 
                font=ctk.CTkFont(family="Inter", size=13),
                anchor="w"
            )
            domain_lbl.pack(side="left", fill="x", expand=True)
            
            # Botón de eliminar
            del_btn = ctk.CTkButton(
                item_frame, 
                text="Eliminar", 
                fg_color="#ef4444", 
                hover_color="#dc2626",
                width=65,
                height=22,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                command=lambda d=domain: self.remove_domain(d)
            )
            del_btn.pack(side="right")


class App(ctk.CTk):
    """Clase principal de la aplicación GUI."""
    
    def __init__(self):
        super().__init__()
        self.title("Control de Enfoque - Bloqueo Parental")
        self.geometry("480x620")
        self.resizable(False, False)
        
        # Inicializar el scheduler de bloqueo en segundo plano
        self.scheduler = scheduler.BlockingScheduler()
        self.scheduler.start()
        
        # Registrar callback de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Contenedor principal de pantallas
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=25, pady=15)
        
        self.current_frame = None
        self.show_appropriate_frame()
        
    def show_appropriate_frame(self):
        """Alterna entre la pantalla de registro de administrador o de inicio de sesión."""
        if self.current_frame:
            self.current_frame.destroy()
            
        if not auth.is_registered():
            self.current_frame = RegisterFrame(self.container, self)
        else:
            self.current_frame = LoginFrame(self.container, self)
            
        self.current_frame.pack(fill="both", expand=True)
        
    def login_success(self):
        """Transiciona al Dashboard después de verificar las credenciales."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = DashboardFrame(self.container, self)
        self.current_frame.pack(fill="both", expand=True)
        
        # Iniciar ciclo de actualización de barra de estado
        self.update_status_loop()
        
    def update_status_loop(self):
        """Bucle para sincronizar la UI con los logs de estado del planificador."""
        if isinstance(self.current_frame, DashboardFrame):
            self.current_frame.status_label.configure(text=self.scheduler.status_message)
            self.after(1000, self.update_status_loop)
            
    def on_closing(self):
        """Controla el apagado limpio al cerrar la ventana principal."""
        print("[GUI] Cerrando ventana principal...")
        self.scheduler.stop()
        self.destroy()

def run_gui():
    app = App()
    app.mainloop()
