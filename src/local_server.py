import os
import ssl
import threading
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from src import cert_generator, config_manager

# Ruta a la plantilla bloqueado.html
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = sys._MEIPASS
else:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
HTML_TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "templates", "bloqueado.html")

class BlockedHandler(BaseHTTPRequestHandler):
    """Manejador HTTP que responde con bloqueado.html a todas las solicitudes."""
    
    def log_message(self, format, *args):
        # Sobrescribir para evitar imprimir peticiones HTTP/HTTPS en la consola
        pass

    def handle_http_request(self):
        """Envía el archivo bloqueado.html al cliente."""
        try:
            config = config_manager.load_config()
            custom_message = config.get("custom_message", "Este sitio ha sido bloqueado temporalmente por tu filtro de enfoque para ayudarte a mantener la concentración.")
            
            if os.path.exists(HTML_TEMPLATE_PATH):
                with open(HTML_TEMPLATE_PATH, "r", encoding="utf-8") as f:
                    html_content = f.read()
                html_content = html_content.replace("{{CUSTOM_MESSAGE}}", custom_message)
            else:
                html_content = (
                    "<!DOCTYPE html><html><head><meta charset='utf-8'></head>"
                    "<body><h1>Sitio Bloqueado</h1>"
                    f"<p>{custom_message}</p></body></html>"
                )
                
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            # Evitar el almacenamiento en caché del navegador
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))
        except Exception as e:
            try:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error interno del servidor de bloqueo: {e}".encode("utf-8"))
            except Exception:
                pass

    def do_GET(self):
        self.handle_http_request()

    def do_POST(self):
        self.handle_http_request()
        
    def do_PUT(self):
        self.handle_http_request()

    def do_DELETE(self):
        self.handle_http_request()


class MultiServer:
    """Administra los servidores HTTP (puerto 80) y HTTPS (puerto 443) en hilos separados."""
    
    def __init__(self):
        self.http_server = None
        self.https_server = None
        self.http_thread = None
        self.https_thread = None
        self.is_running = False
        
        # Guardar errores de enlace de puerto
        self.http_error = None
        self.https_error = None

    def start(self):
        """Inicia los servidores HTTP y HTTPS."""
        if self.is_running:
            return
            
        self.is_running = True
        self.http_error = None
        self.https_error = None
        
        # 1. Asegurar certificados SSL
        cert_path, key_path = cert_generator.generate_self_signed_cert()
        
        # 2. Hilo del Servidor HTTP
        def run_http():
            try:
                self.http_server = HTTPServer(('127.0.0.1', 80), BlockedHandler)
                print("[Server] Servidor HTTP iniciado en 127.0.0.1:80.")
                self.http_server.serve_forever()
            except Exception as e:
                self.http_error = str(e)
                print(f"[Server] Error al iniciar HTTP en puerto 80: {e}")

        # 3. Hilo del Servidor HTTPS
        def run_https():
            try:
                self.https_server = HTTPServer(('127.0.0.1', 443), BlockedHandler)
                
                # Envolver el socket con SSL/TLS
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(certfile=cert_path, keyfile=key_path)
                
                self.https_server.socket = context.wrap_socket(
                    self.https_server.socket,
                    server_side=True
                )
                print("[Server] Servidor HTTPS iniciado en 127.0.0.1:443.")
                self.https_server.serve_forever()
            except Exception as e:
                self.https_error = str(e)
                print(f"[Server] Error al iniciar HTTPS en puerto 443: {e}")

        self.http_thread = threading.Thread(target=run_http, name="HTTP-Server", daemon=True)
        self.https_thread = threading.Thread(target=run_https, name="HTTPS-Server", daemon=True)
        
        self.http_thread.start()
        self.https_thread.start()

    def stop(self):
        """Detiene de forma limpia los servidores HTTP y HTTPS."""
        if not self.is_running:
            return
            
        print("[Server] Deteniendo servidores HTTP y HTTPS...")
        self.is_running = False
        
        if self.http_server:
            try:
                self.http_server.shutdown()
                self.http_server.server_close()
            except Exception as e:
                print(f"[Server] Error cerrando servidor HTTP: {e}")
            self.http_server = None

        if self.https_server:
            try:
                self.https_server.shutdown()
                self.https_server.server_close()
            except Exception as e:
                print(f"[Server] Error cerrando servidor HTTPS: {e}")
            self.https_server = None

        # Esperar a que los hilos cierren de forma segura
        if self.http_thread:
            self.http_thread.join(timeout=2.0)
            self.http_thread = None
            
        if self.https_thread:
            self.https_thread.join(timeout=2.0)
            self.https_thread = None
            
        print("[Server] Servidores de bloqueo apagados.")
