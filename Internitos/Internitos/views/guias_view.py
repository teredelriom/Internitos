import flet as ft
import json
import os
import base64
from utils.persistence import init_database

# Manejo robusto de Graphviz (Opcional)
try:
    import graphviz
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

# --- RUTAS ---
# FILE_DB ya contiene la ruta absoluta a AppData/Roaming/...
FILE_DB = init_database("db_guias.json")

# --- PERSISTENCIA ---
def cargar_guias():
    # CORRECCIÓN: Usar os.path.exists, no init_database.exists
    if not os.path.exists(FILE_DB):
        return []
    try:
        with open(FILE_DB, "r", encoding="utf-8") as f:
            content = json.load(f)
            return content if isinstance(content, list) else []
    except:
        return []

def guardar_guias_db(data):
    # CORRECCIÓN: No crear carpeta "data" local. Usar la ruta FILE_DB directa.
    try:
        with open(FILE_DB, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando guías: {e}")

def view_guias(page: ft.Page):
    
    COLOR_PRIMARY = "#005EB8"
    COLOR_BG_SIDE = "#F1F5F9"

    lista_guias = cargar_guias()
    
    # --- ÁREA DE CONTENIDO ---
    title_display = ft.Text("Selecciona una guía", size=28, weight="bold", color=COLOR_PRIMARY)
    tags_row = ft.Row(wrap=True)
    body_markdown = ft.Markdown(
        "", 
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        selectable=True
    )
    diagram_container = ft.Container()
    
    content_area = ft.Column(
        [
            title_display,
            tags_row,
            ft.Divider(),
            body_markdown,
            ft.Divider(),
            ft.Text("Flujograma / Algoritmo", weight="bold", size=18),
            diagram_container
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        visible=False
    )
    
    empty_state = ft.Container(
        content=ft.Column([
            ft.Icon(ft.icons.LIBRARY_BOOKS, size=80, color="grey"),
            ft.Text("Selecciona una guía del menú", size=20, color="grey")
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
        alignment=ft.alignment.center
    )

    # --- RENDER GRAPHVIZ ---
    def render_dot(dot_code):
        if not dot_code: return ft.Text("Sin diagrama.", italic=True)
        if not HAS_GRAPHVIZ:
            return ft.Container(content=ft.Text("⚠️ Graphviz no detectado.", color="red"), padding=5)

        try:
            src = graphviz.Source(dot_code)
            # Verificar si existe ejecutable antes de pipe
            # En Windows a veces falla silenciosamente sin try-catch amplio
            png_bytes = src.pipe(format='png')
            b64 = base64.b64encode(png_bytes).decode('utf-8')
            return ft.Image(src_base64=b64, fit=ft.ImageFit.CONTAIN)
        except graphviz.backend.ExecutableNotFound:
             return ft.Column([
                 ft.Text("Error: Motor Graphviz no instalado.", color="red", weight="bold"),
                 ft.Text("Instale Graphviz en su sistema (PATH).", size=12)
             ])
        except Exception as e:
            return ft.Text(f"Error rendering: {str(e)}", color="red", size=10)

    # --- LÓGICA UI ---
    def mostrar_guia(guia_data):
        title_display.value = guia_data.get("titulo", "Sin Título")
        body_markdown.value = guia_data.get("contenido", "")
        
        tags_row.controls = [
            ft.Container(
                content=ft.Text(tag, size=10, color="white"),
                bgcolor="#64748B", padding=5, border_radius=5
            ) for tag in guia_data.get("tags", [])
        ]
        
        diagram_container.content = ft.ProgressBar()
        page.update()
        diagram_container.content = render_dot(guia_data.get("diagrama_dot", ""))
        
        content_area.visible = True
        empty_state.visible = False
        page.update()

    lv_guias = ft.ListView(expand=True, spacing=5, padding=10)

    def construir_lista(filtro=""):
        lv_guias.controls.clear()
        for item in lista_guias:
            titulo = item.get("titulo", "").lower()
            tags = " ".join(item.get("tags", [])).lower()
            
            if filtro.lower() in titulo or filtro.lower() in tags:
                # Usamos closure explícito para evitar problemas de referencia
                tile = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.BOOKMARK_BORDER, size=16, color=COLOR_PRIMARY),
                        ft.Text(item.get("titulo", "Guía"), size=14, weight=ft.FontWeight.W_500, overflow=ft.TextOverflow.ELLIPSIS, expand=True)
                    ]),
                    padding=10,
                    border_radius=8,
                    bgcolor="white",
                    on_click=lambda e, x=item: mostrar_guia(x),
                    ink=True
                )
                lv_guias.controls.append(tile)
        page.update()

    search_bar = ft.TextField(
        prefix_icon=ft.icons.SEARCH,
        hint_text="Buscar...",
        text_size=14,
        on_change=lambda e: construir_lista(e.control.value),
        bgcolor="white",
        border_radius=8,
        content_padding=10,
        expand=True
    )

    # --- DIÁLOGO AGREGAR ---
    new_titulo = ft.TextField(label="Título")
    new_tags = ft.TextField(label="Tags (sep. por coma)")
    new_contenido = ft.TextField(label="Contenido (Markdown)", multiline=True, min_lines=5)
    new_dot = ft.TextField(label="Código Graphviz (DOT)", multiline=True, min_lines=3, text_size=12, font_family="monospace")

    def guardar_nueva_guia(e):
        if not new_titulo.value:
            new_titulo.error_text = "Requerido"
            new_titulo.update()
            return
        
        tags_list = [t.strip() for t in new_tags.value.split(",") if t.strip()]
        nueva_data = {
            "titulo": new_titulo.value,
            "tags": tags_list,
            "contenido": new_contenido.value,
            "diagrama_dot": new_dot.value
        }
        
        lista_guias.append(nueva_data)
        guardar_guias_db(lista_guias)
        construir_lista()
        
        dlg_add.open = False
        new_titulo.value = ""
        new_tags.value = ""
        new_contenido.value = ""
        new_dot.value = ""
        page.snack_bar = ft.SnackBar(ft.Text("✅ Guía guardada"))
        page.snack_bar.open = True
        page.update()

    dlg_add = ft.AlertDialog(
        title=ft.Text("Nueva Guía"),
        content=ft.Column([new_titulo, new_tags, new_contenido, ft.Text("Diagrama DOT:", size=12), new_dot], width=500, scroll=ft.ScrollMode.AUTO),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: setattr(dlg_add, 'open', False) or page.update()),
            ft.ElevatedButton("Guardar", on_click=guardar_nueva_guia)
        ]
    )

    construir_lista()

    return ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Text("Biblioteca", weight="bold"),
                ft.Row([search_bar, ft.IconButton(ft.icons.ADD_BOX, on_click=lambda e: page.open(dlg_add))]),
                lv_guias
            ]),
            width=280, bgcolor=COLOR_BG_SIDE, padding=10, border=ft.border.only(right=ft.border.BorderSide(1, "#E2E8F0"))
        ),
        ft.Container(content=ft.Stack([empty_state, content_area]), expand=True, padding=20, bgcolor="white")
    ], expand=True, spacing=0)