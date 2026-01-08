import flet as ft
import logging
import os
from utils.theme import DesignSystem
from utils.persistence import get_user_data_dir
from views.home_view import view_home
from views.ficha_view import view_ficha
from views.laboratorio_view import view_laboratorio
from views.guias_view import view_guias
from views.calculadoras_view import view_calculadoras
from views.plantillas_view import view_plantillas
from views.directorio_view import view_directorio
from views.procedimientos_view import view_procedimientos
from views.electro_view import view_electro

# --- CONFIGURACIÓN DE LOGS ---
try:
    log_dir = get_user_data_dir()
    log_file = log_dir / "debug_errors.log"
    logging.basicConfig(
        filename=str(log_file), 
        level=logging.ERROR, 
        format='%(asctime)s %(levelname)s:%(message)s'
    )
except Exception:
    pass

def main(page: ft.Page):
    
    # 1. Configuración General
    page.title = "Internitos Pro"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = DesignSystem.BACKGROUND
    
    # Fuentes
    page.fonts = {"Roboto": "/fonts/Roboto-Regular.ttf"}
    page.theme = ft.Theme(font_family="Roboto")

    # 2. Navegación con Caché
    main_container = ft.Container(expand=True)
    vistas_cache = {} 

    def cambiar_ruta(e):
        try:
            idx = e.control.selected_index if hasattr(e, "control") else int(e)
            
            if rail.selected_index != idx:
                rail.selected_index = idx
                rail.update() 
            
            rutas_map = {
                0: lambda: view_home(page, on_nav=cambiar_ruta),
                1: lambda: view_ficha(page),
                2: lambda: view_laboratorio(page),
                3: lambda: view_guias(page),
                4: lambda: view_calculadoras(page),
                5: lambda: view_plantillas(page),
                6: lambda: view_directorio(page),
                7: lambda: view_procedimientos(page),
                8: lambda: view_electro(page)
            }

            cacheable_indices = [0, 2, 3, 4, 7, 8] # Vistas estáticas

            if idx in rutas_map:
                if idx in cacheable_indices:
                    if idx not in vistas_cache:
                        vistas_cache[idx] = rutas_map[idx]()
                    main_container.content = vistas_cache[idx]
                else:
                    main_container.content = rutas_map[idx]()
                    if idx in vistas_cache: del vistas_cache[idx]
            
            page.update()
        
        except Exception as ex:
            logging.error(f"Error nav ruta {idx}: {ex}", exc_info=True)
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"))
            page.snack_bar.open = True
            page.update()

    # CORRECCIÓN: Uso de strings para iconos
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=180,
        bgcolor=DesignSystem.SURFACE,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(icon="home", label="Inicio"),
            ft.NavigationRailDestination(icon="insert_drive_file", label="Ficha"),
            ft.NavigationRailDestination(icon="science", label="Lab"),
            ft.NavigationRailDestination(icon="book", label="Guías"),
            ft.NavigationRailDestination(icon="calculate", label="Calc"),
            ft.NavigationRailDestination(icon="description", label="Plantillas"),
            ft.NavigationRailDestination(icon="phone", label="Directorio"),
            ft.NavigationRailDestination(icon="healing", label="Proced."),
            ft.NavigationRailDestination(icon="favorite", label="ECG"),
        ],
        on_change=cambiar_ruta
    )

    # 3. Botón Tema
    def toggle_theme(e):
        es_claro = page.theme_mode == ft.ThemeMode.LIGHT
        page.theme_mode = ft.ThemeMode.DARK if es_claro else ft.ThemeMode.LIGHT
        page.bgcolor = "#111827" if es_claro else DesignSystem.BACKGROUND
        rail.bgcolor = "#1F2937" if es_claro else DesignSystem.SURFACE
        e.control.icon = "light_mode" if es_claro else "dark_mode"
        page.update()

    btn_theme = ft.IconButton("dark_mode", on_click=toggle_theme)

    # 4. Estructura Final
    page.add(
        ft.Row([
            ft.Column([
                ft.Container(rail, expand=True),
                # CORRECCIÓN: ft.alignment.center -> ft.Alignment(0,0)
                ft.Container(btn_theme, padding=20, alignment=ft.Alignment(0, 0))
            ], width=80, spacing=0),
            ft.VerticalDivider(width=1, color="#E2E8F0"),
            main_container
        ], expand=True, spacing=0)
    )

    cambiar_ruta(0)

if __name__ == "__main__":
    # Usamos ft.app para iniciar. La advertencia sobre run() puede ignorarse en la mayoría de versiones actuales
    # si usamos target=main. Si falla, intenta ft.app(main).
    try:
        ft.app(target=main, assets_dir="assets")
    except Exception as e:
        print(f"Error fatal: {e}")