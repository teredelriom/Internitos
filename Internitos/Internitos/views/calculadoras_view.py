import flet as ft
from utils.calculations import ClinicalMath

def view_calculadoras(page: ft.Page):
    
    COLOR_PRIMARY = "#005EB8"
    COLOR_BG_CARD = "#FFFFFF"
    COLOR_RESULT_BG = "#F0F9FF"
    
    # --- HELPER: ROBUSTEZ NUMÉRICA ---
    def safe_float(val):
        """Convierte input a float tolerando comas (formato ES) y vacíos."""
        try:
            if isinstance(val, str):
                val = val.replace(",", ".").strip()
            return float(val)
        except:
            return 0.0

    # --- UI HELPERS ---
    def calc_card(titulo, inputs, resultado_control):
        return ft.Container(
            content=ft.Column([
                ft.Text(titulo, weight="bold", size=16, color=COLOR_PRIMARY),
                ft.Divider(height=5, color="transparent"),
                ft.Column(inputs, spacing=10),
                ft.Divider(),
                ft.Container(content=resultado_control, bgcolor=COLOR_RESULT_BG, padding=10, border_radius=5, border=ft.border.all(1, "#BAE6FD"))
            ]),
            bgcolor=COLOR_BG_CARD, padding=20, border_radius=10, border=ft.border.all(1, "#E2E8F0"),
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.GREY_100), margin=ft.margin.only(bottom=10)
        )

    def input_field(label, value, on_change, suffix=None):
        return ft.TextField(
            label=label, value=value, on_change=on_change, keyboard_type=ft.KeyboardType.NUMBER,
            suffix_text=suffix, height=45, text_size=14, content_padding=10, expand=True,
            border_color=ft.Colors.OUTLINE, focused_border_color=COLOR_PRIMARY
        )

    # ==============================================================================
    # 1. RENAL
    # ==============================================================================
    cg_edad = input_field("Edad", "60", None)
    cg_peso = input_field("Peso", "70", None)
    cg_crea = input_field("Crea", "1.0", None)
    cg_sexo = ft.Dropdown(label="Sexo", width=80, height=45, options=[ft.dropdown.Option("M"), ft.dropdown.Option("F")], value="M")
    res_cg = ft.Text("VFG: -", weight="bold", size=16)

    def calc_cockcroft(e):
        edad, peso, crea = safe_float(cg_edad.value), safe_float(cg_peso.value), safe_float(cg_crea.value)
        es_mujer = cg_sexo.value == "F"
        vfg = ClinicalMath.calc_cockcroft(int(edad), peso, crea, es_mujer)
        
        res_cg.value = f"VFG: {vfg:.1f} ml/min"
        res_cg.color = "red" if vfg < 60 else "green"
        page.update()

    for c in [cg_edad, cg_peso, cg_crea, cg_sexo]: c.on_change = calc_cockcroft

    # FeNa
    fena_nau = input_field("Na U", "", None)
    fena_cru = input_field("Cr U", "", None)
    fena_nap = input_field("Na P", "", None)
    fena_crp = input_field("Cr P", "", None)
    res_fena = ft.Text("FeNa: -", weight="bold")

    def calc_fena(e):
        nau, cru = safe_float(fena_nau.value), safe_float(fena_cru.value)
        nap, crp = safe_float(fena_nap.value), safe_float(fena_crp.value)
        
        fena = ClinicalMath.calc_fena(nau, crp, nap, cru)
        res_fena.value = f"FeNa: {fena:.2f}%"
        res_fena.color = "#005EB8" if fena < 1 else ("orange" if fena < 2 else "red")
        page.update()

    for c in [fena_nau, fena_cru, fena_nap, fena_crp]: c.on_change = calc_fena

    # ==============================================================================
    # 2. CARDIO
    # ==============================================================================
    pam_sis = input_field("PAS", "", None)
    pam_dias = input_field("PAD", "", None)
    res_pam = ft.Text("PAM: -", size=18, weight="bold")

    def calc_pam(e):
        pam = ClinicalMath.calc_pam(safe_float(pam_sis.value), safe_float(pam_dias.value))
        res_pam.value = f"PAM: {pam:.1f} mmHg" if pam > 0 else "PAM: -"
        page.update()

    pam_sis.on_change = calc_pam; pam_dias.on_change = calc_pam

    qt_qt = input_field("QT (ms)", "", None)
    qt_fc = input_field("FC (lpm)", "", None)
    res_qt = ft.Text("QTc: -", size=16, weight="bold")

    def calc_qt(e):
        qtc = ClinicalMath.calc_qtc_bazett(safe_float(qt_qt.value), safe_float(qt_fc.value))
        res_qt.value = f"QTc: {qtc:.0f} ms"
        res_qt.color = "red" if qtc > 450 else "green"
        page.update()

    qt_qt.on_change = calc_qt; qt_fc.on_change = calc_qt

    # ==============================================================================
    # 3. RESPIRATORIO
    # ==============================================================================
    pafi_pa = input_field("PaO2", "", None)
    pafi_fio = input_field("FiO2 %", "", None)
    res_pafi = ft.Text("PAFI: -", size=16, weight="bold")

    def calc_pafi(e):
        pafi = ClinicalMath.calc_pafi(safe_float(pafi_pa.value), safe_float(pafi_fio.value))
        res_pafi.value = f"PAFI: {pafi:.0f}"
        res_pafi.color = "red" if pafi < 150 else ("orange" if pafi < 300 else "green")
        page.update()

    pafi_pa.on_change = calc_pafi; pafi_fio.on_change = calc_pafi

    vt_talla = input_field("Talla (cm)", "170", None)
    vt_sexo = ft.Dropdown(label="Sexo", width=80, height=45, options=[ft.dropdown.Option("H"), ft.dropdown.Option("M")], value="H")
    res_vt = ft.Text("VT: -", size=14)

    def calc_vt(e):
        talla = safe_float(vt_talla.value)
        if talla > 100:
            pi = 50 + 0.91 * (talla - 152.4) if vt_sexo.value == "H" else 45.5 + 0.91 * (talla - 152.4)
            res_vt.value = f"Peso Ideal: {pi:.1f}kg\nVT Meta (6-8ml): {int(pi*6)}-{int(pi*8)} ml"
        page.update()

    vt_talla.on_change = calc_vt; vt_sexo.on_change = calc_vt

    # ==============================================================================
    # 4. INFUSIONES
    # ==============================================================================
    inf_drogas = ft.Dropdown(
        label="Droga", 
        options=[ft.dropdown.Option("Nora"), ft.dropdown.Option("Dobu"), ft.dropdown.Option("Fenta"), ft.dropdown.Option("Manual")],
        value="Nora", expand=True, height=45
    )
    inf_peso = input_field("Peso", "70", None)
    inf_dosis = input_field("Dosis", "0.05", None)
    inf_mg = input_field("Mg", "4", None)
    inf_vol = input_field("Vol", "250", None)
    res_bomba = ft.Text("Bomba: - ml/hr", size=20, weight="bold", color=COLOR_PRIMARY)

    def calc_bomba(e):
        mg, vol = safe_float(inf_mg.value), safe_float(inf_vol.value)
        
        # Presets automáticos
        if inf_drogas.value == "Nora" and e.control == inf_drogas: mg, vol = 4, 250
        elif inf_drogas.value == "Dobu" and e.control == inf_drogas: mg, vol = 250, 250
        
        if e.control == inf_drogas:
            inf_mg.value, inf_vol.value = str(mg), str(vol)
            inf_mg.update(); inf_vol.update()

        conc = (mg * 1000) / vol if vol > 0 else 0
        ml_hr = ClinicalMath.calc_velocidad_bomba(safe_float(inf_dosis.value), safe_float(inf_peso.value), conc)
        res_bomba.value = f"Bomba: {ml_hr:.1f} ml/hr"
        res_bomba.update()

    inf_drogas.on_change = calc_bomba
    for c in [inf_peso, inf_dosis, inf_mg, inf_vol]: c.on_change = calc_bomba

    # --- LAYOUT ---
    return ft.Column([
        ft.Text("Calculadoras Clínicas", size=24, weight="bold", color=COLOR_PRIMARY),
        ft.Tabs(tabs=[
            ft.Tab(text="Renal", content=ft.Column([calc_card("Cockcroft-Gault", [ft.Row([cg_edad, cg_peso]), ft.Row([cg_crea, cg_sexo])], res_cg), calc_card("FeNa", [ft.Row([fena_nau, fena_cru]), ft.Row([fena_nap, fena_crp])], res_fena)], scroll=ft.ScrollMode.AUTO)),
            ft.Tab(text="Cardio", content=ft.Column([calc_card("PAM", [ft.Row([pam_sis, pam_dias])], res_pam), calc_card("QT Bazett", [ft.Row([qt_qt, qt_fc])], res_qt)], scroll=ft.ScrollMode.AUTO)),
            ft.Tab(text="Resp", content=ft.Column([calc_card("PAFI", [ft.Row([pafi_pa, pafi_fio])], res_pafi), calc_card("Vol. Tidal", [ft.Row([vt_talla, vt_sexo])], res_vt)], scroll=ft.ScrollMode.AUTO)),
            ft.Tab(text="UCI", content=ft.Column([calc_card("Infusiones", [inf_drogas, ft.Row([inf_peso, inf_dosis]), ft.ExpansionTile(title=ft.Text("Dilución"), controls=[ft.Row([inf_mg, inf_vol])])], res_bomba)], scroll=ft.ScrollMode.AUTO)),
        ], expand=True)
    ], expand=True)