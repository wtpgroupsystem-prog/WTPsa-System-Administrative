from django.contrib import admin
from .models import User, Venta, Cisterna, Delivery, Promocion, TasaCambio, PagoVenta, Producto, ItemVenta, MetodoDePago

# ----------------- Inline classes for a cleaner admin interface -----------------

class ItemVentaInline(admin.TabularInline):
    """
    Permite editar los ítems de una venta directamente en la página de Venta.
    """
    model = ItemVenta
    extra = 0
    can_delete = False
    fields = ('producto', 'cantidad', 'subtotal_divisa', 'subtotal_bs')
    readonly_fields = ('subtotal_divisa', 'subtotal_bs')

class PagoVentaInline(admin.TabularInline):
    """
    Permite editar los pagos directamente en la página de Venta.
    """
    model = PagoVenta
    extra = 1

# ----------------- ModelAdmin classes for custom display -----------------

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'is_staff')

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fecha',
        'usuario',
        'total_venta_divisa',
        'total_venta_bs',
        'tasa_cambio_usada',
    )
    inlines = [ItemVentaInline, PagoVentaInline]
    list_filter = ('fecha', 'usuario')
    search_fields = ('usuario__username',)
    readonly_fields = ('total_venta_divisa', 'total_venta_bs', 'tasa_cambio_usada')
    fieldsets = (
        (None, {
            'fields': ('usuario',),
        }),
        ('Detalles de la Venta', {
            'fields': ('total_venta_divisa', 'total_venta_bs', 'tasa_cambio_usada'),
        }),
    )

@admin.register(Cisterna)
class CisternaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'volumen', 'litros_disponibles', 'usuario')

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('direccion', 'litros_entregados', 'fecha', 'hora', 'encargado')
    list_filter = ('fecha',)
    search_fields = ('direccion',)

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'botellas_pendientes', 'fecha_creacion')
    search_fields = ('nombre', 'telefono')
    
@admin.register(TasaCambio)
class TasaCambioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tasa_bsd', 'usuario')
    list_filter = ('fecha',)
    search_fields = ('tasa_bsd',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'precio_divisa', 'precio_bolivares')
    search_fields = ('codigo', 'nombre')
    list_filter = ('tipo',)

@admin.register(MetodoDePago)
class MetodoDePagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'es_bolivares')