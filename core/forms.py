from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import (
    Venta, Cisterna, Delivery, Promocion, TasaCambio, Producto
)

# Clases CSS estandarizadas para los widgets de formulario
FORM_WIDGET_CLASS = 'form-input w-full px-3 py-2 border rounded-md focus:outline-none focus:ring focus:ring-blue-300'

# ---------------------- Formularios de Autenticación ----------------------
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': FORM_WIDGET_CLASS,
        'placeholder': 'Usuario'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': FORM_WIDGET_CLASS,
        'placeholder': 'Contraseña'
    }))


# ---------------------- Formularios de Inventario y Control ----------------------
class CisternaForm(forms.ModelForm):
    class Meta:
        model = Cisterna
        fields = ['fecha', 'hora', 'volumen']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': FORM_WIDGET_CLASS
            }),
            'hora': forms.TimeInput(attrs={
                'type': 'time',
                'class': FORM_WIDGET_CLASS
            }),
            'volumen': forms.NumberInput(attrs={
                'class': FORM_WIDGET_CLASS,
                'placeholder': 'Cantidad de litros',
                'step': 'any',
                'min': '0',
            }),
        }

class ProductoForm(forms.ModelForm):
    """
    Formulario para la gestión de productos, incluyendo creación y edición.
    """
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'precio_divisa', 'precio_bolivares', 'stock', 'tipo']
        labels = {
            'codigo': 'Código',
            'nombre': 'Nombre del Producto',
            'precio_divisa': 'Precio en Divisa ($)',
            'precio_bolivares': 'Precio en Bolívares (Bs)',
            'stock': 'Stock Inicial',
            'tipo': 'Tipo de Producto',
        }
        widgets = {
            'codigo': forms.TextInput(attrs={'class': FORM_WIDGET_CLASS, 'placeholder': 'Ej: 00001', 'render_value': True}),
            'nombre': forms.TextInput(attrs={'class': FORM_WIDGET_CLASS, 'placeholder': 'Ej: Botella de 20L', 'render_value': True}),
            'precio_divisa': forms.NumberInput(attrs={'class': FORM_WIDGET_CLASS, 'step': '0.01', 'render_value': True}),
            'precio_bolivares': forms.NumberInput(attrs={'class': FORM_WIDGET_CLASS, 'step': '0.01', 'render_value': True}),
            'stock': forms.NumberInput(attrs={'class': FORM_WIDGET_CLASS, 'render_value': True}),
            'tipo': forms.Select(attrs={'class': 'form-select ' + FORM_WIDGET_CLASS, 'render_value': True}),
        }

class TasaCambioForm(forms.ModelForm):
    """
    Formulario para la gestión de la tasa de cambio del día.
    """
    class Meta:
        model = TasaCambio
        fields = ['tasa_bsd']
        widgets = {
            'tasa_bsd': forms.NumberInput(attrs={
                'class': FORM_WIDGET_CLASS,
                'step': '0.01',
                'placeholder': 'Ej. 30.50',
            })
        }
        
# ---------------------- Formularios de Ventas ----------------------
# Nota: La lógica de la venta se maneja principalmente en la vista.
# Estos formularios son de apoyo.

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = []

# ---------------------- Otros Formularios ----------------------
class DeliveryForm(forms.ModelForm):
    """
    Formulario para el registro de deliveries.
    """
    class Meta:
        model = Delivery
        fields = ['nombre_cliente', 'direccion', 'litros_entregados']
        labels = {
            'nombre_cliente': 'Nombre del Cliente',
            'direccion': 'Dirección de Entrega',
            'litros_entregados': 'Litros Entregados',
        }
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={'class': FORM_WIDGET_CLASS, 'placeholder': 'Nombre Completo'}),
            'direccion': forms.TextInput(attrs={'class': FORM_WIDGET_CLASS, 'placeholder': 'Dirección Completa'}),
            'litros_entregados': forms.NumberInput(attrs={'class': FORM_WIDGET_CLASS, 'placeholder': 'Litros', 'min': '0', 'step': '0.01'}),
        }


class PromocionForm(forms.ModelForm):
    class Meta:
        model = Promocion
        fields = ['nombre', 'telefono', 'cantidad_divisa', 'botellas_pagadas']
        labels = {
            'nombre': 'Nombre del cliente',
            'telefono': 'Teléfono',
            'cantidad_divisa': 'Cantidad pagada ($)',
            'botellas_pagadas': 'Botellas pagadas',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': FORM_WIDGET_CLASS, 'placeholder': 'Nombre del cliente'}),
            'telefono': forms.TextInput(attrs={'class': FORM_WIDGET_CLASS, 'placeholder': 'Teléfono'}),
            'cantidad_divisa': forms.NumberInput(attrs={'step':'0.01','min':'0','class': FORM_WIDGET_CLASS, 'placeholder':'Cantidad en $'}),
            'botellas_pagadas': forms.NumberInput(attrs={'class': FORM_WIDGET_CLASS, 'placeholder':'Número de botellas','min':'0'}),
        }
