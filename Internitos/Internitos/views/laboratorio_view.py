import flet as ft
import json
import os
from utils.persistence import init_database
from utils.calculations import ClinicalMath

# --- RUTA DB ---
FILE_PATH = init_database("db_examenes.json")

def cargar_datos_lab():
    if not os.path.exists(FILE_PATH): 
        return []
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f: 
            return json.load(f)
    except: 
        return []

def view_laboratorio(page: ft.Page):
    
    COLOR_PRIMARY = "#005EB8"
    COLOR_CARD_BG = "#FFFFFF"
    COLOR_WARNING = "#F59E0B"
    COLOR_DANGER = "#DC2626"
    COLOR_SUCCESS = "#10B981"

    hallazgos_resumen = set()

    # --- HELPER ROBUSTEZ ---
    def safe_float(val):
        """Convierte input a float tolerando comas y valores no numéricos."""
        try:
            if isinstance(val, str) or isinstance(val, ft.Control):
                # Si viene del control directo, extraemos el value
                v = val.value if hasattr(val, 'value') else str(val)
                v = v.replace(",", ".").strip()
                return float(v)
            return float(val)
        except:
            return 0.0

    # --- HELPERS UI ---
    def lab_card(title, content_list, border_color=COLOR_PRIMARY):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, weight=ft.FontWeight.BOLD, color=border_color, size=16),
                ft.Divider(height=5, color="transparent"),
                *content_list
            ]),
            bgcolor=COLOR_CARD_BG,
            padding=15,
            border_radius=10,
            border=ft.border.all(1, "#E2E8F0"),
            border_left=ft.border.BorderSide(5, border_color),
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.GREY_100),
            expand=True
        )

    def input_num(label, value, on_change_fn=None):
        return ft.TextField(
            label=label, 
            value=str(value), 
            text_size=14, 
            height=45, 
            content_padding=10, 
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=on_change_fn,
            expand=True
        )
    
    def alert_box(text, color):
        return ft.Container(
            content=ft.Text(text, color="white", size=12, weight="bold"),
            bgcolor=color, padding=5, border_radius=4, margin=ft.margin.only(top=5)
        )

    # --- CONTROLES ---
    # Renal
    in_crea = input_num("Crea", "0.9")
    in_bun = input_num("BUN", "15.0")
    in_crea_prev = input_num("Crea Previa", "0.0")
    lbl_renal = ft.Column()

    # ELP
    in_na = input_num("Na+", "140")
    in_k = input_num("K+", "4.0")
    in_cl = input_num("Cl-", "100")
    in_hco3 = input_num("HCO3", "24")
    lbl_gap = ft.Text("Gap: -", size=13, weight="bold")
    lbl_elp_alert = ft.Column()

    # Hepático
    in_got = input_num("GOT", "25")
    in_gpt = input_num("GPT", "25")
    in_fa = input_num("FA", "80")
    in_ggt = input_num("GGT", "30")
    in_bili = input_num("Bili T", "0.8")
    lbl_hepatic = ft.Text("Patrón: Normal", color="grey", size=13)

    # Hemo
    in_hb = input_num("Hb", "12.0")
    in_vcm = input_num("VCM", "88.0")
    in_gr = input_num("GR", "4.5")
    in_leucos = input_num("Leucos", "7500")
    in_neu_perc = input_num("% Neu", "60")
    in_plaq = input_num("Plaquetas", "250000")
    lbl_hemo_alert = ft.Column()
    lbl_ran = ft.Text("RAN: -", weight="bold")

    # Gases/FIB-4
    in_ph = input_num("pH", "7.35")
    in_pco2 = input_num("pCO2", "40.0")
    in_lac = input_num("Lactato", "1.0")
    in_ca = input_num("Calcio", "9.0")
    in_alb = input_num("Albúmina", "4.0")
    in_age_fib = input_num("Edad (FIB-4)", "50")
    lbl_gas_alert = ft.Column()
    lbl_ca_corr = ft.Text("-", size=12)
    lbl_fib4 = ft.Text("FIB-4: -", weight="bold", size=14)

    # --- LÓGICA ---
    def calc_renal(e):
        lbl_renal.controls.clear()
        crea = safe_float(in_crea)
        bun = safe_float(in_bun)
        crea_prev = safe_float(in_crea_prev)

        ratio = ClinicalMath.calc_ratio_bun_crea(bun, crea)
        if crea > 1.3:
            lbl_renal.controls.append(ft.Text(f"Ratio: {ratio:.1f}", size=12, color="blue"))

        # AKI Check
        if crea_prev > 0:
            delta = crea - crea_prev
            elevacion = crea / crea_prev if crea_prev > 0 else 0
            if delta >= 0.3 or elevacion >= 1.5:
                lbl_renal.controls.append(alert_box(f"🚨 AKI KDIGO (+{delta:.1f})", COLOR_DANGER))
                hallazgos_resumen.add(f"Injuria Renal Aguda (Crea {crea})")
            else:
                hallazgos_resumen.discard(f"Injuria Renal Aguda (Crea {crea})")
        page.update()

    def calc_elp(e):
        lbl_elp_alert.controls.clear()
        na = safe_float(in_na)
        k = safe_float(in_k)
        cl = safe_float(in_cl)
        hco3 = safe_float(in_hco3)

        gap = ClinicalMath.calc_anion_gap(na, cl, hco3)
        lbl_gap.value = f"Anion Gap: {gap:.1f}"
        
        if gap > 12:
            lbl_elp_alert.controls.append(alert_box(f"Acidosis Gap Aumentado ({gap:.1f})", COLOR_DANGER))
            hallazgos_resumen.add(f"Acidosis Metabólica Gap {gap:.1f}")
        
        if k > 5.5:
            lbl_elp_alert.controls.append(alert_box(f"Hiperkalemia ({k})", COLOR_DANGER))
            hallazgos_resumen.add(f"Hiperkalemia {k}")
        elif k < 3.5:
            lbl_elp_alert.controls.append(alert_box(f"Hipokalemia ({k})", COLOR_WARNING))
            hallazgos_resumen.add(f"Hipokalemia {k}")
        page.update()

    def calc_hepatic(e):
        got, gpt = safe_float(in_got), safe_float(in_gpt)
        fa, ggt = safe_float(in_fa), safe_float(in_ggt)
        
        patron = "Normal"
        color = "grey"
        if (got > 40 or gpt > 40) and fa < 130: 
            patron, color = "Hepatocelular", COLOR_WARNING
        elif (fa > 130 or ggt > 50) and got < 50: 
            patron, color = "Colestásico", COLOR_WARNING
        elif (got > 40 or gpt > 40) and (fa > 130): 
            patron, color = "Mixto", COLOR_DANGER
            
        lbl_hepatic.value = f"Patrón: {patron}"
        lbl_hepatic.color = color
        if patron != "Normal": hallazgos_resumen.add(f"Perfil Hepático {patron}")
        page.update()
        calc_fib4(None)

    def calc_hemo(e):
        lbl_hemo_alert.controls.clear()
        hb = safe_float(in_hb)
        vcm = safe_float(in_vcm)
        gr = safe_float(in_gr)
        leuc = safe_float(in_leucos)
        neu = safe_float(in_neu_perc)
        plaq = safe_float(in_plaq)

        if 0 < hb < 12:
            tipo = "Microcítica" if vcm < 80 else ("Macrocítica" if vcm > 100 else "Normocítica")
            lbl_hemo_alert.controls.append(alert_box(f"Anemia {tipo}", COLOR_WARNING))
            hallazgos_resumen.add(f"Anemia {tipo} (Hb {hb})")
            if tipo == "Microcítica" and gr > 0:
                mentzer = ClinicalMath.calc_mentzer(vcm, gr)
                lbl_hemo_alert.controls.append(ft.Text(f"Mentzer: {mentzer:.1f}", size=11, italic=True))

        ran = ClinicalMath.calc_ran(leuc, neu)
        lbl_ran.value = f"RAN: {int(ran)}"
        if ran < 1500:
            lbl_hemo_alert.controls.append(alert_box("Neutropenia", COLOR_DANGER))
            hallazgos_resumen.add(f"Neutropenia ({int(ran)})")

        if plaq < 150000:
            lbl_hemo_alert.controls.append(alert_box("Trombocitopenia", COLOR_WARNING))
            hallazgos_resumen.add(f"Trombocitopenia ({int(plaq)})")
        page.update()
        calc_fib4(None)

    def calc_gases(e):
        lbl_gas_alert.controls.clear()
        lac = safe_float(in_lac)
        ca = safe_float(in_ca)
        alb = safe_float(in_alb)

        if lac > 2:
            lbl_gas_alert.controls.append(alert_box(f"Hiperlactatemia ({lac})", COLOR_DANGER))
            hallazgos_resumen.add(f"Hiperlactatemia {lac}")

        ca_corr = ClinicalMath.calc_calcio_corregido(ca, alb)
        if alb < 4.0:
            lbl_ca_corr.value = f"Ca Corr: {ca_corr:.2f}"
            lbl_ca_corr.color = COLOR_PRIMARY
        else:
            lbl_ca_corr.value = ""
        page.update()

    def calc_fib4(e):
        age = safe_float(in_age_fib)
        ast = safe_float(in_got)
        alt = safe_float(in_gpt)
        plaq = safe_float(in_plaq)

        if alt > 0 and plaq > 0:
            score = ClinicalMath.calc_fib4(int(age), ast, alt, plaq)
            lbl_fib4.value = f"FIB-4: {score:.2f}"
            if score < 1.45: lbl_fib4.color = COLOR_SUCCESS
            elif score > 3.25: lbl_fib4.color = COLOR_DANGER
            else: lbl_fib4.color = COLOR_WARNING
        else:
            lbl_fib4.value = "FIB-4: -"
        page.update()

    # Bindings
    for c in [in_crea, in_bun, in_crea_prev]: c.on_change = calc_renal
    for c in [in_na, in_k, in_cl, in_hco3]: c.on_change = calc_elp
    for c in [in_got, in_gpt, in_fa, in_ggt, in_bili]: c.on_change = calc_hepatic
    for c in [in_hb, in_vcm, in_gr, in_leucos, in_neu_perc, in_plaq]: c.on_change = calc_hemo
    for c in [in_lac, in_ca, in_alb]: c.on_change = calc_gases
    in_age_fib.on_change = calc_fib4

    # --- TABLA BUSCADOR ---
    db_data = cargar_datos_lab()
    
    def crear_filas(filtro=""):
        rows = []
        for item in db_data:
            t = str(item.get("Examen", "")).lower() + str(item.get("Significado", "")).lower()
            if filtro.lower() in t:
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(item.get("Examen", "")), size=12, weight="bold")),
                    ft.DataCell(ft.Text(str(item.get("Rango", "")), size=12)),
                    ft.DataCell(ft.Text(str(item.get("Significado", "")), size=11, italic=True)),
                ]))
        return rows

    lab_table = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("Examen")), ft.DataColumn(ft.Text("Rango")), ft.DataColumn(ft.Text("Interpretación"))
    ], rows=crear_filas(), heading_row_color="#F1F5F9", data_row_min_height=40)

    # --- RESUMEN ---
    def copiar_resumen(e):
        txt = "LABORATORIO:\n" + ("\n".join([f"- {h}." for h in hallazgos_resumen]) if hallazgos_resumen else "- Sin alteraciones críticas.")
        txt += f"\n(Crea: {in_crea.value} | Na: {in_na.value} | K: {in_k.value} | GOT/GPT: {in_got.value}/{in_gpt.value})"
        page.set_clipboard(txt)
        page.snack_bar = ft.SnackBar(ft.Text("✅ Resumen copiado")); page.snack_bar.open = True; page.update()

    # --- LAYOUT ---
    return ft.Column([
        ft.Text("Panel de Laboratorio 🧪", size=24, weight="bold", color=COLOR_PRIMARY),
        ft.Divider(),
        ft.Row([
            lab_card("Función Renal", [ft.Row([in_crea, in_bun]), in_crea_prev, lbl_renal], "#3B82F6"),
            lab_card("Electrolitos", [ft.Row([in_na, in_k]), ft.Row([in_cl, in_hco3]), lbl_gap, lbl_elp_alert], "#F59E0B")
        ]),
        ft.Container(height=10),
        lab_card("Perfil Hepático", [ft.Row([in_got, in_gpt, in_fa, in_ggt, in_bili], spacing=5), lbl_hepatic], "#10B981"),
        ft.Container(height=10),
        ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Hemograma", content=ft.Container(padding=15, content=ft.Column([
                ft.Row([in_hb, in_vcm, in_gr]), ft.Row([in_leucos, in_neu_perc, lbl_ran]), ft.Row([in_plaq]), lbl_hemo_alert
            ]))),
            ft.Tab(text="Gases/Otros", content=ft.Container(padding=15, content=ft.Column([
                ft.Row([in_ph, in_pco2, in_lac]), lbl_gas_alert, ft.Divider(),
                ft.Row([in_ca, in_alb, lbl_ca_corr]), ft.Divider(),
                ft.Row([in_age_fib, lbl_fib4])
            ]))),
            ft.Tab(text="🔍 Buscador", content=ft.Container(padding=15, content=ft.Column([
                ft.TextField(prefix_icon=ft.icons.SEARCH, hint_text="Buscar...", on_change=lambda e: (setattr(lab_table, 'rows', crear_filas(e.control.value)) or page.update())),
                ft.Container(content=ft.Column([lab_table], scroll=ft.ScrollMode.AUTO), height=300, border=ft.border.all(1, "#E2E8F0"))
            ])))
        ], expand=True),
        ft.Divider(),
        ft.ElevatedButton("📋 Copiar Resumen", icon=ft.icons.COPY_ALL, bgcolor=COLOR_PRIMARY, color="white", on_click=copiar_resumen),
        ft.Container(height=50)
    ], scroll=ft.ScrollMode.ALWAYS, expand=True, padding=10)