from django.contrib import admin
from inventariohonducorapp.models import tb_Articulo, tb_DetalleArticulo, tb_categoria_art, tb_entrada, \
    tb_CategoriaMobiliario, tb_Mobiliario, tb_Empleado, Agencia, tb_Municipio, tb_Departamento, tb_Jefatura, \
    tb_MobiliarioPrestado, tb_salida, tb_MobiliarioDevuelto, tb_incidenciaArticulo, tb_Vehiculo, tb_VehiculoAsignado, \
    tb_Inmueble, tb_estado, tb_clasificacion_estados,tb_Admin_Inmueble, tb_proveedor

# from django.contrib.auth.models import User

# Register your models here.
admin.site.register(tb_Empleado)

admin.site.register(tb_Articulo)
admin.site.register(tb_DetalleArticulo)
admin.site.register(tb_incidenciaArticulo)
admin.site.register(tb_categoria_art)
admin.site.register(tb_entrada)
admin.site.register(tb_CategoriaMobiliario)

admin.site.register(Agencia)
admin.site.register(tb_Municipio)
admin.site.register(tb_Departamento)
admin.site.register(tb_Jefatura)
# referente a mobiliario
admin.site.register(tb_Mobiliario)
admin.site.register(tb_MobiliarioPrestado)
admin.site.register(tb_MobiliarioDevuelto)

# registro de la seccion de salidas
admin.site.register(tb_salida)

# registros de vehiculso

admin.site.register(tb_Vehiculo)
admin.site.register(tb_VehiculoAsignado)
admin.site.register(tb_proveedor)

# registros de inmuebles
admin.site.register(tb_Inmueble)
admin.site.register(tb_Admin_Inmueble)
# todos lo que tiene que ver con el panel de control
admin.site.site_header = 'PANEL DE CONTROL INVENTARIO'
admin.site.site_title = "INVENTARIO"
admin.site.index_title = "HONDUCOR"

admin.site.register(tb_estado)
admin.site.register(tb_clasificacion_estados)
