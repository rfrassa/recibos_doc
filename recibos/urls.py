from django.urls import path
from . import views

urlpatterns = [
    path('recibo/<int:recibo_id>/', views.ver_recibo, name='ver_recibo'),
]
