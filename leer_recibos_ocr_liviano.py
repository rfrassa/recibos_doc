# from pdf2image import convert_from_path
# from PIL import Image
# import pytesseract
# import re
# import tempfile
# from pathlib import Path

# def limpiar_monto(valor_str):
#     try:
#         return float(valor_str.replace('.', '').replace(',', '.'))
#     except:
#         return 0.0

# def leer_recibos(path_pdf):
#     path_pdf = Path(path_pdf)
#     if not path_pdf.exists():
#         raise FileNotFoundError(f"No se encontró el archivo: {path_pdf}")

#     recibos = []

#     # Obtener cantidad total de páginas
#     try:
#         from pdf2image.pdf2image import pdfinfo_from_path
#         info = pdfinfo_from_path(str(path_pdf))
#         total_paginas = int(info["Pages"])
#     except Exception as e:
#         raise RuntimeError(f"No se pudo contar páginas del PDF: {e}")

#     for i in range(1, total_paginas + 1):
#         try:
#             imagenes = convert_from_path(str(path_pdf), dpi=150, first_page=i, last_page=i)
#         except Exception as e:
#             print(f"❌ Error procesando página {i}: {e}")
#             continue

#         for imagen in imagenes:
#             with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
#                 imagen.save(tmp.name, "PNG")
#                 texto_pagina = pytesseract.image_to_string(Image.open(tmp.name), config='--psm 6 -l spa')

#             bloques = re.split(r'(Id\. Hr:\s*\d+\s*Apellido y Nombre\s*:\s*[^\n]+)', texto_pagina)
#             if not bloques:
#                 continue

#             for b in range(1, len(bloques), 2):
#                 encabezado = bloques[b]
#                 cuerpo = bloques[b + 1]
#                 bloque_completo = encabezado + "\n" + cuerpo

#                 dni_match = re.search(r'Id\. Hr:\s*(\d+)', encabezado)
#                 nombre_match = re.search(r'Apellido y Nombre\s*:\s*([^\n]+)', encabezado)
#                 if not dni_match or not nombre_match:
#                     continue

#                 dni = dni_match.group(1).strip()
#                 nombre = nombre_match.group(1).strip()

#                 roles_bloques = re.split(r'Rol:\s*(\d+)', cuerpo)
#                 for j in range(1, len(roles_bloques), 2):
#                     rol = roles_bloques[j].strip()
#                     contenido = roles_bloques[j + 1]

#                     cargo = re.search(r'Cargo:\s*(\d+)', contenido)
#                     fecha_alta = re.search(r'Fecha Alta:\s*([\d/]+)', contenido)
#                     centro_pago = re.search(r'Centro Pago:\s*(\w+)', contenido)

#                     rem_c_aporte = re.search(r'Rem c/ Aporte\s*([\d.,]+)', contenido)
#                     rem_s_aporte = re.search(r'Rem s/ Aporte\s*([\d.,]+)', contenido)
#                     liq_pesos = re.search(r'Liq\.? Pesos:\s*([\d.,]+)', contenido)

#                     conceptos = []
#                     for linea in contenido.splitlines():
#                         linea = linea.strip()
#                         match = re.match(r'(DV|RT)\s+(\d+)\s+(.*?)\s+([\d.,]+)$', linea, re.IGNORECASE)
#                         if match:
#                             tipo_bruto = match.group(1).upper()
#                             tipo = 'rem' if tipo_bruto == 'DV' else 'desc'
#                             codigo = match.group(2)
#                             descripcion = match.group(3).strip()
#                             monto = limpiar_monto(match.group(4))
#                             conceptos.append({
#                                 "codigo": codigo,
#                                 "descripcion": descripcion,
#                                 "tipo": tipo,
#                                 "monto": monto
#                             })

