import flet as ft
import json
import os
import copy
import base64
from utils.persistence import init_database, get_user_data_dir

# --- SEGURIDAD ROBUSTA ---
# Intentamos usar criptografía real, si falla, usamos fallback a Base64
HAS_CRYPTO = False
cipher_suite = None

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    pass # Se manejará con fallback

FILE_DB = init_database("db_directorio.json", merge_key="Unidad")
USER_DATA_DIR = str(get_user_data_dir())
KEY_FILE = os.path.join(USER_DATA_DIR, "secret.key")

def init_cipher():
    global cipher_suite
    if not HAS_CRYPTO: return

    # Generar o cargar llave
    if not os.path.exists(KEY_FILE):
        try:
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as kf:
                kf.write(key)
        except Exception as e:
            print(f"Error escribiendo llave crypto: {e}")
            return
            
    try:
        with open(KEY_FILE, "rb") as kf:
            key = kf.read()
        cipher_suite = Fernet(key)
    except Exception as e:
        print(f"Error cargando llave crypto: {e}")

# Inicializamos
init_cipher()

def encrypt_text(text):
    if not text: return ""
    try:
        if cipher_suite:
            return cipher_suite.encrypt(text.encode()).decode()
        else:
            # Fallback simple (ofuscación) para no romper la app
            return "B64:" + base64.b64encode(text.encode()).decode()
    except:
        return text

def decrypt_text(text):
    if not text: return ""
    try:
        if cipher_suite and not text.startswith("B64:"):
            return cipher_suite.decrypt(text.encode()).decode()
        elif text.startswith("B64:"):
            # Fallback
            return base64.b64decode(text[4:].encode()).decode()
        return text
    except:
        return text # Si falla, devolver original (quizás ya era plano)

# --- GESTIÓN DE DATOS ---
def cargar_contactos():
    if not os.path.exists(FILE_DB): return []
    try:
        with open(FILE_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Desencriptar en memoria
            for item in data:
                if "Contraseña" in item:
                    item["Contraseña"] = decrypt_text(item["Contraseña"])
            return data
    except:
        return []

def guardar_contactos(data_original):
    # Encriptar copia para disco
    data_to_save = copy.deepcopy(data_original)
    for item in data_to_save:
        if "Contraseña" in item:
            item["Contraseña"] = encrypt_text(item["Contraseña"])
            
    with open(FILE_DB, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)

# --- VISTA ---
def view_directorio(page: ft.Page):
    COLOR_PRIMARY = "#005EB8"
    contactos = cargar_contactos()
    edit_index = [-1]

    # Alerta de seguridad si no hay crypto real
    security_warning = ft.Container()
    if not HAS_CRYPTO or not cipher_suite:
        security_warning = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.WARNING, color="orange"), 
                ft.Text("Modo Compatibilidad: Cifrado débil (Librería 'cryptography' no activa).", color="orange", size=12)
            ]),
            bgcolor="#FFF7ED", padding=10, border_radius=5
        )

    # Campos Editor
    d_unidad = ft.TextField(label="Unidad")
    d_anexo = ft.TextField(label="Anexo", width=100)
    d_usuario = ft.TextField(label="Usuario", width=150)
    d_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=150)
    d_ubicacion = ft.TextField(label="Ubicación")
    d_notas = ft.TextField(label="Notas", multiline=True)

    def guardar_cambios(e):
        item = {
            "Unidad": d_unidad.value, "Anexo": d_anexo.value,
            "Usuario": d_usuario.value, "Contraseña": d_pass.value,
            "Ubicación": d_ubicacion.value, "Notas": d_notas.value
        }
        if edit_index[0] == -1: contactos.append(item)
        else: contactos[edit_index[0]] = item
        
        guardar_contactos(contactos)
        refrescar_tabla()
        dlg_editor.open = False
        page.update()

    dlg_editor = ft.AlertDialog(
        title=ft.Text("Contacto"),
        content=ft.Column([d_unidad, ft.Row([d_anexo, d_ubicacion]), ft.Row([d_usuario, d_pass]), d_notas], height=300, scroll=ft.ScrollMode.AUTO),
        actions=[ft.ElevatedButton("Guardar", on_click=guardar_cambios)]
    )

    def abrir_editor(idx=None):
        edit_index[0] = idx if idx is not None else -1
        if idx is not None:
            c = contactos[idx]
            d_unidad.value = c.get("Unidad", "")
            d_anexo.value = c.get("Anexo", "")
            d_usuario.value = c.get("Usuario", "")
            d_pass.value = c.get("Contraseña", "")
            d_ubicacion.value = c.get("Ubicación", "")
            d_notas.value = c.get("Notas", "")
        else:
            for ctl in [d_unidad, d_anexo, d_usuario, d_pass, d_ubicacion, d_notas]: ctl.value = ""
        page.open(dlg_editor)

    tabla = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(t)) for t in ["Unidad", "Anexo", "Usuario", "Clave", "Ubicación", "Acciones"]],
        rows=[]
    )
    
    switch_ver = ft.Switch(label="Ver Claves", on_change=lambda e: refrescar_tabla())
    txt_buscar = ft.TextField(prefix_icon=ft.icons.SEARCH, hint_text="Buscar...", expand=True, on_change=lambda e: refrescar_tabla())

    def refrescar_tabla():
        tabla.rows.clear()
        filtro = txt_buscar.value.lower()
        for i, c in enumerate(contactos):
            # Filtrado simple en todos los campos
            if filtro in str(c.values()).lower():
                pw = c.get("Contraseña", "") if switch_ver.value else "••••"
                bg_pw = "#FEF2F2" if switch_ver.value else "transparent"
                
                tabla.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(c.get("Unidad", ""), weight="bold")),
                    ft.DataCell(ft.Text(c.get("Anexo", ""))),
                    ft.DataCell(ft.Text(c.get("Usuario", ""))),
                    ft.DataCell(ft.Container(ft.Text(pw, font_family="monospace"), bgcolor=bg_pw, padding=3, border_radius=4)),
                    ft.DataCell(ft.Text(c.get("Ubicación", ""))),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.icons.EDIT, on_click=lambda e, x=i: abrir_editor(x)),
                        ft.IconButton(ft.icons.DELETE, icon_color="red", on_click=lambda e, x=i: (contactos.pop(x), guardar_contactos(contactos), refrescar_tabla(), page.update()))
                    ]))
                ]))
        page.update()

    refrescar_tabla()

    return ft.Column([
        ft.Row([ft.Text("Directorio Seguro", size=24, weight="bold", color=COLOR_PRIMARY)]),
        security_warning,
        ft.Row([txt_buscar, switch_ver, ft.ElevatedButton("Agregar", on_click=lambda e: abrir_editor())]),
        ft.Container(tabla, scroll=ft.ScrollMode.AUTO, expand=True, border=ft.border.all(1, "#E2E8F0"))
    ], expand=True, padding=10)