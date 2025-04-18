from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Recibo
from num2words import num2words


# Create your views here.
def ver_recibo(request, recibo_id):
    recibo = get_object_or_404(Recibo, id=recibo_id)
    conceptos = recibo.concepto_set.all()
    total_en_letras = num2words(recibo.total_liquido, lang='es').upper()

    return render(request, 'recibos/recibo.html', {
        'recibo': recibo,
        'conceptos': conceptos,
        'total_en_letras': total_en_letras
    })
