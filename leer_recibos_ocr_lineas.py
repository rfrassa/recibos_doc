import re
from pathlib import Path
from datetime import datetime

def normalizar_fecha(fecha_str):
    try:
        return datetime.strptime(fecha_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        try:
            # Manejar casos como 2006/1966
            if '/' in fecha_str and len(fecha_str.split('/')[-1]) == 4:
                return datetime.strptime(fecha_str.split('/')[-1], '%Y').strftime('%Y-%m-%d')
        except:
            return None

def limpiar_monto(valor_str):
    try:
        return float(valor_str.replace('.', '').replace(',', '.'))
    except:
        return 0.0

def leer_recibos(carpeta_textos):
    recibos = []
    dnis_procesados = set()
    lineas_acumuladas = []
    mes_global = "Diciembre 2025"  # Ajustar según el mes del PDF

    archivos = sorted(Path(carpeta_textos).glob("ocr_pagina_*.txt"))
    for archivo in archivos:
        with open(archivo, encoding="utf-8") as f:
            lineas = [linea.strip() for linea in f.readlines() if linea.strip()]

        for linea in lineas:
            dni_match = re.search(r'Id\. Hr[:=]\s*(\d{6,})', linea)
            if dni_match and dni_match.group(1) in dnis_procesados:
                continue  # Saltar DNI ya procesado
            if re.search(r'^Id\. Hr[:=]', linea):
                if lineas_acumuladas:
                    recibo = procesar_bloque(lineas_acumuladas, mes_global)
                    if recibo and recibo['dni'] not in dnis_procesados:
                        recibos.append(recibo)
                        dnis_procesados.add(recibo['dni'])
                    lineas_acumuladas = []
            lineas_acumuladas.append(linea)

        # Procesar bloques sin Id. Hr al final de cada archivo
        if lineas_acumuladas and not any(re.search(r'^Id\. Hr[:=]', l) for l in lineas_acumuladas):
            recibo = procesar_bloque_sin_dni(lineas_acumuladas, mes_global)
            if recibo:
                recibos.append(recibo)
            lineas_acumuladas = []

    # Procesar cualquier bloque restante
    if lineas_acumuladas:
        recibo = procesar_bloque(lineas_acumuladas, mes_global)
        if recibo and recibo['dni'] not in dnis_procesados:
            recibos.append(recibo)

    return recibos

def procesar_bloque_sin_dni(lineas, mes_global):
    texto_bloque = " ".join(lineas)
    recibo = {
        'dni': 'SIN_DNI',
        'nombre': 'SIN_NOMBRE',
        'centro_pago': None,
        'cargo': None,
        'fecha_alta': None,
        'fecha_nacimiento': None,
        'rol': None,
        'dias_trabajados': None,
        'mes': mes_global,
        'rem_c_aporte': 0.0,
        'rem_s_aporte': 0.0,
        'reduccion_pav': 0.0,
        'salario_familiar': 0.0,
        'liquido': 0.0,
        'conceptos': []
    }

    # Extraer montos
    patrones = {
        'rem_s_aporte': r'Rem s/ Aporte[:=\s]*([\d.,]+)',
        'rem_c_aporte': r'Rem c/ Aporte[:=\s]*([\d.,]+)',
        'reduccion_pav': r'Reducción PAV[:=\s]*([\d.,]+)',
        'salario_familiar': r'Salario Familiar[:=\s]*([\d.,]+)',
        'liquido': r'Liq(?:uido)?\.?(?: Pesos| Letras)?[:=\s]*\$?([\d.,]+)'
    }

    for campo, patron in patrones.items():
        match = re.search(patron, texto_bloque)
        if match:
            valor = match.group(1)
            recibo[campo] = limpiar_monto(valor)

    # Buscar conceptos DV o RT
    for linea in lineas:
        match_concepto = re.match(r'^(DV|RT)\s*(\d{5,6})\s+(.+?)\s+([\d.,]+)$', linea)
        if match_concepto:
            tipo = 'rem' if match_concepto.group(1) == 'DV' else 'desc'
            codigo = match_concepto.group(2)
            descripcion = match_concepto.group(3).strip()
            monto = limpiar_monto(match_concepto.group(4))
            recibo['conceptos'].append({
                'codigo': codigo,
                'descripcion': descripcion,
                'tipo': tipo,
                'monto': monto
            })

    return recibo

def procesar_bloque(lineas, mes_global):
    texto_bloque = " ".join(lineas)
    dni_match = re.search(r'Id\. Hr[:=]\s*(\d{6,})', texto_bloque)
    nombre_match = re.search(r'Apellido y Nombre[:=]?\s*([A-ZÑÁÉÍÓÚ, ]+)', texto_bloque)
    rol_match = re.search(r'Rol[:=]?\s*(\d+)', texto_bloque)

    if not dni_match:  # Solo DNI es obligatorio
        return None

    dni = dni_match.group(1)
    nombre = nombre_match.group(1).strip() if nombre_match else "SIN_NOMBRE"
    rol = rol_match.group(1) if rol_match else None  # Permitir None para rol

    recibo = {
        'dni': dni,
        'nombre': nombre,
        'centro_pago': None,
        'cargo': None,
        'fecha_alta': None,
        'fecha_nacimiento': None,
        'rol': rol,
        'dias_trabajados': None,
        'mes': mes_global,
        'rem_c_aporte': 0.0,
        'rem_s_aporte': 0.0,
        'reduccion_pav': 0.0,
        'salario_familiar': 0.0,
        'liquido': 0.0,
        'conceptos': []
    }

    # Datos individuales
    patrones = {
        'centro_pago': r'Centro Pago[:=]?\s*(\w+)',
        'cargo': r'Cargo[:=]?\s*(\d+)',
        'fecha_alta': r'Fecha Antig\.?[:=]?\s*([\d/]+)',
        'fecha_nacimiento': r'Fec\. Nac\.?[:=]?\s*([\d/]+)',
        'dias_trabajados': r'Dias Trab[:=\s]+(\d{1,3})',
        'rem_s_aporte': r'Rem s/ Aporte[:=\s]*([\d.,]+)',
        'rem_c_aporte': r'Rem c/ Aporte[:=\s]*([\d.,]+)',
        'reduccion_pav': r'Reducción PAV[:=\s]*([\d.,]+)',
        'salario_familiar': r'Salario Familiar[:=\s]*([\d.,]+)',
        'liquido': r'Liq(?:uido)?\.?(?: Pesos| Letras)?[:=\s]*\$?([\d.,]+)'
    }

    for campo, patron in patrones.items():
        match = re.search(patron, texto_bloque)
        if match:
            valor = match.group(1)
            if campo in ['rem_s_aporte', 'rem_c_aporte', 'reduccion_pav', 'salario_familiar', 'liquido']:
                recibo[campo] = limpiar_monto(valor)
            elif campo in ['fecha_alta', 'fecha_nacimiento']:
                recibo[campo] = normalizar_fecha(valor)
            else:
                recibo[campo] = valor.strip()

    # Buscar conceptos DV o RT
    for linea in lineas:
        match_concepto = re.match(r'^(DV|RT)\s*(\d{5,6})\s+(.+?)\s+([\d.,]+)$', linea)
        if match_concepto:
            tipo = 'rem' if match_concepto.group(1) == 'DV' else 'desc'
            codigo = match_concepto.group(2)
            descripcion = match_concepto.group(3).strip()
            monto = limpiar_monto(match_concepto.group(4))
            recibo['conceptos'].append({
                'codigo': codigo,
                'descripcion': descripcion,
                'tipo': tipo,
                'monto': monto
            })

    return recibo