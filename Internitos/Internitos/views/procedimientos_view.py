import flet as ft
from utils.calculations import ClinicalMath

def view_procedimientos(page: ft.Page):
    
    COLOR_PRIMARY = "#005EB8"
    
    def check_item(text): return ft.Checkbox(label=text, label_style=ft.TextStyle(size=14))
    def step_text(text): return ft.Text(text, size=14)
    def title_section(text, icon): return ft.Row([ft.Icon(icon, color=COLOR_PRIMARY), ft.Text(text, weight="bold", color=COLOR_PRIMARY)])

    # --- CONTENIDOS ---
    def content_paracentesis():
        txt_litros = ft.TextField(label="Litros extraídos", value="5", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        lbl_alb = ft.Container()

        def calc_alb(e):
            try:
                litros = float(txt_litros.value)
                reposicion = ClinicalMath.calc_reposicion_albumina(litros) # Usa lógica centralizada
                if reposicion > 0:
                    lbl_alb.content = ft.Container(content=ft.Text(f"⚠️ Reponer {reposicion}g Albúmina", color="white", weight="bold"), bgcolor="#DC2626", padding=10, border_radius=5)
                else:
                    lbl_alb.content = ft.Text("✅ < 5L: No requiere reposición obligatoria", color="green")
                lbl_alb.update()
            except: pass

        txt_litros.on_change = calc_alb
        calc_alb(None)

        return ft.Row([
            ft.Column([
                title_section("Preparación", ft.icons.SECURITY), check_item("Consentimiento"), check_item("Plaq > 50k / INR < 1.5"), check_item("Ecografía (Sitio)"),
                ft.Divider(), title_section("Insumos", ft.icons.SHOPPING_CART), check_item("Clorhexidina"), check_item("Lidocaína 2%"), check_item("Jelco 14G / Catéter"), check_item("Botellas vacío")
            ], expand=True),
            ft.VerticalDivider(),
            ft.Column([
                title_section("Pasos Críticos", ft.icons.DIRECTIONS_WALK), step_text("1. Aseo amplio y campo estéril."), step_text("2. Anestesia Z (Piel->Peritoneo)."), step_text("3. Punción aspirando."),
                ft.Divider(), title_section("Reposición Albúmina", ft.icons.MEDICAL_SERVICES), txt_litros, lbl_alb
            ], expand=True)
        ], vertical_alignment=ft.CrossAxisAlignment.START)

    def content_cvc():
        return ft.Row([
            ft.Column([title_section("Insumos", ft.icons.SHOPPING_CART), check_item("Set CVC"), check_item("EPP Máximo"), check_item("Ecógrafo estéril")], expand=True),
            ft.VerticalDivider(),
            ft.Column([title_section("Seldinger", ft.icons.DIRECTIONS_WALK), step_text("1. Purgar lúmenes."), step_text("2. Punción -> Guía (Sin resistencia)."), step_text("3. Retirar aguja, mantener guía."), 
                       ft.Container(ft.Text("⚠️ ¡NUNCA SOLTAR LA GUÍA!", color="red", weight="bold"), bgcolor="#FEF2F2", padding=5), step_text("4. Dilatar -> Pasar catéter."), step_text("5. RX TÓRAX CONTROL.")], expand=True)
        ], vertical_alignment=ft.CrossAxisAlignment.START)

    # --- SELECTOR ---
    main_content = ft.Container(content_paracentesis(), padding=10)
    
    def cambiar_proc(e):
        if e.control.value == "Paracentesis": main_content.content = content_paracentesis()
        elif e.control.value == "CVC": main_content.content = content_cvc()
        else: main_content.content = ft.Text("En construcción...", italic=True)
        page.update()

    dd_proc = ft.Dropdown(label="Procedimiento", options=[ft.dropdown.Option("Paracentesis"), ft.dropdown.Option("CVC"), ft.dropdown.Option("Punción Lumbar")], value="Paracentesis", on_change=cambiar_proc)

    # --- GENERADOR NOTA ---
    def generar_nota(e):
        page.set_clipboard(f"PROCEDIMIENTO: {dd_proc.value}\nRealizado por interno. Consentimiento verbal/escrito. Técnica aséptica. Sin complicaciones inmediatas.")
        page.snack_bar = ft.SnackBar(ft.Text("✅ Nota copiada")); page.snack_bar.open = True; page.update()

    return ft.Column([
        ft.Text("Procedimientos", size=24, weight="bold", color=COLOR_PRIMARY),
        ft.Container(dd_proc, bgcolor="#F1F5F9", padding=10, border_radius=8),
        ft.Container(main_content, border=ft.border.all(1, "#E2E8F0"), border_radius=10, expand=True, padding=20),
        ft.ElevatedButton("Copiar Nota Tipo", icon=ft.icons.COPY, on_click=generar_nota),
        ft.Container(height=50)
    ], expand=True, padding=10)