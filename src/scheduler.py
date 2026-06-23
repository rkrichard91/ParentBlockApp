import time
import threading
from datetime import datetime
from src import config_manager, hosts_manager, local_server

class BlockingScheduler:
    """Administra el bucle secundario que monitorea la hora y activa/desactiva el bloqueo."""
    
    def __init__(self):
        self.server = local_server.MultiServer()
        self.thread = None
        self.running = False
        self.currently_blocking = False
        self.status_message = "Servicio inactivo"
        self._last_domains = []

    def start(self):
        """Inicia el hilo del planificador en segundo plano."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, name="Scheduler-Loop", daemon=True)
        self.thread.start()
        print("[Scheduler] Bucle del planificador iniciado.")

    def stop(self):
        """Detiene el bucle del planificador y limpia los bloqueos activos."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        # Asegurar de remover el bloqueo de hosts y apagar el servidor al salir
        self._deactivate_blocking()
        self.status_message = "Servicio apagado"
        print("[Scheduler] Bucle del planificador detenido.")

    def force_reload(self):
        """Fuerza al planificador a revisar los dominios y aplicarlos inmediatamente si está bloqueando."""
        if self.currently_blocking:
            config = config_manager.load_config()
            domains = config.get("domains", [])
            print("[Scheduler] Recargando lista de dominios bloqueados en caliente...")
            hosts_manager.write_domains(domains)
            self._last_domains = list(domains)

    def _loop(self):
        while self.running:
            try:
                config = config_manager.load_config()
                is_active = config.get("active", False)
                domains = config.get("domains", [])
                start_time_str = config.get("start_time", "08:00")
                end_time_str = config.get("end_time", "17:00")
                
                in_range = self.is_time_in_range(start_time_str, end_time_str)
                
                if is_active and in_range and domains:
                    # Si no estaba bloqueando, o si los dominios cambiaron, actualizamos
                    if not self.currently_blocking or domains != self._last_domains:
                        print("[Scheduler] Entrando en rango horario de bloqueo. Activando...")
                        self._activate_blocking(domains)
                        self._last_domains = list(domains)
                    
                    # Reportar estado
                    if self.server.http_error or self.server.https_error:
                        errors = []
                        if self.server.http_error:
                            errors.append(f"HTTP 80 ({self.server.http_error})")
                        if self.server.https_error:
                            errors.append(f"HTTPS 443 ({self.server.https_error})")
                        self.status_message = f"BLOQUEO ACTIVO con problemas: {', '.join(errors)}"
                    else:
                        self.status_message = "BLOQUEO ACTIVO - Servidores interceptores corriendo"
                else:
                    # Si estaba bloqueando, limpiar
                    if self.currently_blocking:
                        print("[Scheduler] Saliendo de rango horario o bloqueo desactivado. Limpiando...")
                        self._deactivate_blocking()
                    
                    if not is_active:
                        self.status_message = "Servicio inactivo (Filtro apagado en panel)"
                    elif not domains:
                        self.status_message = "Filtro encendido, pero no hay dominios configurados"
                    else:
                        self.status_message = f"Fuera de horario de bloqueo (Horario: {start_time_str} a {end_time_str})"
                        
            except Exception as e:
                print(f"[Scheduler] Error en ciclo de planificación: {e}")
                self.status_message = f"Error: {e}"
                
            # Dormir 5 segundos (comprobando el estado de apagado frecuentemente)
            for _ in range(5):
                if not self.running:
                    break
                time.sleep(1)

    def _activate_blocking(self, domains):
        try:
            # 1. Modificar archivo hosts
            hosts_manager.write_domains(domains)
            # 2. Iniciar servidor local HTTP y HTTPS
            self.server.start()
            self.currently_blocking = True
        except Exception as e:
            print(f"[Scheduler] Excepción al activar bloqueo: {e}")

    def _deactivate_blocking(self):
        try:
            # 1. Restaurar archivo hosts
            hosts_manager.restore_hosts()
            # 2. Apagar servidor local
            self.server.stop()
            self.currently_blocking = False
            self._last_domains = []
        except Exception as e:
            print(f"[Scheduler] Excepción al desactivar bloqueo: {e}")

    @staticmethod
    def is_time_in_range(start_str, end_str, current_dt=None):
        """Determina si la hora actual entra en el rango configurado (soporta cruce de medianoche)."""
        if current_dt is None:
            current_dt = datetime.now()
            
        try:
            start_t = datetime.strptime(start_str.strip(), "%H:%M").time()
            end_t = datetime.strptime(end_str.strip(), "%H:%M").time()
        except ValueError:
            return False
            
        now_t = current_dt.time()
        
        if start_t <= end_t:
            return start_t <= now_t <= end_t
        else:  # Cruce de medianoche (ej. de 22:00 a 06:00)
            return now_t >= start_t or now_t <= end_t
