import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

DEFAULT_CONFIG = {
    "username": "",
    "password_hash": "",
    "password_salt": "",
    "domains": [],
    "start_time": "08:00",
    "end_time": "17:00",
    "active": False
}

def load_config():
    """Carga la configuración desde config.json. Si no existe, crea una por defecto."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Asegurar que todas las llaves por defecto existan
            for key, val in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = val
            return config
    except Exception as e:
        print(f"Error cargando la configuración: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Guarda la configuración actual en config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando la configuración: {e}")
        return False
