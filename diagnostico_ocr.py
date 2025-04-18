from pathlib import Path

archivos = sorted(Path(".").glob("ocr_pagina_*.txt"))

print(f"📁 Se encontraron {len(archivos)} archivos OCR.")

for path in archivos:
    print(f"\n📄 {path.name}")
    with open(path, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    print(f"🔍 Total líneas: {len(lineas)}")

    id_lineas = [l for l in lineas if "Id. Hr" in l]
    print(f"🔍 Líneas con 'Id. Hr': {len(id_lineas)}")

    if id_lineas:
        print("🧾 Ejemplo:")
        print(id_lineas[0].strip())
