import os
import sys
import json
import shutil
from pathlib import Path

# Nombre de la carpeta del sistema en AppData
APP_NAME = "InternitosPro"

def get_base_path():
    """Devuelve la ruta base donde están los assets (soporta PyInstaller/EXE)."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.abspath(".")

def get_user_data_dir():
    """Devuelve la ruta segura (AppData/Roaming) para guardar datos del usuario."""
    home = Path.home()
    if sys.platform == "win32":
        data_dir = home / "AppData" / "Roaming" / APP_NAME
    else:
        data_dir = home / f".{APP_NAME}"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def _merge_json_lists(user_data, default_data, key_field=None):
    """
    Fusiona listas de diccionarios.
    Prioriza los datos del usuario, pero agrega nuevos ítems que vengan en una actualización.
    """
    if not isinstance(user_data, list) or not isinstance(default_data, list):
        return user_data

    if not key_field:
        return user_data

    # Claves que ya tiene el usuario
    existing_keys = {str(item.get(key_field)) for item in user_data if isinstance(item, dict)}
    
    # Agregar solo lo nuevo
    for item in default_data:
        if isinstance(item, dict) and str(item.get(key_field)) not in existing_keys:
            user_data.append(item)
            
    return user_data

def init_database(filename, default_data_folder="data", merge_key=None):
    """
    Inicializa la DB. Si existe, intenta fusionar nuevos datos (updates) sin borrar los del usuario.
    :param merge_key: Campo único (ej: 'titulo', 'Unidad') para detectar nuevos registros.
    """
    user_dir = get_user_data_dir()
    target_file = user_dir / filename
    source_path = os.path.join(get_base_path(), default_data_folder, filename)
    
    # 1. Si no existe en usuario, copiamos el default o creamos vacío
    if not target_file.exists():
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, target_file)
            except Exception as e:
                print(f"Error copiando DB inicial {filename}: {e}")
                _crear_vacio(target_file)
        else:
            _crear_vacio(target_file)
        return str(target_file)

    # 2. Si YA existe y hay un source (update), intentamos fusionar datos nuevos
    if os.path.exists(source_path) and merge_key:
        try:
            with open(target_file, 'r', encoding='utf-8') as f_user:
                user_data = json.load(f_user)
            with open(source_path, 'r', encoding='utf-8') as f_def:
                default_data = json.load(f_def)
            
            if isinstance(user_data, list):
                merged_data = _merge_json_lists(user_data, default_data, merge_key)
                with open(target_file, 'w', encoding='utf-8') as f_out:
                    json.dump(merged_data, f_out, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Advertencia: No se pudieron fusionar datos nuevos en {filename}: {e}")

    return str(target_file)

def _crear_vacio(path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([], f)