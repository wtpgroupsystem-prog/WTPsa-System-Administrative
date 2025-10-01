from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.http import JsonResponse #
from django.db.models import Sum, F, Value, DecimalField
from django.db.models.functions import TruncDay
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta, date
import json
from decimal import Decimal
from django.http import HttpResponse # Necesaria para la respuesta de archivo
import csv

# Importa los modelos y formularios
from .models import (
    Venta, Cisterna, Delivery, Promocion, PagoVenta, TasaCambio,
    Producto, ItemVenta, MetodoDePago
)
from .forms import VentaForm, CisternaForm, TasaCambioForm, ProductoForm, DeliveryForm

User = get_user_model()

# ---------------------- LOGIN / LOGOUT ----------------------
def login_view(request):
    """
    Gestiona el inicio de sesión de los usuarios.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, '¡Bienvenido!')
            return redirect('dashboard')
        messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'login.html')

def logout_view(request):
    """
    Cierra la sesión del usuario actual.
    """
    logout(request)
    messages.info(request, 'Has cerrado la sesión exitosamente.')
    return redirect('login')

# ---------------------- DASHBOARD ----------------------
@login_required
def dashboard_view(request):
    """
    Muestra el panel de control con estadísticas clave del día.
    """
    hoy = timezone.now().date()
    
    try:
        litros_disponibles = Cisterna.objects.latest('fecha', 'hora').litros_disponibles
    except Cisterna.DoesNotExist:
        litros_disponibles = Decimal('0.00')

    # Litros vendidos hoy, filtrando por el producto de "Agua por Litros"
    ventas_hoy = Venta.objects.filter(fecha__date=hoy)
    litros_vendidos_hoy_q = ItemVenta.objects.filter(
        venta__in=ventas_hoy,
        producto__tipo='agua_litros'
    ).aggregate(total=Sum('cantidad'))['total'] or Decimal('0.00')

    # Suma total recaudada por método de pago
    pagos_del_dia = PagoVenta.objects.filter(venta__in=ventas_hoy)
    total_recaudado_divisa = pagos_del_dia.filter(metodo_pago__es_bolivares=False).aggregate(total=Sum('monto_recibido'))['total'] or Decimal('0.00')
    total_recaudado_bs = pagos_del_dia.filter(metodo_pago__es_bolivares=True).aggregate(total=Sum('monto_recibido'))['total'] or Decimal('0.00')
    
    # Desglose de pagos
    total_divisa = pagos_del_dia.filter(metodo_pago__nombre='Divisa $').aggregate(total=Sum('monto_recibido'))['total'] or Decimal('0.00')
    total_bs_efectivo = pagos_del_dia.filter(metodo_pago__nombre='Efectivo BsD').aggregate(total=Sum('monto_recibido'))['total'] or Decimal('0.00')
    total_pago_movil = pagos_del_dia.filter(metodo_pago__nombre='Pago Móvil').aggregate(total=Sum('monto_recibido'))['total'] or Decimal('0.00')
    total_transferencia = pagos_del_dia.filter(metodo_pago__nombre='Transferencia').aggregate(total=Sum('monto_recibido'))['total'] or Decimal('0.00')
    total_debito = pagos_del_dia.filter(metodo_pago__nombre='Tarjeta de Débito BsD').aggregate(total=Sum('monto_recibido'))['total'] or Decimal('0.00')
    total_credito = pagos_del_dia.filter(metodo_pago__nombre='Tarjeta de Crédito BsD').aggregate(total=Sum('monto_recibido'))['total'] or Decimal('0.00')

    ultimos_7_dias = [hoy - timedelta(days=i) for i in range(6, -1, -1)]
    ventas_dia_labels = [dia.strftime('%d/%m') for dia in ultimos_7_dias]
    ventas_dia_data = [
        float(ItemVenta.objects.filter(
            venta__fecha__date=dia,
            producto__tipo='agua_litros'
        ).aggregate(total=Sum('cantidad'))['total'] or 0)
        for dia in ultimos_7_dias
    ]

    context = {
        'litros_disponibles': litros_disponibles,
        'litros_vendidos_hoy': litros_vendidos_hoy_q,
        'ventas_dia_labels': json.dumps(ventas_dia_labels),
        'ventas_dia_data': json.dumps(ventas_dia_data),
        'total_recaudado_divisa': total_recaudado_divisa,
        'total_recaudado_bs': total_recaudado_bs,
        'total_divisa': total_divisa,
        'total_bs_efectivo': total_bs_efectivo,
        'total_pago_movil': total_pago_movil,
        'total_transferencia': total_transferencia,
        'total_debito': total_debito,
        'total_credito': total_credito,
    }
    return render(request, 'dashboard.html', context)

# ---------------------- GESTIÓN DE PRODUCTOS ----------------------
@login_required
def productos_view(request, pk=None):
    """
    Vista unificada para listar, crear y editar productos.
    Si se proporciona un 'pk', se trata de una edición. De lo contrario, es una creación o lista.
    """
    producto_a_editar = None
    if pk:
        producto_a_editar = get_object_or_404(Producto, pk=pk)
        form = ProductoForm(request.POST or None, instance=producto_a_editar)
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('productos')
    else:
        form = ProductoForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('productos')

    productos = Producto.objects.all().order_by('nombre')
    context = {
        'productos': productos,
        'form': form,
        'producto_a_editar': producto_a_editar
    }
    return render(request, 'core/productos.html', context)

@login_required
def eliminar_producto_view(request, pk):
    """
    Elimina un producto existente.
    """
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('productos')
    return redirect('productos') # Siempre redirigir a la lista de productos


# ---------------------- VENTAS ----------------------
@login_required
@transaction.atomic
def ventas_view(request):
    """
    Vista para la página de punto de venta.
    Maneja el registro de ventas y la lógica de negocio asociada.
    """
    
    # --- Lógica de la Solicitud POST para registrar la venta ---
    if request.method == 'POST':
        try:
            # 1. Obtener y parsear los datos JSON del frontend
            items_data = json.loads(request.POST.get('items', '[]'))
            pagos_data = json.loads(request.POST.get('pagos', '[]'))
            
            # Validar que al menos haya un producto y un pago en la venta
            if not items_data:
                messages.error(request, "No se puede registrar una venta sin productos.")
                return redirect('ventas')
            if not pagos_data:
                messages.error(request, "No se puede registrar una venta sin pagos.")
                return redirect('ventas')
            
            # 2. Obtener la tasa de cambio actual desde la base de datos
            try:
                tasa_cambio_obj = TasaCambio.objects.latest('fecha')
                tasa_actual = tasa_cambio_obj.tasa_bsd
            except TasaCambio.DoesNotExist:
                messages.error(request, "No hay una tasa de cambio registrada para hoy. Por favor, regístrela primero.")
                return redirect('ventas')

            # 3. Calcular el total de la venta y verificar el stock de agua
            total_venta_divisa = Decimal('0.00')
            cantidad_litros = Decimal('0.00')
            productos_en_venta = {}
            for item in items_data:
                codigo = item['codigo']
                # Convertir a Decimal con cuidado para evitar errores de precisión
                cantidad = Decimal(str(item['cantidad']))
                
                # Obtener el producto o mostrar un error si no se encuentra
                producto = get_object_or_404(Producto, codigo=codigo)
                productos_en_venta[codigo] = producto
                
                subtotal_divisa = producto.precio_divisa * cantidad
                total_venta_divisa += subtotal_divisa
                
                if producto.tipo == 'agua_litros':
                    cantidad_litros += cantidad

            if cantidad_litros > 0:
                try:
                    cisterna_actual = Cisterna.objects.latest('fecha', 'hora')
                except Cisterna.DoesNotExist:
                    messages.error(request, "No hay una cisterna registrada. Contacte al administrador.")
                    return redirect('ventas')
                if cisterna_actual.litros_disponibles < cantidad_litros:
                    messages.error(request, f"No hay suficientes litros de agua en la cisterna. Solo quedan {cisterna_actual.litros_disponibles}L.")
                    return redirect('ventas')
            
            # 4. Validar que el monto total de los pagos coincida con el total de la venta
            total_pagado_divisa = Decimal('0.00')
            for pago in pagos_data:
                # Convertir a Decimal con cuidado para evitar errores de precisión
                monto = Decimal(str(pago['monto']))
                metodo_nombre = pago['metodo_pago']
                # Obtener el método de pago por nombre
                metodo_pago = get_object_or_404(MetodoDePago, nombre=metodo_nombre)
                
                if metodo_pago.es_bolivares:
                    total_pagado_divisa += monto / tasa_actual
                else:
                    total_pagado_divisa += monto

            # Se usa una tolerancia de 0.01 para evitar problemas de precisión con los decimales.
            if abs(total_venta_divisa - total_pagado_divisa) > Decimal('0.01'):
                saldo_pendiente = (total_venta_divisa - total_pagado_divisa).quantize(Decimal('0.01'))
                messages.error(request, f"El monto total de los pagos no coincide con el total de la venta. Saldo pendiente: ${saldo_pendiente}")
                return redirect('ventas')
            
            # 5. Guardar la venta y sus ítems
            venta = Venta.objects.create(
                usuario=request.user,
                total_venta_divisa=total_venta_divisa,
                total_venta_bs=total_venta_divisa * tasa_actual,
                tasa_cambio_usada=tasa_actual
            )
            for item in items_data:
                codigo = item['codigo']
                cantidad = Decimal(str(item['cantidad']))
                producto = productos_en_venta[codigo]
                subtotal_divisa = producto.precio_divisa * cantidad
                subtotal_bs = subtotal_divisa * tasa_actual
                
                ItemVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    subtotal_divisa=subtotal_divisa,
                    subtotal_bs=subtotal_bs
                )
            
            # 6. Guardar los pagos asociados a la venta
            for pago in pagos_data:
                PagoVenta.objects.create(
                    venta=venta,
                    monto_recibido=pago['monto'],
                    metodo_pago=get_object_or_404(MetodoDePago, nombre=pago['metodo_pago'])
                )
            
            # 7. Descontar litros de la cisterna si aplica
            if cantidad_litros > 0:
                cisterna_actual.litros_disponibles = F('litros_disponibles') - cantidad_litros
                cisterna_actual.save(update_fields=['litros_disponibles'])
            
            messages.success(request, "Venta registrada correctamente.")
            return redirect('ventas')
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            messages.error(request, f"Error en los datos enviados. Por favor, intente de nuevo. Detalle: {e}")
            return redirect('ventas')
            
    # --- Lógica de la Solicitud GET para cargar la página de ventas ---
    
    # Obtener la lista de productos
    productos_qs = Producto.objects.all().values('id', 'codigo', 'nombre', 'precio_divisa', 'precio_bolivares', 'tipo')
    productos_list = []
    for p in productos_qs:
        p['precio_divisa'] = str(p['precio_divisa'])
        p['precio_bolivares'] = str(p['precio_bolivares'])
        productos_list.append(p)

    # Crear métodos de pago por defecto si no existen, de forma segura
    metodos_defecto = [
        ("Tarjeta de Débito BsD", True),
        ("Tarjeta de Crédito BsD", True),
        ("Efectivo BsD", True),
        ("Divisa $", False),
        ("Transferencia", True),
        ("Pago Móvil", True),
    ]
    for nombre, es_bolivares in metodos_defecto:
        MetodoDePago.objects.get_or_create(nombre=nombre, defaults={'es_bolivares': es_bolivares})
    
    # Obtener la lista de métodos de pago
    metodos_pago = list(MetodoDePago.objects.all().values('id', 'nombre', 'es_bolivares'))
    
    # Obtener la tasa de cambio actual
    try:
        tasa_actual = TasaCambio.objects.latest('fecha').tasa_bsd
    except TasaCambio.DoesNotExist:
        messages.warning(request, "No hay una tasa de cambio registrada. Usando una tasa predeterminada de 1.00.")
        tasa_actual = Decimal('1.00')

    # Obtener las ventas del día para el resumen
    ventas_hoy = Venta.objects.filter(fecha__date=timezone.now().date())
    
    # ✅ CORRECCIÓN DE KEYERROR: Se usa 'total' como clave, ya que fue el nombre dado en aggregate()
    total_divisas_hoy = ventas_hoy.aggregate(total=Sum('total_venta_divisa'))['total'] or Decimal('0.00')
    total_bs_hoy = ventas_hoy.aggregate(total=Sum('total_venta_bs'))['total'] or Decimal('0.00')

    # ✅ CORRECCIÓN DE PYLANCE: Definir 'current_time_stamp' para evitar el error "is not defined"
    current_time_stamp = timezone.now().timestamp()
    
    context = {
        'productos': json.dumps(productos_list),
        'metodos_pago': json.dumps(metodos_pago),
        'tasa_actual': json.dumps(str(tasa_actual)),
        'ventas_hoy': ventas_hoy,
        'total_divisas_hoy': total_divisas_hoy,
        'total_bs_hoy': total_bs_hoy,
        # ✅ Pasar la variable al contexto
        'current_time_stamp': current_time_stamp,
    }

    return render(request, 'core/ventas.html', context)


# ---------------------- CISTERNAS ----------------------
@login_required
def cisternas_view(request):
    """
    Gestiona el registro de la entrada de agua a la cisterna.
    """
    if request.method == 'POST':
        form = CisternaForm(request.POST)
        if form.is_valid():
            cisterna = form.save(commit=False)
            cisterna.usuario = request.user
            
            try:
                # Obtener la última cisterna para sumar el nuevo volumen
                ultima_cisterna = Cisterna.objects.latest('fecha', 'hora')
                cisterna.litros_disponibles = ultima_cisterna.litros_disponibles + cisterna.volumen
            except Cisterna.DoesNotExist:
                # Si no hay cisternas, el volumen es el total disponible
                cisterna.litros_disponibles = cisterna.volumen
            
            cisterna.save()
            messages.success(request, "Cisterna registrada correctamente.")
            return redirect('cisternas')
    else:
        form = CisternaForm()
        
    cisternas = Cisterna.objects.all().order_by('-fecha', '-hora')
    return render(request, 'core/cisternas.html', {'form': form, 'cisternas': cisternas})

# ---------------------- DELIVERIES ----------------------
@login_required
def deliveries_view(request):
    """
    Registra y muestra los detalles de los deliveries.
    """
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.encargado = request.user
            delivery.save()
            messages.success(request, "Delivery registrado correctamente.")
            return redirect('deliveries')
    else:
        form = DeliveryForm()
        
    deliveries = Delivery.objects.all().order_by('-fecha')
    return render(request, 'deliveries.html', {'form': form, 'deliveries': deliveries})

# ---------------------- GESTIÓN DE TASAS DE CAMBIO ----------------------
@login_required
def tasa_view(request):
    """
    Gestiona la creación y actualización de la tasa de cambio diaria.
    """
    if request.method == 'POST':
        form = TasaCambioForm(request.POST)
        if form.is_valid():
            try:
                tasa = form.save(commit=False)
                tasa.usuario = request.user
                tasa.save()
                messages.success(request, "Tasa de cambio actualizada con éxito.")
                return redirect('tasa')
            except IntegrityError:
                messages.error(request, "Ya existe una tasa de cambio registrada para el día de hoy.")
    else:
        try:
            tasa_actual = TasaCambio.objects.get(fecha=date.today())
            form = TasaCambioForm(instance=tasa_actual)
        except TasaCambio.DoesNotExist:
            form = TasaCambioForm()

    context = {
        'form': form,
        'tasas': TasaCambio.objects.all().order_by('-fecha')[:10]
    }
    return render(request, 'core/tasa_cambio.html', context)

# ---------------------- CONTROL MANUAL ----------------------

def get_date_range_from_request(request):
    """Calcula el rango de fechas basado en los parámetros de la solicitud."""
    hoy = timezone.localdate()
    rango = request.GET.get('rango', 'semanal')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # 1. Rango predefinido
    if rango == 'semanal':
        start_date = hoy - timedelta(days=6)
        end_date = hoy
    elif rango == 'mensual':
        start_date = hoy.replace(day=1)
        end_date = hoy
    elif rango == 'anual':
        start_date = hoy.replace(month=1, day=1)
        end_date = hoy
    elif rango == 'personalizado' and fecha_inicio and fecha_fin:
        # 2. Rango personalizado
        try:
            start_date = timezone.datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de fecha inválido. Usando rango semanal por defecto.")
            return get_date_range_from_request(request) # Recalcula con el valor por defecto
    else:
        # Por defecto, semanal
        start_date = hoy - timedelta(days=6)
        end_date = hoy
        rango = 'semanal'
        
    # El filtro de Venta.fecha debe ser >= start_date y < end_date + 1 día
    # para incluir el día completo de la fecha final.
    return start_date, end_date, rango
@login_required
def control_manual_view(request):
    """
    Vista para la página de control manual de ventas, con filtrado y comparación.
    """
    
    start_date, end_date, rango_seleccionado = get_date_range_from_request(request)
    
    # Asegurarse de que el rango sea válido
    if start_date > end_date:
        messages.error(request, "La fecha de inicio no puede ser posterior a la fecha de fin.")
        # Usar el rango semanal por defecto en caso de error
        start_date, end_date, rango_seleccionado = get_date_range_from_request({'GET': {'rango': 'semanal'}})

    # 1. Obtener los datos de ventas en el rango
    ventas_en_rango = Venta.objects.filter(
        fecha__date__gte=start_date,
        fecha__date__lte=end_date
    )

    # 2. Ventas Agrupadas por Día (para el gráfico de evolución)
    ventas_por_dia = ventas_en_rango.annotate(
        dia=TruncDay('fecha')
    ).values('dia').annotate(
        total_diario=Sum('total_venta_divisa')
    ).order_by('dia')

    # --- INICIO DE LA CORRECCIÓN CRÍTICA PARA GRÁFICO ---
    # 2.1. Mapear los datos existentes a un diccionario {fecha_str: total}
    # Aseguramos que los valores sean float para JS
    data_map = {item['dia'].strftime('%Y-%m-%d'): float(item['total_diario']) for item in ventas_por_dia}
    
    # 2.2. Generar etiquetas y datos para CADA DÍA del rango (rellenando vacíos)
    fechas_labels = []
    totales_data = []
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        fechas_labels.append(date_str)
        # Rellena con el valor de la BD o 0.0 si no hay ventas ese día
        totales_data.append(data_map.get(date_str, 0.0)) 
        current_date += timedelta(days=1)
    # --- FIN DE LA CORRECCIÓN CRÍTICA ---


    # 3. Totales Recaudados (Sumarios)
    total_ventas_divisa = ventas_en_rango.aggregate(Sum('total_venta_divisa'))['total_venta_divisa__sum'] or Decimal('0.00')
    total_ventas_bs = ventas_en_rango.aggregate(Sum('total_venta_bs'))['total_venta_bs__sum'] or Decimal('0.00')

    # 4. Desglose de Recaudación por Método de Pago
    pagos_en_rango = PagoVenta.objects.filter(venta__in=ventas_en_rango)
    recaudacion_por_metodo = pagos_en_rango.values('metodo_pago__nombre').annotate(
        total_monto=Sum('monto_recibido')
    ).order_by('-total_monto')
    
    # 5. Calcular el total de litros vendidos
    litros_vendidos = ItemVenta.objects.filter(
        venta__in=ventas_en_rango,
        producto__tipo='agua_litros'
    ).aggregate(total_litros=Sum('cantidad'))['total_litros'] or Decimal('0.00')

    # Preparar contexto
    context = {
        'start_date_str': start_date.strftime('%Y-%m-%d'),
        'end_date_str': end_date.strftime('%Y-%m-%d'),
        'rango_seleccionado': rango_seleccionado,
        'total_ventas_divisa': total_ventas_divisa,
        'total_ventas_bs': total_ventas_bs,
        'litros_vendidos': litros_vendidos,
        'recaudacion_por_metodo': recaudacion_por_metodo,
        
        # Datos para Chart.js (¡Serializados con json.dumps!)
        'fechas_labels': json.dumps(fechas_labels),
        'totales_data': json.dumps(totales_data),
        
        # Datos para el gráfico de métodos de pago 
        'metodos_labels': json.dumps([r['metodo_pago__nombre'] for r in recaudacion_por_metodo]),
        'metodos_data': json.dumps([float(r['total_monto']) for r in recaudacion_por_metodo]),
    }
    
    return render(request, 'core/control_manual.html', context)

#CONTROL MANUAL 

@login_required
def exportar_ventas_a_excel(request):
    """
    Función para exportar los datos de ventas filtrados a un archivo CSV.
    """
    start_date, end_date, _ = get_date_range_from_request(request)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{start_date}_{end_date}.csv"'

    writer = csv.writer(response)
    
    # Encabezados del archivo CSV
    writer.writerow([
        'ID Venta', 'Fecha', 'Usuario', 'Total $', 'Total Bs', 
        'Tasa Cambio', 'Producto', 'Cantidad', 'Subtotal $'
    ])

    # Obtener todas las ventas y sus items en el rango
    items_vendidos = ItemVenta.objects.select_related('venta', 'producto', 'venta__usuario').filter(
        venta__fecha__date__gte=start_date,
        venta__fecha__date__lte=end_date
    ).order_by('venta__fecha')

    # Escribir los datos
    for item in items_vendidos:
        venta = item.venta
        writer.writerow([
            venta.id,
            venta.fecha.strftime('%Y-%m-%d %H:%M'),
            venta.usuario.username,
            venta.total_venta_divisa,
            venta.total_venta_bs,
            venta.tasa_cambio_usada,
            item.producto.nombre,
            item.cantidad,
            item.subtotal_divisa,
        ])

    return response

# ABOUT US
def about_us_view(request):
    """
    Renders the 'About Us' page.
    """
    return render(request, 'about_us.html')
