from django.contrib import admin
from .models import Empleado, Recibo, Concepto

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dni', 'centro_pago')  # quitamos 'cuil'
    search_fields = ('nombre', 'dni')

@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'mes', 'rol', 'liquido')  # 'liquido' en lugar de 'total_liquido'
    list_filter = ('mes', 'rol')
    search_fields = ('empleado__nombre', 'rol')

@admin.register(Concepto)
class ConceptoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'tipo', 'monto', 'recibo')
    list_filter = ('tipo',)
    search_fields = ('descripcion', 'codigo')
