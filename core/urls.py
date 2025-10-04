# wtp_admin/urls.py (o tu archivo principal de URLs)

from django.contrib import admin
from django.urls import path

# ========================================================================
# NOTA PROFESIONAL: Si este es el archivo principal del proyecto, 
# las importaciones deben apuntar a la app (ej. 'core.views_main'). 
# He ajustado las importaciones asumiendo que tu app se llama 'core'.
# ========================================================================

from core.views_main import (
    login_view, 
    logout_view, 
    dashboard_view, 
    ventas_view, 
    cisternas_view, 
    control_manual_view, 
    deliveries_view,
    tasa_view,
    productos_view,
    eliminar_producto_view,
    about_us_view,
    exportar_ventas_a_excel
)
# Asumiendo que 'promos' es una subcarpeta dentro de la app 'core'
from core.views.promos import promos_view, registrar_promocion, restar_botella 

urlpatterns = [
    # URLs del Administrador de Django (Jazzmin)
    path('admin/', admin.site.urls),

    # =================================================
    # URLs de la aplicación principal (core)
    # =================================================

    # 1. URLs de Autenticación
    path('', login_view, name='login'), # Raíz del proyecto -> Login
    path('logout/', logout_view, name='logout'),

    # 2. URLs de Navegación principal
    path('dashboard/', dashboard_view, name='dashboard'),
    path('ventas/', ventas_view, name='ventas'),
    path('cisternas/', cisternas_view, name='cisternas'),
    path('control-manual/', control_manual_view, name='control_manual'),
    path('deliveries/', deliveries_view, name='deliveries'),
    path('acerca-de-nosotros/', about_us_view, name='about_us'),
    
    # 3. URLs de Gestión de Productos
    path('productos/', productos_view, name='productos'),
    path('productos/editar/<int:pk>/', productos_view, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', eliminar_producto_view, name='eliminar_producto'),

    # 4. URLs de Promociones
    path('promos/', promos_view, name='promos'),
    path('promos/registrar/', registrar_promocion, name='registrar_promocion'),
    # CORREGIDO: Se usa un nombre de URL válido ('restar_botella')
    path('promos/restar/<int:promo_id>/', restar_botella, name='restar_botella'), 

    # 5. URLs Misceláneas
    path('tasa/', tasa_view, name='tasa'), # Gestión de la tasa de cambio
    # Exportación (ubicada lógicamente bajo control-manual)
    path('control-manual/exportar/', exportar_ventas_a_excel, name='exportar_ventas_a_excel'), 
]