import hashlib
import os
from src import config_manager

def generate_salt():
    """Genera una sal aleatoria en formato hexadecimal."""
    return os.urandom(16).hex()

def hash_password(password: str, salt: str) -> str:
    """Aplica el algoritmo SHA-256 combinando la contraseña y la sal."""
    salted_password = password.encode('utf-8') + salt.encode('utf-8')
    return hashlib.sha256(salted_password).hexdigest()

def register_user(username: str, password: str) -> bool:
    """Registra las credenciales del administrador en el archivo de configuración."""
    config = config_manager.load_config()
    salt = generate_salt()
    pw_hash = hash_password(password, salt)
    
    config["username"] = username.strip()
    config["password_hash"] = pw_hash
    config["password_salt"] = salt
    return config_manager.save_config(config)

def verify_login(username: str, password: str) -> bool:
    """Verifica si el usuario y contraseña coinciden con las credenciales registradas."""
    config = config_manager.load_config()
    stored_username = config.get("username", "")
    stored_hash = config.get("password_hash", "")
    stored_salt = config.get("password_salt", "")
    
    if not stored_hash or not stored_salt:
        return False
        
    # Comparación insensible a mayúsculas/minúsculas para el nombre de usuario
    if username.strip().lower() != stored_username.strip().lower():
        return False
        
    pw_hash = hash_password(password, stored_salt)
    return pw_hash == stored_hash

def is_registered() -> bool:
    """Retorna True si ya hay credenciales configuradas en la aplicación."""
    config = config_manager.load_config()
    return bool(config.get("password_hash", ""))
