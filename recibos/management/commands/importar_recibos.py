# importar_recibos.py

import os
from django.core.management.base import BaseCommand
from django.db import transaction
from recibos.models import Recibo, Concepto
from leer_recibos_ocr_lineas import leer_recibos


class Command(BaseCommand):
    help = 'Importa recibos desde archivos OCR en formato .txt'

    def add_arguments(self, parser):
        parser.add_argument('carpeta', type=str, help='Carpeta con archivos .txt OCR')

    def handle(self, *args, **kwargs):
        carpeta = kwargs['carpeta']
        total = 0

        try:
            recibos = leer_recibos(carpeta)
            with transaction.atomic():
                for recibo in recibos:
                    dni = recibo.get('dni')
                    if not dni:
                        self.stdout.write(f"⛔ Saltando recibo sin DNI: {recibo.get('nombre')}")
                        continue

                    recibo_obj, created = Recibo.objects.update_or_create(
                        dni=dni,
                        mes=recibo['mes'],
                        defaults={
                            'nombre': recibo['nombre'],
                            'centro_pago': recibo['centro_pago'],
                            'cargo': recibo['cargo'],
                            'fecha_alta': recibo['fecha_alta'],
                            'rol': recibo['rol'],
                            'dias_trabajados': recibo.get('dias_trabajados'),
                            'rem_c_aporte': recibo['rem_c_aporte'],
                            'rem_s_aporte': recibo['rem_s_aporte'],
                            'reduccion_pav': recibo['reduccion_pav'],
                            'salario_familiar': recibo['salario_familiar'],
                            'liquido': recibo['liquido'],
                        }
                    )

                    # 1) remove old conceptos
                    recibo_obj.concepto_set.all().delete()

                    # 2) prepare new Concepto instances
                    objs = [
                        Concepto(
                            recibo=recibo_obj,
                            codigo=c['codigo'],
                            descripcion=c['descripcion'],
                            tipo=c['tipo'],
                            monto=c['monto'],
                        )
                        for c in recibo['conceptos']
                    ]
                    # bulk insert in one go
                    Concepto.objects.bulk_create(objs)

                    op = "Creado" if created else "Actualizado"
                    self.stdout.write(f"✔ {op} recibo {recibo['nombre']} (DNI {dni})")
                    total += 1

            self.stdout.write(f"✅ Total procesados: {total}")

        except Exception as e:
            self.stderr.write(f"❌ Error: {e}")
