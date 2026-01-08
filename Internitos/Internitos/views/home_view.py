import flet as ft
from datetime import datetime
from utils.theme import DesignSystem, GlassCard, GradientCard

def view_home(page: ft.Page, on_nav=None):
    
    # --- BIENVENIDA ---
    now = datetime.now()
    dias = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
    meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 
             7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    
    fecha_str = f"{dias[now.weekday()]} {now.day} de {meses[now.month]}"
    
    header = ft.Row([
        ft.Column([
            ft.Text(f"Hola, Interno 👋", size=32, weight="bold", color=DesignSystem.TEXT_MAIN),
            ft.Text(f"Hoy es {fecha_str} | Turno de Medicina", size=16, color=DesignSystem.TEXT_MUTED),
        ]),
        ft.CircleAvatar(
            content=ft.Icon("person", color="white"), # CORREGIDO: String
            bgcolor=DesignSystem.PRIMARY,
            radius=25
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # --- KPI CARDS ---
    def kpi_box(titulo, valor, icono, subtexto, es_destacado=False):
        content = ft.Column([
            ft.Icon(icono, color="white" if es_destacado else DesignSystem.PRIMARY, size=30),
            ft.Text(valor, size=28, weight="bold", color="white" if es_destacado else DesignSystem.TEXT_MAIN),
            ft.Text(titulo, size=14, color="white" if es_destacado else DesignSystem.TEXT_MUTED),
            ft.Divider(color="white54" if es_destacado else "#E2E8F0", height=10),
            ft.Text(subtexto, size=12, italic=True, color="white70" if es_destacado else "green")
        ], spacing=5)
        
        card = GradientCard(content, expand=True) if es_destacado else GlassCard(content, expand=True)
        return card

    metrics_row = ft.Row([
        kpi_box("Pacientes Activos", "12", "bed", "+2 ingresos hoy", es_destacado=True),
        kpi_box("Pendientes", "3", "pending_actions", "Laboratorios por revisar"),
        kpi_box("Altas Probables", "2", "check_circle", "Para mañana"),
    ], spacing=20)

    # --- ACCESOS RÁPIDOS ---
    def navegar_a(index):
        if on_nav:
            on_nav(index)
        else:
            print(f"Navegación solicitada al índice {index}")

    def quick_action(icon, label, color, ruta_idx):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icon, color=color, size=30),
                    padding=15,
                    bgcolor=ft.Colors.with_opacity(0.1, color),
                    border_radius=12,
                ),
                ft.Text(label, weight="bold", size=13, color=DesignSystem.TEXT_MAIN)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=15,
            border_radius=16,
            bgcolor=DesignSystem.SURFACE,
            shadow=DesignSystem.SHADOW_SM,
            on_click=lambda e: navegar_a(ruta_idx),
            ink=True,
            width=110, height=120,
            alignment=ft.Alignment(0, 0) # CORREGIDO: ft.alignment.center -> ft.Alignment(0,0)
        )

    quick_access = ft.Row([
        quick_action("calculate", "Calculadoras", ft.Colors.ORANGE, 4),
        quick_action("edit_document", "Ficha", ft.Colors.BLUE, 1),
        quick_action("science", "Lab", ft.Colors.PURPLE, 2),
        quick_action("phone", "Directorio", ft.Colors.GREEN, 6),
    ], wrap=True, alignment=ft.MainAxisAlignment.CENTER)

    # --- NOVEDADES ---
    turno_card = GlassCard(
        ft.Column([
            ft.Row([ft.Icon("event_note", color=DesignSystem.SECONDARY), ft.Text("Novedades del Turno", weight="bold")]),
            ft.Divider(),
            ft.ListTile(leading=ft.Icon("warning", color="red"), title=ft.Text("Cama 402: Vigilar K+"), subtitle=ft.Text("Controlar ELP a las 14:00")),
            ft.ListTile(leading=ft.Icon("info", color="blue"), title=ft.Text("Reunión Clínica"), subtitle=ft.Text("Hoy 12:00 hrs en Auditorio")),
        ])
    )

    return ft.Column([
        header,
        ft.Divider(height=30, color="transparent"),
        metrics_row,
        ft.Divider(height=20, color="transparent"),
        ft.Row([
            ft.Column([
                ft.Text("Acceso Rápido", style=DesignSystem.title_style(), size=18),
                quick_access
            ], expand=2),
            ft.Column([
                ft.Text("Pizarra", style=DesignSystem.title_style(), size=18),
                turno_card
            ], expand=3)
        ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=20)
    ], scroll=ft.ScrollMode.HIDDEN, expand=True, padding=20)