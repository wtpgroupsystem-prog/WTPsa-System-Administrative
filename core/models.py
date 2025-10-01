from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from decimal import Decimal

# Modelo de Usuario personalizado
class User(AbstractUser):
    ROLES = (
        ('trabajador', 'Trabajador'),
        ('encargada', 'Encargada de Deliveries'),
        ('dueno', 'Dueño'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='trabajador')

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

# Nuevo modelo para la tasa de cambio del día
class TasaCambio(models.Model):
    fecha = models.DateField(default=timezone.now, unique=True)
    tasa_bsd = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasas_cambio'
    )

    def __str__(self):
        return f"Tasa del {self.fecha}: {self.tasa_bsd} Bs/USD"

# Modelo de Cisterna con lógica de acumulación
class Cisterna(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    volumen = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Volumen de la cisterna en litros"
    )
    litros_disponibles = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Litros totales disponibles en la cisterna"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cisternas'
    )

    def __str__(self):
        return f"{self.fecha} - {self.hora} - {self.volumen} L"
        
# Modelo de Delivery
class Delivery(models.Model):
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    nombre_cliente = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    litros_entregados = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Litros entregados en el delivery"
    )
    encargado = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="deliveries",
        help_text="Usuario encargado del delivery"
    )

    def __str__(self):
        return f"Delivery – {self.direccion} ({self.litros_entregados} L) at {self.fecha}"

# Modelo para unificar todos los productos/servicios
class Producto(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    precio_divisa = models.DecimalField(max_digits=10, decimal_places=2)
    precio_bolivares = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00')) 
    stock = models.IntegerField(default=0)
    TIPO_CHOICES = [
        ('articulos_extra', 'Articulos extra'),
        ('agua_litros', 'Agua por Litros'),
        ('botella_20l', 'Botella 20L'),
        ('botella_10l', 'Botella 10L'),
        ('botella_5l', 'Botella 5L'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='agua_litros')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

# Modelo para registrar una venta, ahora más genérico
class Venta(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Usuario que registra la venta",
        related_name='ventas'
    )
    fecha = models.DateTimeField(default=timezone.now)
    total_venta_divisa = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_venta_bs = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tasa_cambio_usada = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    # Se agrega este campo para corregir el error
    tipo_venta = models.CharField(max_length=20, default='Normal')
    
    def __str__(self):
        return f"Venta #{self.pk} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

# Modelo para los ítems individuales de una venta
class ItemVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='items_vendidos')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal_divisa = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal_bs = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

# Modelo para los métodos de pago, para evitar listas fijas
class MetodoDePago(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    es_bolivares = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nombre

# Modelo para registrar cada pago individual de una venta
class PagoVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='pagos')
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.ForeignKey(MetodoDePago, on_delete=models.PROTECT, related_name='pagos_recibidos')
    
    def __str__(self):
        return f"Pago de {self.monto_recibido} con {self.metodo_pago.nombre}"

# Modelo de Promoción
class Promocion(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    cantidad_divisa = models.DecimalField(max_digits=10, decimal_places=2)
    botellas_pagadas = models.PositiveIntegerField(default=0)
    botellas_retiradas = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='promociones'
    )

    @property
    def botellas_pendientes(self):
        return self.botellas_pagadas - self.botellas_retiradas

    def __str__(self):
        return f"{self.nombre} ({self.botellas_pendientes} pendientes)"
