import pdfplumber
import re
from pathlib import Path

def limpiar_monto(valor_str):
    try:
        return float(valor_str.replace('.', '').replace(',', '.'))
    except:
        return 0.0

def extraer_mes_desde_nombre(nombre_archivo):
    meses = {
        '01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril',
        '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto',
        '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
    }
    match = re.search(r'(\d{2})(\d{4})', nombre_archivo)
    if match:
        mes = meses.get(match.group(1), None)
        anio = match.group(2)
        if mes:
            return f"{mes} {anio}"
    return None

def leer_recibos(path_pdf):
    recibos = []
    nombre_archivo = Path(path_pdf).stem
    mes_desde_nombre = extraer_mes_desde_nombre(nombre_archivo)

    with pdfplumber.open(path_pdf) as pdf:
        texto_total = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    bloques = re.split(r'Id\. Hr:\s*(\d+)\s*Apellido y Nombre\s*:\s*', texto_total)[1:]
    for i in range(0, len(bloques), 2):
        dni = bloques[i].strip()
        bloque = bloques[i+1]
        lineas = bloque.strip().split("\n")

        nombre_match = re.search(r'^([A-ZÑÁÉÍÓÚÜ, ]+)', bloque.strip())
        nombre = nombre_match.group(1).strip() if nombre_match else 'SIN NOMBRE'

        recibo = {
            'dni': dni,
            'nombre': nombre,
            'centro_pago': None,
            'cargo': None,
            'fecha_alta': None,
            'rol': None,
            'dias_trabajados': None,
            'mes': None,
            'rem_c_aporte': 0,
            'rem_s_aporte': 0,
            'reduccion_pav': 0,
            'salario_familiar': 0,
            'liquido': 0,
            'conceptos': []
        }

        patrones = {
            'centro_pago': r'Centro Pago:\s*(\w+)',
            'cargo': r'Cargo:\s*(\d+)',
            'fecha_alta': r'Fecha Alta:\s*([\d/]+)',
            'rol': r'Rol:\s*(\d+)',
            'dias_trabajados': r'Dias Trab:\s*-?\s*(\d*)',
            'rem_s_aporte': r'Rem s/ Aporte\s*([\d.,]+)',
            'rem_c_aporte': r'Rem c/ Aporte\s*([\d.,]+)',
            'reduccion_pav': r'Reducción PAV\s*([\d.,]+)',
            'salario_familiar': r'Salario Familiar\s*:\s*([\d.,]+)',
            'liquido': r'Liq(?:uido)?\.?\s+(?:Pesos|Letras)?\s*:?\s*\$?\s*([\d.,]+)'
        }

        for campo, patron in patrones.items():
            match = re.search(patron, bloque)
            if match:
                valor = match.group(1)
                if campo in ['rem_s_aporte', 'rem_c_aporte', 'reduccion_pav', 'salario_familiar', 'liquido']:
                    recibo[campo] = limpiar_monto(valor)
                else:
                    recibo[campo] = valor.strip()

        if not recibo['mes']:
            mes_match = re.search(r'(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)\s+\d{4}', bloque, re.IGNORECASE)
            if mes_match:
                recibo['mes'] = mes_match.group(0).capitalize()
            elif mes_desde_nombre:
                recibo['mes'] = mes_desde_nombre

        for idx in range(len(lineas)):
            linea = lineas[idx].strip()

            if re.match(r'^(DV|RT)?\s*\d{5,7}\s+', linea):
                partes = linea.split()
                if len(partes) >= 2:
                    codigo = partes[1] if partes[0] in ['DV', 'RT'] else partes[0]
                    tipo = 'rem' if 'DV' in linea or codigo.startswith("1") else 'desc' if 'RT' in linea or codigo.startswith("6") else 'otro'
                    descripcion = " ".join(partes[2:]) if partes[0] in ['DV', 'RT'] else " ".join(partes[1:])
                    monto = 0
                    if idx + 1 < len(lineas):
                        monto_linea = lineas[idx + 1].strip()
                        monto_match = re.match(r'\$?\s*([\d.,]+)$', monto_linea)
                        if monto_match:
                            monto = limpiar_monto(monto_match.group(1))
                    recibo['conceptos'].append({
                        'codigo': codigo,
                        'descripcion': descripcion,
                        'tipo': tipo,
                        'monto': monto
                    })

        recibos.append(recibo)

    return recibos