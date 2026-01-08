import flet as ft
from datetime import datetime
import re
import json
import os
# Importamos solo init_database, os ya está importado arriba
from utils.persistence import init_database

# --- RUTA DE LA BASE DE DATOS ---
# Esto asegura que FILE_PLANTILLAS apunte a AppData/Roaming/InternitosPro/plantillas_ficha.json
FILE_PLANTILLAS = init_database("plantillas_ficha.json")

PLANTILLAS_DEFAULT = {
    "Vacio": {"motivo": "", "plan": ""},
    "Insuficiencia Cardíaca": {
        "motivo": "Disnea de esfuerzos progresiva, ortopnea y DPN. Aumento de volumen en EEII.",
        "plan": "1. Furosemida __ mg EV\n2. Restricción hidrosalina\n3. Control peso diario\n4. Balance hídrico estricto"
    },
    "NAC (Neumonía)": {
        "motivo": "Fiebre cuantificada, tos con expectoración purulenta y puntada de costado.",
        "plan": "1. Antibiótico: Ceftriaxona 2g/día\n2. O2 para sat > 92%\n3. Kinesioterapia respiratoria"
    }
}

def cargar_plantillas_db():
    # CORRECCIÓN: Usar os.path.exists en lugar de init_database.exists
    if not os.path.exists(FILE_PLANTILLAS):
        return PLANTILLAS_DEFAULT.copy()
    try:
        with open(FILE_PLANTILLAS, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data: return PLANTILLAS_DEFAULT.copy()
            return data
    except:
        return PLANTILLAS_DEFAULT.copy()

def guardar_plantillas_db(data):
    # CORRECCIÓN: No crear carpetas locales 'data'. 
    # Escribir directamente en la ruta provista por persistence.py
    try:
        with open(FILE_PLANTILLAS, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando plantilla: {e}")

# --- VISTA PRINCIPAL ---
def view_ficha(page: ft.Page):
    
    plantillas_actuales = cargar_plantillas_db()

    # --- ESTILOS ---
    COLOR_PRIMARY = "#005EB8"
    
    def input_style(label, multiline=False, height=None, expand=False, value=""):
        return ft.TextField(
            label=label,
            multiline=multiline,
            min_lines=3 if multiline and not height else 1,
            height=height,
            text_size=14,
            border_radius=8,
            filled=True,
            bgcolor="#F8F9FA",
            expand=expand,
            value=value
        )

    # --- CONTROLES ---
    txt_iniciales = ft.TextField(label="Iniciales", width=100)
    txt_edad = ft.TextField(label="Edad", width=80, keyboard_type=ft.KeyboardType.NUMBER)
    dd_sexo = ft.Dropdown(label="Sexo", width=100, options=[ft.dropdown.Option("M"), ft.dropdown.Option("F")])
    dd_servicio = ft.Dropdown(label="Servicio", width=150, options=[
        ft.dropdown.Option("Medicina"), ft.dropdown.Option("UTI"), ft.dropdown.Option("Urgencia")
    ], value="Medicina")
    txt_fecha = ft.TextField(label="Fecha", value=datetime.now().strftime("%d/%m/%Y"), width=120)

    dd_plantilla = ft.Dropdown(
        label="📋 Cargar Plantilla",
        options=[ft.dropdown.Option(k) for k in plantillas_actuales.keys()],
        expand=True
    )
    
    txt_motivo = input_style("Motivo de Ingreso", multiline=True, height=80)
    txt_historia = input_style("Historia Actual", multiline=True, height=150)
    txt_morbidos = input_style("Mórbidos / Qx", multiline=True, height=100)
    txt_farmacos = input_style("Fármacos / Alergias", multiline=True, height=100)
    txt_sv = ft.TextField(label="Signos Vitales (PA: 120/80...)", expand=True)
    lbl_pam = ft.Text("PAM: -", size=12, color=ft.Colors.GREY, weight="bold")
    txt_ef = input_style("Examen Segmentario", multiline=True, height=150)
    txt_diagnostico = input_style("Hipótesis Diagnóstica", multiline=True, height=120)
    txt_problemas = input_style("Problemas Activos", multiline=True, height=120)
    txt_plan = input_style("Indicaciones / Plan", multiline=True, height=150)
    txt_alarma = input_style("⚠️ Criterios de Alarma", value="")
    txt_evolucion = input_style("Evolución", multiline=True, height=100)

    # --- MODAL CREAR ---
    new_titulo = ft.TextField(label="Nombre Plantilla")
    new_motivo = ft.TextField(label="Motivo Sugerido", multiline=True)
    new_plan = ft.TextField(label="Plan Sugerido", multiline=True)
    
    dlg_crear = ft.AlertDialog(
        title=ft.Text("Nueva Plantilla"),
        content=ft.Column([new_titulo, new_motivo, new_plan], height=300, scroll=ft.ScrollMode.AUTO),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: setattr(dlg_crear, 'open', False) or page.update()),
            ft.ElevatedButton("Guardar", on_click=lambda e: guardar_nueva_plantilla(e))
        ]
    )

    def guardar_nueva_plantilla(e):
        if not new_titulo.value: return
        plantillas_actuales[new_titulo.value] = {"motivo": new_motivo.value, "plan": new_plan.value}
        guardar_plantillas_db(plantillas_actuales)
        dd_plantilla.options = [ft.dropdown.Option(k) for k in plantillas_actuales.keys()]
        dd_plantilla.value = new_titulo.value
        txt_motivo.value = new_motivo.value
        txt_plan.value = new_plan.value
        dlg_crear.open = False
        page.update()

    def cambiar_plantilla(e):
        if dd_plantilla.value in plantillas_actuales:
            data = plantillas_actuales[dd_plantilla.value]
            txt_motivo.value = data.get("motivo", "")
            txt_plan.value = data.get("plan", "")
            page.update()

    dd_plantilla.on_change = cambiar_plantilla

    # Lógica PAM
    def calcular_pam(e):
        match = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', txt_sv.value)
        if match:
            sis, dias = int(match.group(1)), int(match.group(2))
            lbl_pam.value = f"PAM: {int((sis + 2*dias)/3)}"
        page.update()
    txt_sv.on_change = calcular_pam

    # Generar Texto
    def generar_ficha(e):
        txt = f"*** FICHA {txt_fecha.value} ***\nPACIENTE: {txt_iniciales.value}\n\nMOTIVO: {txt_motivo.value}\n\nHISTORIA: {txt_historia.value}\n\nDG: {txt_diagnostico.value}\n\nPLAN:\n{txt_plan.value}"
        page.set_clipboard(txt)
        page.snack_bar = ft.SnackBar(ft.Text("Copiado!"))
        page.snack_bar.open = True
        page.update()

    # Layout simplificado
    return ft.Column([
        ft.Text("Ficha Clínica", size=24, weight="bold", color=COLOR_PRIMARY),
        ft.Row([dd_plantilla, ft.IconButton(ft.icons.ADD, on_click=lambda e: page.open(dlg_crear))]),
        ft.Container(content=ft.Column([
            ft.Text("Identificación", weight="bold"),
            ft.Row([txt_iniciales, txt_edad, dd_sexo, txt_fecha]),
            txt_motivo, txt_historia,
            ft.Row([txt_sv, lbl_pam]),
            txt_ef,
            txt_diagnostico, txt_plan,
            ft.ElevatedButton("Copiar Ficha", on_click=generar_ficha, bgcolor=COLOR_PRIMARY, color="white")
        ]), padding=10, scroll=ft.ScrollMode.AUTO, expand=True)
    ], expand=True)