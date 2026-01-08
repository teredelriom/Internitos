import math

class ClinicalMath:
    
    # --- RENAL ---
    @staticmethod
    def calc_fena(na_u: float, cr_s: float, na_s: float, cr_u: float) -> float:
        if na_s <= 0 or cr_u <= 0: return 0.0
        return (na_u * cr_s) / (na_s * cr_u) * 100

    @staticmethod
    def calc_cockcroft(edad: int, peso: float, crea: float, es_mujer: bool) -> float:
        if crea <= 0: return 0.0
        constante = 0.85 if es_mujer else 1.0
        return ((140 - edad) * peso) / (72 * crea) * constante
    
    @staticmethod
    def calc_ratio_bun_crea(bun: float, crea: float) -> float:
        """Calcula relación BUN/Creatinina (Útil para AKI prerrenal)."""
        if crea <= 0: return 0.0
        return bun / crea

    # --- MEDIO INTERNO ---
    @staticmethod
    def calc_adrogue(peso: float, na_actual: float, na_infusion: float, es_mujer: bool = False) -> float:
        agua_corporal = 0.5 if es_mujer else 0.6
        act = peso * agua_corporal
        if act == -1: return 0.0 
        return (na_infusion - na_actual) / (act + 1)
    
    @staticmethod
    def calc_anion_gap(na: float, cl: float, hco3: float) -> float:
        """Anion Gap = Na - (Cl + HCO3). Normal: 8-12."""
        return na - (cl + hco3)
    
    @staticmethod
    def calc_calcio_corregido(ca: float, alb: float) -> float:
        """Corrige calcio si albúmina < 4.0."""
        if alb >= 4.0: return ca
        return ca + 0.8 * (4.0 - alb)

    # --- CARDIO ---
    @staticmethod
    def calc_qtc_bazett(qt_medido: float, fc: float) -> float:
        if fc <= 0: return 0.0
        return qt_medido / math.sqrt(60 / fc)

    @staticmethod
    def calc_pam(sistolica: float, diastolica: float) -> float:
        return (sistolica + 2 * diastolica) / 3

    # --- RESPIRATORIO ---
    @staticmethod
    def calc_pafi(pao2: float, fio2_porcentaje: float) -> float:
        if fio2_porcentaje <= 0: return 0.0
        return pao2 / (fio2_porcentaje / 100)

    # --- HEMATOLOGÍA / HEPÁTICO ---
    @staticmethod
    def calc_fib4(edad: int, ast: float, alt: float, plaquetas_conteo_absoluto: float) -> float:
        """Score FIB-4 para fibrosis hepática."""
        if alt <= 0 or plaquetas_conteo_absoluto <= 0: return 0.0
        
        # Corrección de unidades: si usuario pone 150000 -> 150
        plaq_val = plaquetas_conteo_absoluto
        if plaq_val > 1000: 
            plaq_val = plaq_val / 1000
            
        return (edad * ast) / (plaq_val * math.sqrt(alt))

    @staticmethod
    def calc_mentzer(vcm: float, gr: float) -> float:
        """Índice de Mentzer = VCM / GR (<13 Talasemia, >13 Ferropenia)."""
        if gr <= 0: return 0.0
        return vcm / gr

    @staticmethod
    def calc_ran(leucos: float, neu_perc: float) -> float:
        """Recuento Absoluto de Neutrófilos."""
        return leucos * (neu_perc / 100)

    # --- UCI / PROCEDIMIENTOS ---
    @staticmethod
    def calc_velocidad_bomba(dosis_ug_kg_min: float, peso: float, concentracion_ug_ml: float) -> float:
        if concentracion_ug_ml <= 0: return 0.0
        return (dosis_ug_kg_min * peso * 60) / concentracion_ug_ml
    
    @staticmethod
    def calc_reposicion_albumina(litros_extraidos: float) -> float:
        """
        Gramos de albúmina a reponer en paracentesis evacuadora.
        Regla: > 5L -> 8g albúmina por cada litro total extraído.
        """
        if litros_extraidos < 5: return 0.0
        return litros_extraidos * 8