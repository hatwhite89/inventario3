"""InventarioHONDUCOR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from inventariohonducorapp import views
from InventarioHONDUCOR import settings
from django.contrib.auth.views import login
from  inventariohonducorapp.pdf import Print_PDF, PDFSalida, PDFEnregaMobiliario, PDF_Bitacora_Salida, \
    PDF_Bitacora_Salida2, PDF_Bitacora_Mobiliario, PDF_Bitacora_Vehiculo, PDF_Bitacora_Inmueble, PDF_Bitacora_Login, \
    PDF_entradas, PDF_entradas_fecha, PDF_salidas, PDF_salidas_fecha,PDF_Total_Existencias
from django.contrib.auth.views import logout_then_login

from inventariohonducorapp.pie import PieChart02
from inventariohonducorapp.excel import export_entrada_excel, export_salida_excel, export_articulo_excel, \
    export_vehiculo_excel, export_entrada_fechas_excel, export_salida_fecha_excel, export_mobiliario_agencia_excel, \
    export_bitacora_detalle_art_excel, export_bitacora_entrada_excel, export_bitacora_mobiliario_excel, \
    export_bitacora_salida_excel, export_bitacora_vehiculo_excel, export_bitacora_mobiliario_fecha_excel, \
    export_bitacora_vehiculo_fecha_excel, export_bitacora_entrada_fecha_excel, export_bitacora_salida_fecha_excel, \
    export_inmueble_excel, export_bitacora_login_excel

from inventariohonducorapp.views import main, Personas, VerEntradas, BuscarMobiliario, VerSalidas, BuscarMobiliario2, \
    BuscarEmpleado, BuscarMobiliarioPrestado, BuscarEmpleadoMP, VerExistenciasArticulos, VerExistenciasArticulosDet

urlpatterns = [
    # URL para el sitio de panel de administracion
    url(r'^admin/', admin.site.urls),
    # esta URL es para redireccionar al login y realizar todos los procesos de autenticacion
    url(r'^$', login, {'template_name': 'Inventario/login.html'}, name='login'),
    # Esta url redireccion al index del sitio
    url(r'^main/$', views.main, name="main"),
    # esta url redirecciona al calendario
    url(r'^calendario/$', views.Calendario, name="calendario"),
    # esta URL es usada luego de cualquier validacion exitosa de los formularios
    url(r'^add_post/$', main, name="add_post"),
    # Esta URL cierra sesion
    url(r'^cerrar/$', logout_then_login, name='logout'),
    url(r'^graficos/$', views.graficos, name='graficos'),
    url(r'^graficos2/$', views.grafico_agencia, name='graficos2'),
    url(r'^graficoMobiliario/$', views.graficosMobiliario, name='graficosMobiliario'),
    url(r'^graficoMobiliario2/$', views.grafico_mobiliario_agencia, name='graficosMobiliario2'),
    url(r'^graficoVehiculo/$', views.graficosVehiculo, name='graficoVehiculo'),
    # ======================================== URL DE ARTICULOS =============================

    # Esta URL sirve para registrar una nueva entrada, recibe el parametro pk
    url(r'^nuevoDetalleArticulo/', views.nuevoDetalleArticulo, name='nuevoDetalleArticulo'),
    url(r'^nuevoArticulo/$', views.nuevoArticulo, name='nuevoArticulo'),
    url(r'^buscarArticulo/', login_required(Personas.as_view()), name="personas"),
    url(r'^buscarSoloArticulos/', login_required(views.BuscarAticulosSolamente.as_view()), name="buscarSoloArticulos"),
    # lista los incidentes de los articulos
    url(r'^listarIncidenteArticulo2/', login_required(views.ListarIncidenteArticulo2.as_view()),
        name="listarIncidenteArticulo2"),
    url(r'^buscarArticuloDet/', login_required(VerExistenciasArticulosDet.as_view()), name="verExistenciasDet"),
    # VER EXISTENCIA DE ARTICULOS
    url(r'^verExistencias/', login_required(VerExistenciasArticulos.as_view()), name="verExistencias"),
    # VER ARTICULOS SIN EXISTENCIA
    url(r'^verNoExistencias/', login_required(views.VerSinExistenciasArticulos.as_view()), name="verNoExistencias"),
    #
    url(r'^nuevoDetalleArticuloLista/', login_required(views.VerArticulosEntradas.as_view()),
        name="nuevoDetalleArticuloLista"),
    url(r'^listarArticulosIncidencias/$', login_required(views.ListaArticulosIncidentias.as_view()),
        name="listarArticulosIncidencias"),
    url(r'^modificarArticulo/$', login_required(views.ModificarArticulo.as_view()),
        name="modificarArticulo"),
    # DAR BAJA ARTICULO
    url(r'^bajaArticulo/$', login_required(views.ListarDarBajaArticulo.as_view()),
        name="bajaArticulo"),
    url(r'^bajaArticulo2/$', views.DarBajaArticulo, name="bajaArticulo2"),

    url(r'^modificarArticulo2/$', views.ModificarArticulo2, name="modificarArticulo2"),
    # esta URL es para registrar nueva incidencia, redirecciona a registrar_incidencia.html
    url(r'^nuevaIncidenciaArt/$', views.nuevaIncidenciaArticulo, name='nuevaIncidenciaArt'),
    # ALERTA DE EXISTENCIAS
    url(r'^alerta/$', login_required(views.AlertaExistencias.as_view()),
        name="alerta"),
    # ===========================  URL DE ENTRADAS =====================================
    # ENTRADAS QUE SE VAN A MODIFICAR
    url(r'^verEntradaModificar/', login_required(views.VerEntradasModificar.as_view()), name="verEntradaModificar"),
    url(r'^verEntrada/', login_required(VerEntradas.as_view()), name="entradas"),
    # url de entradas_fecha.html
    url(r'^verEntradaFecha/', login_required(views.VerEntradaFecha.as_view()), name="verEntradaFecha"),
    url(r'^modificarEntradas2/', views.ModificarEntrada2, name="modificarEntradas2"),

    # ======================== URL DE SALIDAS ===============================
    url(r'^nuevaSalida/', views.nuevaSalida, name="nuevaSalida"),
    url(r'^verSalidas/', login_required(VerSalidas.as_view()), name="verSalidas"),
    # url de salidas_fecha.html
    url(r'^verSalidaFecha/', login_required(views.VerSalidaFecha.as_view()), name="verSalidaFecha"),

    # ==================  URL DE MOBILIARIO  ========================
    url(r'^nuevoMobiliario/', views.nuevoMobiliario, name="nuevoMobiliario"),
    url(r'^asignarMobiliario/', views.asignarMobiliario, name="asignarMobiliario"),
    url(r'^descargarMobiliario/', views.descargarMobiliario, name="descargarMobiliario"),
    url(r'^buscarMobiliario/', login_required(BuscarMobiliario.as_view()), name="buscarMobiliario"),
    url(r'^BuscarMobiliarioPrestado/', login_required(BuscarMobiliarioPrestado.as_view()),
        name="BuscarMobiliarioPrestado"),
    url(r'^buscarMobiliarioIndex/', login_required(views.BuscarMobiliarioIndex.as_view()),
        name="buscarMobiliarioIndex"),
    # esta url direcciona hacia buscar_mobiliario2.html es la que asgina el mobiliario
    url(r'^buscarMobiliario2/', login_required(BuscarMobiliario2.as_view()), name="buscarMobiliario2"),
    url(r'^agenciaMobiliario/', login_required(views.ListarAgenciasMobiliario.as_view()),
        name="agenciaMobiliario"),
    url(r'^inventarioMobiliarioAgencia', login_required(views.ListarAgenciasMobiliario2.as_view()),
        name="inventarioMobiliarioAgencia"),
    # listar_mobiliario_modificar
    url(r'^modificarMobiliario/', login_required(views.ListarModificarMobiliario.as_view()),
        name="modificarMobiliario"),
    url(r'^modificarMobiliario2/', views.ModificarMobiliario2,
        name="modificarMobiliario2"),
    # empleado para detalle mobiliario
    url(r'^empleadoMobiliario10/', login_required(views.BuscarEmpleado10.as_view()),
        name="empleadoMobiliario10"),
    # mobiliario detalle
    url(r'^asignarMobiliario11/', login_required(views.MobiliarioDetalle11.as_view()),
        name="asignarMobiliario11"),
    url(r'^bajaMobiliario/', login_required(views.ListarMobiliarioDarDeBaja.as_view()),
        name="bajaMobiliario"),
    url(r'^bajaMobiliario2/', views.DarBajaMobiliario,
        name="bajaMobiliario2"),
    # LISTAR MOBILIARIO SOLO
    url(r'^mobiliarioSolo/', login_required(views.ListarMobiliarioPrestadoSolo.as_view()),
        name="mobiliarioSolo"),
    # ======================   URL DE EMPLEADOS  ===============================
    # esta url direccion a buscar_empleado_mobiliario.html es para asignar mobiliaro
    url(r'^verEmpleado/', login_required(BuscarEmpleado.as_view()), name="verEmpleado"),
    url(r'^verEmpleado2/', login_required(BuscarEmpleadoMP.as_view()), name="verEmpleado2"),

    # =========== OTRAS URL
    # trabajar se puede borrar
    url(r'^verExistenciasPDF/', login_required(views.VerExistenciasArticulosPDF.as_view()), name="verExistenciasPDF"),
    # esta url de abajo es la que toma un parametro por url y se lo envia a la vista que se hace referencia para hacer un filtrado despues
    url(r'^ancillaries/(?P<pk>\d+)/',
        login_required(views.AncillaryDetail.as_view(template_name='inventario/buscar_articulo_detalle.html')),
        name="ancillary_detail"),
    url(r'^verlista/', login_required(views.pruebaListview.as_view()), name="verlista"),

    # ============================= URL DE VEHICULOS===========================
    url(r'^nuevoVehiculo/', views.nuevoVehiculo, name="nuevoVehiculo"),
    # ESTA URL ES PARA LISTAR LOS VEHICULOS ANTES DE ASIGNAR REDIRECCIONA HACIA  listar_vehiculos_asignar.html
    url(r'^asignarVehiculo/', login_required(views.ListarVehiculosAsignar.as_view()), name="asignarVehiculo"),
    # ESTA URL ES PARA LISTAR LOS EMPLEADOS ANTES DE ASIGNAR un vehiculo REDIRECCIONA HACIA  asignar_vehiculo_empleado.html
    url(r'^asignarVehiculo2/', login_required(views.ListarEmpleadosAsignarVehi.as_view()), name="asignarVehiculo2"),
    # URL  para descargar el vehiculo
    url(r'^descargarVehiculo/$', login_required(views.ListarVehiculosDescargar.as_view()), name="descargarVehiculo"),
    # URL DESCARGAR VEHICULO
    url(r'^descargarVehiculo2/$', views.descargarVehiculo, name='descargarVehiculo'),

    # esa url es paras asignar un nuevo vehiculo
    url(r'^asigVehiculo/$', views.asignarVehiculo, name='asigVehiculo'),
    # Lista todos los vehiculos
    url(r'^listarVehiculosIndex/$', login_required(views.ListarVehiculos.as_view()), name="listarVehiculosIndex"),
    # esta url es para listar los articulos de las incidencias, redirecciona a ver_det_incidencias.html

    # url listar_vehiculos_modificar ES PARA MODIFICAR VEHICULOS
    url(r'^modificarVehiculo/$', login_required(views.ListarVehiculosModificar.as_view()), name="modificarVehiculo"),
    # VEHICULOS QUE SERAN DADOS DE BAJA
    url(r'^bajaVehiculo/$', login_required(views.ListarVehiculosDarBaja.as_view()), name="bajaVehiculo"),
    url(r'^bajaVehiculo2/$', views.DarBajaVehiculo, name="bajaVehiculo2"),
    # url que ya realiza las modificaciones en los vehiculos
    url(r'^modificarVehiculo2/$', views.ModificarVehiculo2, name="modificarVehiculo2"),

    # ====================     PARA HACER REPORTES EN PDF ========================================
    url(r'^reporte_existencias_pdf/$', login_required(views.ReportePersonasPDF.as_view()), name="reporte_personas_pdf"),

    url(r'^reporte_mobiliario_pdf/$', login_required(views.ReporteMobiliarioPDF.as_view()),
        name="reporte_mobiliario_pdf"),

    url(r'^reporte_articulos_detalle_pdf/$', Print_PDF, name="reporte_articulos_detalle_pdf"),

    url(r'^salidas_pdf/$', PDFSalida, name="salidas_pdf"),
    url(r'^entradas_PDF/$', PDF_Bitacora_Salida, name="entradas_PDF"),
    url(r'^salidas_PDF/$', PDF_Bitacora_Salida2, name="salidas_PDF"),
    url(r'^mobiliario_PDF/$', PDF_Bitacora_Mobiliario, name="mobiliario_PDF"),
    url(r'^vehiculo_PDF/$', PDF_Bitacora_Vehiculo, name="vehiculo_PDF"),
    url(r'^inmueble_PDF/$', PDF_Bitacora_Inmueble, name="inmueble_PDF"),

    url(r'^pdf_asignarMobiliario/$', PDFEnregaMobiliario, name="pdf_asignarMobiliario"),
    url(r'^login_PDF/$', PDF_Bitacora_Login, name="login_PDF"),
    url(r'^PDF_entradas/$', PDF_entradas, name="PDF_entradas"),
    url(r'^PDF_entradasfecha/$', PDF_entradas_fecha, name="PDF_entradasfecha"),
    url(r'^PDF_salidas/$', PDF_salidas, name="PDF_salidas"),
    url(r'^PDF_salidas_fecha/$', PDF_salidas_fecha, name="PDF_salidas_fecha"),
url(r'^PDF_existencias2/$', PDF_Total_Existencias, name="PDF_existencias2"),

    # ======================= URL DE INMUEBLES ===========================================

    url(r'^nuevoInmueble/$', views.nuevoInmueble, name="nuevoInmueble"),
    url(r'^asignarInmueble/$', login_required(views.ListarInmuebleAsignar.as_view()),
        name="asignarInmueble"),
    url(r'^listarInmueble/$', login_required(views.ListarInmueble.as_view()),
        name="listarInmueble"),
    url(r'^asignaInmueble/$', views.asignarInmueble, name="asignaInmueble"),
    url(r'^listarInmuebleEmpleado/$', login_required(views.ListarEmpleadoInmueble.as_view()),
        name="listarInmuebleEmpleado"),
    url(r'^descargarInmuebleLista/$', login_required(views.ListarDescargarInmueble.as_view()),
        name="descargarInmuebleLista"),

    # MODIFICAR INMUEBLE
    url(r'^modificarInmueble/$', login_required(views.ListarInmuebleModificar.as_view()),
        name="modificarInmueble"),
    url(r'^modificarInmueble2/$', views.ModificarInmueble2, name="modificarInmueble2"),
    # DESCARGAR INMUEBLE
    url(r'^descargarInmueble/$', views.descargarInmueble, name="descargarInmueble"),

    # ======================= URL DE EXCEL ============================================

    url(r'^export/xls/$', views.export_users_xls, name='export_users_xls'),
    url(r'^export/xlsmoobiliarioall/$', views.export_mobiliario_excel, name='xlsmoobiliarioall'),
    url(r'^export/xlsentradaall/$', export_entrada_excel, name='xlsentradaall'),
    url(r'^export/xlssalidaall/$', export_salida_excel, name='xlssalidaaall'),
    url(r'^export/xlsarticuloall/$', export_articulo_excel, name='xlsarticuloaall'),
    url(r'^export/xlsvehiculoall/$', export_vehiculo_excel, name='xlsvehiculoall'),
    url(r'^export/xlsentradafecha/$', export_entrada_fechas_excel, name='xlsentradafecha'),
    url(r'^export/xlssalidafecha/$', export_salida_fecha_excel, name='xlssalidafecha'),
    url(r'^export/xlsinventarioagencia/$', export_mobiliario_agencia_excel, name='xlsinventarioagencia'),
    url(r'^export/xlsbitacoraDetEnt/$', export_bitacora_detalle_art_excel, name='xlsbitacoraDetEnt'),
    url(r'^export/xlsbitacoraEntrada/$', export_bitacora_entrada_excel, name='xlsbitacoraEntrada'),
    url(r'^export/xlsbitacoraSalida/$', export_bitacora_salida_excel, name='xlsbitacoraSalida'),
    url(r'^export/xlsbitacoraVehiculo/$', export_bitacora_vehiculo_excel, name='xlsbitacoraVehiculo'),
    url(r'^export/xlsbitacoraMobiliario/$', export_bitacora_mobiliario_excel, name='xlsbitacoraMobiliario'),
    # excel de bitacoras
    url(r'^export/xlsbitacoraMobiliarioFecha/$', export_bitacora_mobiliario_fecha_excel,
        name='xlsbitacoraMobiliarioFecha'),
    url(r'^export/xlsbitacoraVehiculoFecha/$', export_bitacora_vehiculo_fecha_excel, name='xlsbitacoraVehiculoFecha'),

    url(r'^export/xlsbitacoraEntradaFecha/$', export_bitacora_entrada_fecha_excel, name='xlsbitacoraEntradaFecha'),
    url(r'^export/xlsbitacoraSalidaFecha/$', export_bitacora_salida_fecha_excel, name='xlsbitacoraEntradaFecha'),
    url(r'^export/xlsinmueble/$', export_inmueble_excel, name='xlsinmueble'),
    url(r'^export/xlslogin/$', export_bitacora_login_excel, name='xlslogin'),

    # ======================================= URL DE BITACORAS ===========================================

    url(r'^bitacoraMobiliario/$', login_required(views.BitacoraMobiliario.as_view()),
        name="bitacoraMobiliario"),

    url(r'^bitacoraDetEntrada/$', login_required(views.BitacoraDetEntrada.as_view()),
        name="bitacoraDetEntrada"),

    url(r'^bitacoraEntrada/$', login_required(views.BitacoraEntrada.as_view()),
        name="bitacoraEntrada"),

    url(r'^bitacoraSalida/$', login_required(views.BitacoraSalida.as_view()),
        name="bitacoraSalida"),
    url(r'^bitacoraLogin/$', login_required(views.BitacoraLogin.as_view()),
        name="bitacoraLogin"),

    url(r'^bitacoraVehiculo/$', login_required(views.BitacoraVehiculo.as_view()),
        name="bitacoraVehiculo"),
    url(r'^bitacoraMobiliarioFecha/$', login_required(views.BitacoraMobiliarioFecha.as_view()),
        name="bitacoraMobiliarioFecha"),
    url(r'^bitacoraVehiculoFecha/$', login_required(views.BitacoraVehiculoFecha.as_view()),
        name="bitacoraVehiculoFecha"),
    url(r'^bitacoraEntradaFecha/$', login_required(views.BitacoraEntradaFecha.as_view()),
        name="bitacoraEntradaFecha"),
    url(r'^bitacoraSalidaFecha/$', login_required(views.BitacoraSalidaFecha.as_view()),
        name="bitacoraSalidaFecha"),

    url(r'^nuevoDetSalida/$', views.detalleSalida, name='nuevoDetSalida'),
    url(r'^nuevoDetalleSalida2/$', views.nuevoDetalleSalida2, name='nuevoDetalleSalida2'),
    url(r'^nuevoProveedor/$', views.nuevoProveedor, name='nuevoProveedor'),
    url(r'^listarProveedor/$', login_required(views.ListarProveedor.as_view()), name='listarProveedor'),
    url(r'^modificarProveedor/$', login_required(views.ListarProveedorModificar.as_view()), name='modificarProveedor'),
    url(r'^modificarProveedor2/$', login_required(views.AuthorUpdate.as_view()), name='modificarProveedor2'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
