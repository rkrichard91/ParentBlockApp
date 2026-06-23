import os
import sys
import unittest
from datetime import datetime

# Cambiar el directorio al root para poder importar la carpeta src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import auth, config_manager, scheduler

class TestAuth(unittest.TestCase):
    def test_hashing_and_verification(self):
        """Verifica que el hash de la contraseña sea consistente y valide correctamente."""
        password = "mi_super_clave_segura_123"
        salt = auth.generate_salt()
        
        # 1. Comprobar que el hash es consistente
        hash_1 = auth.hash_password(password, salt)
        hash_2 = auth.hash_password(password, salt)
        self.assertEqual(hash_1, hash_2)
        
        # 2. Comprobar que contraseñas distintas generen hashes distintos
        different_hash = auth.hash_password("otra_clave", salt)
        self.assertNotEqual(hash_1, different_hash)


class TestScheduler(unittest.TestCase):
    def test_time_in_range_standard(self):
        """Prueba rangos horarios normales (mismo día)."""
        # Horario de 08:00 a 17:00
        start = "08:00"
        end = "17:00"
        
        # Caso 1: A las 12:00 (Dentro del rango)
        dt_inside = datetime(2026, 6, 23, 12, 0)
        self.assertTrue(scheduler.BlockingScheduler.is_time_in_range(start, end, dt_inside))
        
        # Caso 2: A las 07:00 (Antes del rango)
        dt_before = datetime(2026, 6, 23, 7, 0)
        self.assertFalse(scheduler.BlockingScheduler.is_time_in_range(start, end, dt_before))
        
        # Caso 3: A las 18:00 (Después del rango)
        dt_after = datetime(2026, 6, 23, 18, 0)
        self.assertFalse(scheduler.BlockingScheduler.is_time_in_range(start, end, dt_after))

    def test_time_in_range_midnight(self):
        """Prueba rangos horarios que cruzan la medianoche."""
        # Horario de 22:00 a 06:00 (Cruza medianoche)
        start = "22:00"
        end = "06:00"
        
        # Caso 1: A las 23:00 (Dentro del rango - antes de medianoche)
        dt_before_midnight = datetime(2026, 6, 23, 23, 0)
        self.assertTrue(scheduler.BlockingScheduler.is_time_in_range(start, end, dt_before_midnight))
        
        # Caso 2: A las 03:00 (Dentro del rango - después de medianoche)
        dt_after_midnight = datetime(2026, 6, 24, 3, 0)
        self.assertTrue(scheduler.BlockingScheduler.is_time_in_range(start, end, dt_after_midnight))
        
        # Caso 3: A las 12:00 (Fuera del rango)
        dt_outside = datetime(2026, 6, 23, 12, 0)
        self.assertFalse(scheduler.BlockingScheduler.is_time_in_range(start, end, dt_outside))

    def test_time_in_range_invalid_format(self):
        """Valida que si el formato de la hora es incorrecto, no ocurra un crash y retorne False."""
        dt = datetime.now()
        self.assertFalse(scheduler.BlockingScheduler.is_time_in_range("invalido", "12:00", dt))
        self.assertFalse(scheduler.BlockingScheduler.is_time_in_range("08:00", "invalido", dt))


class TestConfigManager(unittest.TestCase):
    def test_default_config_loading(self):
        """Comprueba la carga de llaves por defecto en el gestor de configuración."""
        # Respaldar archivo config.json si existe para no estropearlo en el test
        config_path = config_manager.CONFIG_FILE
        backup_config_path = config_path + ".test_bak"
        existed = os.path.exists(config_path)
        
        if existed:
            if os.path.exists(backup_config_path):
                os.remove(backup_config_path)
            os.rename(config_path, backup_config_path)
            
        try:
            # Forzar carga para crear uno nuevo con defaults
            config = config_manager.load_config()
            self.assertIn("active", config)
            self.assertIn("domains", config)
            self.assertIn("start_time", config)
            self.assertIn("end_time", config)
            
            # Limpiar el de prueba creado
            if os.path.exists(config_path):
                os.remove(config_path)
        finally:
            # Restaurar original si existía
            if existed and os.path.exists(backup_config_path):
                os.rename(backup_config_path, config_path)


if __name__ == "__main__":
    unittest.main()
