from django.shortcuts import render
from django.http import HttpResponse
from ..models import Venta, Cisterna
from django.contrib.auth.decorators import login_required
from datetime import datetime

@login_required
def dashboard(request):
    # Datos de ejemplo, reemplaza con los valores reales de tu base de datos
    litros_disponibles = 5000  # Este valor puede ser calculado dinámicamente desde tu base de datos
    ventas = Venta.objects.filter(fecha=datetime.today()).count()
    cisternas = Cisterna.objects.all()

    context = {
        'litros_disponibles': litros_disponibles,
        'ventas': ventas,
        'cisternas': cisternas,
    }
    
    return render(request, 'core/dashboard.html', context)
