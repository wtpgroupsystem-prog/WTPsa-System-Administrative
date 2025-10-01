from django.urls import path
from .views_main import (
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
from .views.promos import promos_view, registrar_promocion, restar_botella

urlpatterns = [
    # URLs de autenticación
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # URLs de la aplicación principal
    path('dashboard/', dashboard_view, name='dashboard'),
    path('ventas/', ventas_view, name='ventas'),
    path('cisternas/', cisternas_view, name='cisternas'),
    path('control-manual/', control_manual_view, name='control_manual'),
    path('deliveries/', deliveries_view, name='deliveries'),

     # URL para la página de "Acerca de Nosotros"
    path('acerca-de-nosotros/', about_us_view, name='about_us'),
    
    # Nueva URL para la exportación
    path('control-manual/exportar/', exportar_ventas_a_excel, name='exportar_ventas_a_excel'), 
    
    # URLs para promociones
    path('promos/', promos_view, name='promos'),
    path('promos/registrar/', registrar_promocion, name='registrar_promocion'),
    path('promos/restar/<int:promo_id>/', restar_botella, name='restar_<Abotella'),

    # URL para la gestión de la tasa de cambio
    path('tasa/', tasa_view, name='tasa'),

    # URLs para la gestión de productos (unificadas)
    path('productos/', productos_view, name='productos'),
    path('productos/editar/<int:pk>/', productos_view, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', eliminar_producto_view, name='eliminar_producto'),
]

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('admin/', admin.site.urls),
]