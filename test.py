from leer_recibos_old import leer_recibos

resultados = leer_recibos("EE1240253_LIQHAB_2511240.pdf")

for r in resultados:
    print(f"{r['nombre']} - {r['dni']}")
    print(f"Centro de pago: {r['centro_pago']} | Cargo: {r['cargo']} | Fecha alta: {r['fecha_alta']}")
    print(f"Rem c/Aporte: {r['rem_c_aporte']} | Rem s/Aporte: {r['rem_s_aporte']}")
    print(f"Líquido: {r['liquido']} | Conceptos: {len(r['conceptos'])}")
    print("--------")
