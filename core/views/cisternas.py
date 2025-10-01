from django.shortcuts import render, redirect
from ..models import Cisterna
from ..forms import CisternaForm
from ..decorators import role_required

@role_required('trabajador')
def cisternas(request):
    if request.method == 'POST':
        form = CisternaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cisternas')
    else:
        form = CisternaForm()
    cisternas = Cisterna.objects.all()
    return render(request, 'core/cisternas.html', {'form': form, 'cisternas': cisternas})