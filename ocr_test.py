from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# Ruta al ejecutable de Tesseract (ajustado a tu entorno Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
custom_config = r'-l spa'

# Archivo PDF de origen
pdf_path = "EE1240253_LIQHAB_042024.PDF"

try:
    # Convertimos todas las páginas a imágenes
    paginas = convert_from_path(pdf_path, dpi=200)
    print(f"Se convirtieron {len(paginas)} páginas del PDF.")

    for i, imagen in enumerate(paginas, start=1):
        texto = pytesseract.image_to_string(imagen, config=custom_config)
        print(f"\n=== TEXTO OCR - Página {i} ===")
        print(texto)
        # También podés guardar el resultado si querés revisarlo después:
        with open(f"ocr_pagina_{i}.txt", "w", encoding="utf-8") as f:
            f.write(texto)

except Exception as e:
    print(f"❌ Error al procesar el PDF: {e}")