#                     recibos.append({
#                         "dni": dni,
#                         "nombre": nombre,
#                         "rol": rol,
#                         "cargo": cargo.group(1) if cargo else None,
#                         "fecha_alta": fecha_alta.group(1) if fecha_alta else None,
#                         "centro_pago": centro_pago.group(1) if centro_pago else None,
#                         "rem_c_aporte": limpiar_monto(rem_c_aporte.group(1)) if rem_c_aporte else 0,
#                         "rem_s_aporte": limpiar_monto(rem_s_aporte.group(1)) if rem_s_aporte else 0,
#                         "liquido": limpiar_monto(liq_pesos.group(1)) if liq_pesos else 0,
#                         "conceptos": conceptos
#                     })

#     return recibos

from pathlib import Path
import re
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from datetime import datetime

def limpiar_monto(valor_str):
    try:
        return float(valor_str.replace('.', '').replace(',', '.'))
    except Exception:
        return 0.0

def leer_recibos(path_pdf):
    path_pdf = Path(path_pdf)
    conceptos_globales = []
    recibos = []
    try:
        paginas = convert_from_path(str(path_pdf), dpi=200)
    except Exception as e:
        print(f"❌ Error abriendo PDF: {e}")
        return []

    for i, pagina in enumerate(paginas):
        try:
            texto = pytesseract.image_to_string(pagina, lang='spa')
            bloques = re.split(r"Id\. Hr:\s*(\d+)", texto)

            for j in range(1, len(bloques), 2):
                dni = bloques[j].strip()
                bloque = bloques[j + 1]

                # Buscar nombre
                nombre_match = re.search(r"Apellido y Nombre\s*:\s*(.*)", bloque)
                nombre = nombre_match.group(1).strip() if nombre_match else "SIN NOMBRE"

                # Buscar rol
                rol_match = re.search(r"Rol:\s*(\d+)", bloque)
                rol = rol_match.group(1) if rol_match else None

                # Buscar mes y año desde el nombre del archivo
                nombre_archivo = path_pdf.name
                fecha_match = re.search(r"(\d{6})", nombre_archivo)
                if fecha_match:
                    raw = fecha_match.group(1)
                    mes = datetime.strptime(raw, "%m%Y").strftime("%B %Y")
                else:
                    mes = None

                # Buscar totales
                rem_c_aporte = limpiar_monto(re.search(r"Rem c/ Aporte\s*([\d.,]+)", bloque).group(1)) if re.search(r"Rem c/ Aporte\s*([\d.,]+)", bloque) else 0
                rem_s_aporte = limpiar_monto(re.search(r"Rem s/ Aporte\s*([\d.,]+)", bloque).group(1)) if re.search(r"Rem s/ Aporte\s*([\d.,]+)", bloque) else 0
                salario_familiar = limpiar_monto(re.search(r"Salario Familiar\s*:\s*([\d.,]+)", bloque).group(1)) if re.search(r"Salario Familiar\s*:\s*([\d.,]+)", bloque) else 0
                liquido = limpiar_monto(re.search(r"Liq\.? Pesos\s*:\s*([\d.,]+)", bloque).group(1)) if re.search(r"Liq\.? Pesos\s*:\s*([\d.,]+)", bloque) else 0

                # Buscar conceptos
                conceptos = []
                lineas = bloque.splitlines()
                for linea in lineas:
                    if "DV" in linea or "RT" in linea:
                        linea = linea.strip()
                        tipo = "rem" if "DV" in linea else "desc"
                        item_match = re.search(r"(DV|RT)\s*(\d+)\s+(.+?)\s+([\d.,]+)$", linea)
                        if item_match:
                            codigo = item_match.group(2)
                            descripcion = item_match.group(3).strip()
                            monto = limpiar_monto(item_match.group(4))
                            conceptos.append({
                                "codigo": codigo,
                                "descripcion": descripcion,
                                "tipo": tipo,
                                "monto": monto
                            })

                if conceptos:
                    recibo = {
                        "dni": dni,
                        "nombre": nombre,
                        "rol": rol,
                        "mes": mes,
                        "rem_c_aporte": rem_c_aporte,
                        "rem_s_aporte": rem_s_aporte,
                        "salario_familiar": salario_familiar,
                        "liquido": liquido,
                        "conceptos": conceptos
                    }
                    recibos.append(recibo)
        except Exception as e:
            print(f"❌ Error procesando página {i+1}: {e}")
            continue
    return recibos
