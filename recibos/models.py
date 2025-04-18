from django.db import models

class Empleado(models.Model):
    dni = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    centro_pago = models.CharField(max_length=50, null=True, blank=True)
    cargo = models.CharField(max_length=50, null=True, blank=True)
    fecha_alta = models.CharField(max_length=10, null=True, blank=True)
    fecha_nacimiento = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} (DNI: {self.dni})"

class Recibo(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, null=True, blank=True)
    dias_trabajados = models.IntegerField(null=True, blank=True)
    mes = models.CharField(max_length=20)
    rem_c_aporte = models.FloatField(default=0.0)
    rem_s_aporte = models.FloatField(default=0.0)
    reduccion_pav = models.FloatField(default=0.0)
    salario_familiar = models.FloatField(default=0.0)
    liquido = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empleado.nombre} - Rol {self.rol} - {self.mes}"

class Concepto(models.Model):
    recibo = models.ForeignKey(Recibo, related_name='conceptos', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=[('rem', 'Remuneración'), ('desc', 'Descuento')])
    monto = models.FloatField()

    def __str__(self):
        return f"{self.descripcion} ({self.codigo}) - {self.monto}"


# models.py - Empleado
# cargo = models.CharField(max_length=100, blank=True, null=True)
# obra_social = models.CharField(max_length=100, blank=True, null=True)
# cuil = models.CharField(max_length=20, blank=True, null=True)
# domicilio = models.TextField(blank=True, null=True)
# rol = models.IntegerField(default=1)