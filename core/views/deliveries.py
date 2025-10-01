from django.shortcuts import render, redirect, get_object_or_404
from ..models import Delivery
from ..forms import DeliveryForm
from ..decorators import role_required

@role_required('encargada')
def deliveries(request):
    """
    View para mostrar la lista de entregas y manejar la creación de una nueva.
    """
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('deliveries')
    else:
        form = DeliveryForm()
    
    deliveries = Delivery.objects.all()
    return render(request, 'core/deliveries.html', {'form': form, 'deliveries': deliveries})

@role_required('encargada')
def delete_delivery(request, delivery_id):
    """
    View para eliminar una entrega específica.
    """
    # Busca la entrega por su ID o devuelve un error 404 si no existe
    delivery = get_object_or_404(Delivery, id=delivery_id)
    
    # Si el método de la solicitud es POST, procedemos a eliminar la entrega
    if request.method == 'POST':
        delivery.delete()
        return redirect('deliveries')
    
    # En caso de que no sea una solicitud POST, se puede mostrar una página de confirmación
    # o simplemente redirigir. Para este ejemplo, simplemente redirigimos.
    return redirect('deliveries')
