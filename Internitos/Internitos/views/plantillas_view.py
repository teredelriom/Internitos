import flet as ft
import json
import os
# CORRECCIÓN: Importar desde persistence, no config
from utils.persistence import init_database

# --- GESTIÓN DE DATOS ---
FILE_DB = init_database("db_plantillas_hsjd.json")

def cargar_plantillas():
    # CORRECCIÓN: Usar os.path.exists
    if not os.path.exists(FILE_DB):
        return []
    try:
        with open(FILE_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def guardar_plantillas_db(data):
    # CORRECCIÓN: Guardar directamente en FILE_DB (ruta segura AppData)
    try:
        with open(FILE_DB, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando: {e}")

def view_plantillas(page: ft.Page):
    
    COLOR_PRIMARY = "#005EB8"
    COLOR_BG_SIDE = "#F8FAFC"
    
    lista_docs = cargar_plantillas()

    # --- EDITOR (Derecha) ---
    txt_titulo = ft.Text("Selecciona una plantilla", size=20, weight="bold", color="grey")
    txt_editor = ft.TextField(multiline=True, min_lines=20, expand=True, bgcolor="white", hint_text="Contenido...")

    def copiar_texto(e):
        if txt_editor.value:
            page.set_clipboard(txt_editor.value)
            page.snack_bar = ft.SnackBar(ft.Text("✅ Copiado")); page.snack_bar.open = True; page.update()

    btn_copiar = ft.ElevatedButton("Copiar", icon=ft.icons.COPY, bgcolor=COLOR_PRIMARY, color="white", on_click=copiar_texto, visible=False)
    editor_col = ft.Column([ft.Row([txt_titulo, ft.Container(expand=True), btn_copiar]), ft.Divider(), txt_editor], expand=True, visible=False)
    
    empty = ft.Container(content=ft.Column([ft.Icon(ft.icons.DESCRIPTION, size=60, color="grey"), ft.Text("Selecciona plantilla", color="grey")], alignment="center"), expand=True, alignment=ft.alignment.center)

    def seleccionar(item):
        txt_titulo.value = item.get("titulo", "Doc")
        txt_titulo.color = "black"
        txt_editor.value = item.get("contenido", "")
        btn_copiar.visible = True
        editor_col.visible = True
        empty.visible = False
        page.update()

    # --- LISTA (Izquierda) ---
    lv = ft.ListView(expand=True, spacing=5, padding=10)

    def filtrar(filtro=""):
        lv.controls.clear()
        for item in lista_docs:
            if filtro.lower() in item.get("titulo", "").lower() + item.get("categoria", "").lower():
                # Closure seguro para lambda
                lv.controls.append(ft.Container(
                    content=ft.Column([ft.Text(item.get("titulo", ""), weight="bold"), ft.Text(item.get("categoria", "").upper(), size=10, color="grey")]),
                    padding=10, bgcolor="white", border_radius=8, border=ft.border.all(1, "#E2E8F0"),
                    on_click=lambda e, x=item: seleccionar(x)
                ))
        page.update()

    # --- DIALOGO NUEVO ---
    n_tit = ft.TextField(label="Título")
    n_cat = ft.Dropdown(label="Categoría", options=[ft.dropdown.Option("General"), ft.dropdown.Option("Alta"), ft.dropdown.Option("Procedimientos")], value="General")
    n_con = ft.TextField(label="Contenido", multiline=True)
    
    def guardar_nuevo(e):
        if not n_tit.value: return
        lista_docs.append({"titulo": n_tit.value, "categoria": n_cat.value, "contenido": n_con.value})
        guardar_plantillas_db(lista_docs)
        filtrar()
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(title=ft.Text("Nueva Plantilla"), content=ft.Column([n_tit, n_cat, n_con], height=300), actions=[ft.ElevatedButton("Guardar", on_click=guardar_nuevo)])

    filtrar()

    return ft.Row([
        ft.Container(content=ft.Column([
            ft.Text("Plantillas", weight="bold", size=18, color=COLOR_PRIMARY),
            ft.Row([ft.TextField(hint_text="Buscar...", on_change=lambda e: filtrar(e.control.value), expand=True), ft.IconButton(ft.icons.ADD_CIRCLE, icon_color=COLOR_PRIMARY, on_click=lambda e: page.open(dlg))]),
            lv
        ]), width=300, bgcolor=COLOR_BG_SIDE, padding=10, border=ft.border.only(right=ft.border.BorderSide(1, "#E2E8F0"))),
        ft.Container(content=ft.Stack([empty, editor_col]), expand=True, padding=20, bgcolor="white")
    ], expand=True, spacing=0)