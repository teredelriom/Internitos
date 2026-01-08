import flet as ft

class DesignSystem:
    PRIMARY = "#005EB8"       
    PRIMARY_LIGHT = "#E0F2FE" 
    SECONDARY = "#0EA5E9"     
    ACCENT = "#F59E0B"        
    
    BACKGROUND = "#F8FAFC"    
    SURFACE = "#FFFFFF"       
    TEXT_MAIN = "#1E293B"     
    TEXT_MUTED = "#64748B"    

    SHADOW_SM = ft.BoxShadow(
        blur_radius=5, 
        spread_radius=1, 
        color=ft.Colors.with_opacity(0.05, "black"), 
        offset=ft.Offset(0, 2)
    )
    SHADOW_MD = ft.BoxShadow(
        blur_radius=15, 
        spread_radius=2, 
        color=ft.Colors.with_opacity(0.1, "#005EB8"), 
        offset=ft.Offset(0, 5)
    )

    RADIUS_CARD = 16
    RADIUS_BTN = 8

    @staticmethod
    def title_style():
        return ft.TextStyle(size=26, weight=ft.FontWeight.BOLD, color=DesignSystem.PRIMARY, font_family="Roboto")

    @staticmethod
    def get_light_theme():
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=DesignSystem.PRIMARY,
                background=DesignSystem.BACKGROUND,
                surface=DesignSystem.SURFACE,
                on_background=DesignSystem.TEXT_MAIN,
                on_surface=DesignSystem.TEXT_MAIN,
            ),
            font_family="Roboto"
        )

# --- COMPONENTES UI REUTILIZABLES ---

def GlassCard(content, padding=20, expand=False, on_click=None):
    return ft.Container(
        content=content,
        bgcolor=DesignSystem.SURFACE,
        padding=padding,
        border_radius=DesignSystem.RADIUS_CARD,
        shadow=DesignSystem.SHADOW_SM,
        border=ft.border.all(1, "#F1F5F9"),
        expand=expand,
        on_click=on_click,
        ink=True if on_click else False
    )

def GradientCard(content, padding=20, expand=False, on_click=None):
    """
    Tarjeta con fondo gradiente para destacar elementos.
    CORREGIDO: Uso de ft.Alignment explícito en lugar de constantes obsoletas.
    """
    return ft.Container(
        content=content,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1), # Antes: ft.alignment.top_left
            end=ft.Alignment(1, 1),     # Antes: ft.alignment.bottom_right
            colors=[DesignSystem.PRIMARY, DesignSystem.SECONDARY],
        ),
        padding=padding,
        border_radius=DesignSystem.RADIUS_CARD,
        shadow=DesignSystem.SHADOW_MD,
        expand=expand,
        on_click=on_click,
        ink=True if on_click else False
    )

def SectionHeader(title, icon_name):
    # icon_name debe ser string (ej: "home")
    return ft.Row([
        ft.Container(
            content=ft.Icon(icon_name, color="white", size=20),
            padding=8,
            bgcolor=DesignSystem.PRIMARY,
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.4, DesignSystem.PRIMARY))
        ),
        ft.Text(title, style=DesignSystem.title_style(), size=20)
    ])