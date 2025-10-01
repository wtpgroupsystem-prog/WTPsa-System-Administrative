from django.shortcuts import render
from ..decorators import role_required

@role_required('dueno')
def control_mensual(request):
    return render(request, 'core/control_mensual.html')

@role_required('dueno')
def control_anual(request):
    return render(request, 'core/control_anual.html')