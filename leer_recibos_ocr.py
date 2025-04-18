
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import re
import tempfile
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def limpiar_monto(texto):
    try:
        return float(texto.replace('.', '').replace(',', '.'))
    except:
        return 0.0

def leer_recibos(path_pdf):
    path_pdf = Path(path_pdf)
    if not path_pdf.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path_pdf}")

    imagenes = convert_from_path(str(path_pdf), dpi=200)
    texto_total = ""

    for imagen in imagenes:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            imagen.save(tmp.name, "PNG")
            texto = pytesseract.image_to_string(Image.open(tmp.name), config='--psm 6 -l spa')
            texto_total += texto + "\n"

    bloques = re.split(r'(Id\. Hr:\s*\d+\s*Apellido y Nombre\s*:\s*[^\n]+)', texto_total)
    recibos = []
    if not bloques:
        return recibos

    for i in range(1, len(bloques), 2):
        encabezado = bloques[i]
        cuerpo = bloques[i+1]
        bloque_completo = encabezado + "\n" + cuerpo

        dni_match = re.search(r'Id\. Hr:\s*(\d+)', encabezado)
        nombre_match = re.search(r'Apellido y Nombre\s*:\s*([^\n]+)', encabezado)
        if not dni_match or not nombre_match:
            continue

        dni = dni_match.group(1).strip()
        nombre = nombre_match.group(1).strip()

        roles_bloques = re.split(r'Rol:\s*(\d+)', cuerpo)
        for j in range(1, len(roles_bloques), 2):
            rol = roles_bloques[j].strip()
            contenido = roles_bloques[j+1]

            cargo = re.search(r'Cargo:\s*(\d+)', contenido)
            fecha_alta = re.search(r'Fecha Alta:\s*([\d/]+)', contenido)
            centro_pago = re.search(r'Centro Pago:\s*(\w+)', contenido)

            rem_c_aporte = re.search(r'Rem c/ Aporte\s*([\d.,]+)', contenido)
            rem_s_aporte = re.search(r'Rem s/ Aporte\s*([\d.,]+)', contenido)
            liq_pesos = re.search(r'Liq\.? Pesos:\s*([\d.,]+)', contenido)

            conceptos = []
            for linea in contenido.splitlines():
                linea = linea.strip()
                match = re.match(r'(DV|RT)\s+(\d+)\s+(.*?)\s+([\d.,]+)$', linea, re.IGNORECASE)
                if match:
                    tipo_bruto = match.group(1).upper()
                    tipo = 'rem' if tipo_bruto == 'DV' else 'desc'
                    codigo = match.group(2)
                    descripcion = match.group(3).strip()
                    monto = limpiar_monto(match.group(4))
                    conceptos.append({
                        "codigo": codigo,
                        "descripcion": descripcion,
                        "tipo": tipo,
                        "monto": monto
                    })

            recibos.append({
                "dni": dni,
                "nombre": nombre,
                "rol": rol,
                "cargo": cargo.group(1) if cargo else None,
                "fecha_alta": fecha_alta.group(1) if fecha_alta else None,
                "centro_pago": centro_pago.group(1) if centro_pago else None,
                "rem_c_aporte": limpiar_monto(rem_c_aporte.group(1)) if rem_c_aporte else 0,
                "rem_s_aporte": limpiar_monto(rem_s_aporte.group(1)) if rem_s_aporte else 0,
                "liquido": limpiar_monto(liq_pesos.group(1)) if liq_pesos else 0,
                "conceptos": conceptos
            })

    return recibos
