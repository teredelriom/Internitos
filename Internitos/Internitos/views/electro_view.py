import flet as ft
from utils.calculations import ClinicalMath

def view_electro(page: ft.Page):
    
    COLOR_PRIMARY = "#005EB8"
    COLOR_DANGER = "#DC2626"
    COLOR_SUCCESS = "#16A34A"
    COLOR_WARNING = "#F59E0B"
    
    # 1. FRECUENCIA
    txt_cuadros = ft.TextField(label="N° Cuadros Grandes", width=200, keyboard_type=ft.KeyboardType.NUMBER)
    lbl_res_fc = ft.Text("FC: -", size=20, weight="bold", color=COLOR_PRIMARY)

    def calc_fc(e):
        try:
            n = float(txt_cuadros.value)
            if n > 0:
                fc = 300 / n
                lbl_res_fc.value = f"FC: {int(fc)} lpm"
                lbl_res_fc.color = COLOR_SUCCESS if 60 <= fc <= 100 else COLOR_DANGER
            page.update()
        except: pass
    txt_cuadros.on_change = calc_fc

    # 2. EJE
    dd_d1 = ft.Dropdown(label="D1", width=100, options=[ft.dropdown.Option("Pos (+)", text="+"), ft.dropdown.Option("Neg (-)", text="-")], value="Pos (+)")
    dd_avf = ft.Dropdown(label="aVF", width=100, options=[ft.dropdown.Option("Pos (+)", text="+"), ft.dropdown.Option("Neg (-)", text="-")], value="Pos (+)")
    lbl_eje = ft.Text("Eje Normal", size=16, weight="bold", color=COLOR_SUCCESS)

    def calc_eje(e):
        # Mapeamos valores simples para usar la clase utilitaria
        val_d1 = 1 if dd_d1.value == "Pos (+)" else -1
        val_avf = 1 if dd_avf.value == "Pos (+)" else -1
        
        # ClinicalMath usa valores continuos, pero podemos inferir cuadrante
        # D1+, aVF+ -> Normal (0 a 90)
        # D1+, aVF- -> Izquierda (0 a -90)
        # D1-, aVF+ -> Derecha (90 a 180)
        # D1-, aVF- -> Extremo (-90 a -180)
        
        if val_d1 > 0 and val_avf > 0:
            lbl_eje.value, lbl_eje.color = "✅ Normal (0° a 90°)", COLOR_SUCCESS
        elif val_d1 > 0 and val_avf < 0:
            lbl_eje.value, lbl_eje.color = "⬅️ Izquierda (Posible HVI)", COLOR_WARNING
        elif val_d1 < 0 and val_avf > 0:
            lbl_eje.value, lbl_eje.color = "➡️ Derecha (Posible HVD)", COLOR_WARNING
        else:
            lbl_eje.value, lbl_eje.color = "⚠️ Extremo (Tierra de nadie)", COLOR_DANGER
        page.update()

    dd_d1.on_change = calc_eje
    dd_avf.on_change = calc_eje

    # 3. QT BAZETT
    txt_qt = ft.TextField(label="QT (ms)", width=120, value="400")
    txt_fc = ft.TextField(label="FC (lpm)", width=120, value="70")
    lbl_qtc = ft.Text("QTc: 432 ms", weight="bold", size=16)

    def calc_qt(e):
        try:
            qt, fc = float(txt_qt.value), float(txt_fc.value)
            qtc = ClinicalMath.calc_qtc_bazett(qt, fc)
            lbl_qtc.value = f"QTc: {int(qtc)} ms"
            
            if qtc > 480: lbl_qtc.color, lbl_qtc.value = COLOR_DANGER, lbl_qtc.value + " (Peligroso)"
            elif qtc > 450: lbl_qtc.color, lbl_qtc.value = COLOR_WARNING, lbl_qtc.value + " (Largo)"
            else: lbl_qtc.color = COLOR_SUCCESS
            page.update()
        except: pass

    txt_qt.on_change = calc_qt
    txt_fc.on_change = calc_qt

    # --- UI HELPERS ---
    def card(title, content):
        return ft.Container(content=ft.Column([ft.Text(title, weight="bold", color=COLOR_PRIMARY), ft.Divider(), content]),
                            bgcolor="white", padding=15, border_radius=10, border=ft.border.all(1, "#E2E8F0"))

    # TABLAS DE REFERENCIA
    tabla_paredes = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Pared")), ft.DataColumn(ft.Text("Derivaciones")), ft.DataColumn(ft.Text("Arteria"))],
        rows=[
            ft.DataRow([ft.DataCell(ft.Text("Septal")), ft.DataCell(ft.Text("V1-V2")), ft.DataCell(ft.Text("DA"))]),
            ft.DataRow([ft.DataCell(ft.Text("Anterior")), ft.DataCell(ft.Text("V3-V4")), ft.DataCell(ft.Text("DA"))]),
            ft.DataRow([ft.DataCell(ft.Text("Lateral")), ft.DataCell(ft.Text("I, aVL, V5-6")), ft.DataCell(ft.Text("Cx / DA"))]),
            ft.DataRow([ft.DataCell(ft.Text("Inferior")), ft.DataCell(ft.Text("II, III, aVF")), ft.DataCell(ft.Text("CD"))]),
        ]
    )

    # --- LAYOUT ---
    tab_tools = ft.Column([
        card("Frecuencia Cardíaca", ft.Row([txt_cuadros, lbl_res_fc], vertical_alignment="center")),
        card("Eje Eléctrico", ft.Column([ft.Row([dd_d1, dd_avf]), lbl_eje])),
        card("QT Corregido", ft.Row([txt_qt, txt_fc, lbl_qtc], vertical_alignment="center")),
    ], scroll=ft.ScrollMode.AUTO)

    tab_ref = ft.Column([
        ft.ExpansionTile(title=ft.Text("Infarto (Paredes)"), controls=[tabla_paredes]),
        ft.ExpansionTile(title=ft.Text("Bloqueos de Rama"), controls=[
            ft.Container(padding=10, content=ft.Column([
                ft.Text("BRD (Derecha): QRS > 120ms + V1 (rSR')"),
                ft.Text("BRI (Izquierda): QRS > 120ms + V1 (QS) + V6 (R mellada)"),
                ft.Text("⚠️ BRI nuevo = IAM hasta demostrar lo contrario", color="red")
            ]))
        ])
    ], scroll=ft.ScrollMode.AUTO)

    return ft.Column([
        ft.Text("Electrocardiograma ⚡", size=24, weight="bold", color=COLOR_PRIMARY),
        ft.Tabs(tabs=[
            ft.Tab(text="Cálculos", icon=ft.icons.CALCULATE, content=ft.Container(tab_tools, padding=10)),
            ft.Tab(text="Referencias", icon=ft.icons.MENU_BOOK, content=ft.Container(tab_ref, padding=10))
        ], expand=True)
    ], expand=True, padding=10)