from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from decimal import Decimal
from django.contrib import messages

from ..models import Promocion, Venta, Cisterna 
from ..forms import PromocionForm


@login_required
def promos_view(request):
    """
    Muestra la página de promociones y el formulario de registro.
    """
    promo_form = PromocionForm()

    promociones = Promocion.objects.filter(botellas_pagadas__gt=F('botellas_retiradas')).order_by('-id')

    context = {
        'promo_form': promo_form,
        'promociones': promociones,
    }
    return render(request, 'core/promos.html', context)


@login_required
def registrar_promocion(request):
    """
    Procesa el formulario de registro de promociones.
    """
    if request.method == 'POST':
        form = PromocionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                promo = form.save(commit=False)
                promo.botellas_retiradas = 0
                promo.save()
                
                # Se crea una Venta con total de 0 para registrar la promoción.
                # Asegúrate de que tu modelo Venta tenga los campos `total_venta_divisa`, `total_venta_bs` y `tipo_venta`.
                Venta.objects.create(
                    usuario=request.user,
                    total_venta_divisa=Decimal('0.00'),
                    total_venta_bs=Decimal('0.00'),
                    tipo_venta='Promocion'
                )
            messages.success(request, "Promoción registrada correctamente.")
            return redirect('promos')
        else:
            messages.error(request, "Error al registrar la promoción. Revisa los datos.")
            return redirect('promos')
    # Si la petición no es POST, redirige a la página principal de promos.
    return redirect('promos')


@login_required
@transaction.atomic
def restar_botella(request, promo_id):
    promocion = get_object_or_404(Promocion, id=promo_id)
    pendientes = promocion.botellas_pagadas - promocion.botellas_retiradas

    if pendientes > 0:
        try:
            cisterna = Cisterna.objects.latest('id')
        except Cisterna.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No hay cisternas registradas.'})

        litros_a_restar = Decimal('20.00')

        if cisterna.litros_disponibles < litros_a_restar:
            return JsonResponse({'success': False, 'error': 'No hay suficientes litros disponibles en la cisterna.'})

        promocion.botellas_retiradas = F('botellas_retiradas') + 1
        promocion.save(update_fields=['botellas_retiradas'])

        cisterna.litros_disponibles = F('litros_disponibles') - litros_a_restar
        cisterna.save(update_fields=['litros_disponibles'])
        
        promocion.refresh_from_db()

        # Se crea una Venta con total de 0 para registrar la botella retirada.
        # Asegúrate de que tu modelo Venta tenga los campos `total_venta_divisa`, `total_venta_bs` y `tipo_venta`.
        Venta.objects.create(
            usuario=request.user,
            total_venta_divisa=Decimal('0.00'),
            total_venta_bs=Decimal('0.00'),
            tipo_venta='Promocion'
        )

        return JsonResponse({
            'success': True,
            'botellas_restantes': promocion.botellas_pagadas - promocion.botellas_retiradas
        })
    else:
        return JsonResponse({'success': False, 'error': 'No hay botellas pendientes'})
