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
    
    
    DESDE AQUI SON MANEJADAS TODAS LAS URL DEL SISTEMA, ESTO QUIERE DECIR QUE ES EL ENLACE ENTRE
    LAS VISTAS Y LOS MODELOS, LAS URL SIRVEN COMO CONTROLADORES DEL SISTEMA.
    
"""

from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from inventariohonducorapp import views
from InventarioHONDUCOR import settings
#VISTA PARA MANEJAR EL LOGIN
from django.contrib.auth.views import login
#VISTAS QUE CONTIENEN PDF
from  inventariohonducorapp.pdf import Print_PDF, PDFSalida, PDFEnregaMobiliario, PDF_Bitacora_Salida, \
    PDF_Bitacora_Salida2, PDF_Bitacora_Mobiliario, PDF_Bitacora_Vehiculo, PDF_Bitacora_Inmueble, PDF_Bitacora_Login, \
    PDF_entradas, PDF_entradas_fecha, PDF_salidas, PDF_salidas_fecha,PDF_Total_Existencias,PDF_MobiliarioP
from django.contrib.auth.views import logout_then_login

#VISTAS QUE CONTIENEN EXCEL
from inventariohonducorapp.excel import export_entrada_excel, export_salida_excel, export_articulo_excel, \
    export_vehiculo_excel, export_entrada_fechas_excel, export_salida_fecha_excel, export_mobiliario_agencia_excel, \
    export_bitacora_detalle_art_excel, export_bitacora_entrada_excel, export_bitacora_mobiliario_excel, \
    export_bitacora_salida_excel, export_bitacora_vehiculo_excel, export_bitacora_mobiliario_fecha_excel, \
    export_bitacora_vehiculo_fecha_excel, export_bitacora_entrada_fecha_excel, export_bitacora_salida_fecha_excel, \
    export_inmueble_excel, export_bitacora_login_excel,export_mobiliario_prestado2_excel
#VISTAS DEL SISTEMA
from inventariohonducorapp.views import main, Personas, VerEntradas, BuscarMobiliario, VerSalidas, BuscarMobiliario2, \
    BuscarEmpleado, BuscarMobiliarioPrestado, BuscarEmpleadoMP, VerExistenciasArticulos, VerExistenciasArticulosDet
#ARRAY CON TODAS LAS URL
urlpatterns = [
    #ESTA URL SIRVE PARA MOSTRAR EL PDF CON LA DOCUMENTACION
    url(r'^documentacion/$', views.Documentacion, name="documentacion"),
    # URL para el sitio de panel de administracion
    url(r'^admin/', admin.site.urls),
    # esta URL es para redireccionar al login y realizar todos los procesos de autenticacion
    url(r'^$', login, {'template_name': 'login.html'}, name='login'),
    # Esta url redireccion al index del sitio
    url(r'^main/$', views.main, name="main"),
    # esta url redirecciona al calendario
    #url(r'^calendario/$', views.Calendario, name="calendario"),
    # esta URL es usada luego de cualquier validacion exitosa de los formularios
    url(r'^add_post/$', main, name="add_post"),
    # Esta URL cierra sesion
    url(r'^cerrar/$', logout_then_login, name='logout'),
    #URL DE GRACISO DE ALMACEN 1
    url(r'^graficos/$', views.graficos, name='graficos'),
    #URL DE GRAFICOS DE ALMACEN 2
    url(r'^graficos2/$', views.grafico_agencia, name='graficos2'),
    #URL DE GRAFICOS DE MOBILIARIO 1
    url(r'^graficoMobiliario/$', views.graficosMobiliario, name='graficosMobiliario'),
    #URL DE GRAFICOS DE MOBILIARIO2
    url(r'^graficoMobiliario2/$', views.grafico_mobiliario_agencia, name='graficosMobiliario2'),
    #URL DE GRAFICO DE VEHICULOS
    url(r'^graficoVehiculo/$', views.graficosVehiculo, name='graficoVehiculo'),
    # ======================================== URL DE ARTICULOS =============================

    # Esta URL sirve para registrar una nueva entrada, recibe el parametro pk
    url(r'^nuevoDetalleArticulo/', views.nuevoDetalleArticulo, name='nuevoDetalleArticulo'),
    #URL PARA REGISTRAR UNA NUEVA ENTRADA 2
    url(r'^nuevoArticulo/$', views.nuevoArticulo, name='nuevoArticulo'),
    #ESTA URL SIRVE PARA BUSCAR UN ARTICULO
    url(r'^buscarArticulo/', login_required(Personas.as_view()), name="personas"),
    #ESTA URL SIRVE PARA BUSCAR ARTICULOS, NO ENLAZA CON NADA MAS
    url(r'^buscarSoloArticulos/', login_required(views.BuscarAticulosSolamente.as_view()), name="buscarSoloArticulos"),
    # lista los incidentes de los articulos
    url(r'^listarIncidenteArticulo2/', login_required(views.ListarIncidenteArticulo2.as_view()),
        name="listarIncidenteArticulo2"),
    #ESTA URL SIRVE PARA BUSCAR LOS ARTICULOS EN LAS EXISTENCIAS POR DETALLE
    url(r'^buscarArticuloDet/', login_required(VerExistenciasArticulosDet.as_view()), name="verExistenciasDet"),
    # VER EXISTENCIA DE ARTICULOS
    url(r'^verExistencias/', login_required(VerExistenciasArticulos.as_view()), name="verExistencias"),
    # VER ARTICULOS SIN EXISTENCIA
    url(r'^verNoExistencias/', login_required(views.VerSinExistenciasArticulos.as_view()), name="verNoExistencias"),
    #URL PARA NUEVO DETALLE DE ARTICULO
    url(r'^nuevoDetalleArticuloLista/', login_required(views.VerArticulosEntradas.as_view()),
        name="nuevoDetalleArticuloLista"),
    #URL PARA LISTAR LAS INCIDENCIAS DE LOS ARTICULOS
    url(r'^listarArticulosIncidencias/$', login_required(views.ListaArticulosIncidentias.as_view()),
        name="listarArticulosIncidencias"),
    #URL PARA MODIFICAR LOS ARTICULOS
    url(r'^modificarArticulo/$', login_required(views.ModificarArticulo.as_view()),
        name="modificarArticulo"),
    # DAR BAJA ARTICULO
    url(r'^bajaArticulo/$', login_required(views.ListarDarBajaArticulo.as_view()),
        name="bajaArticulo"),
    #URL PARA DAR DE BAJA A LOS ARTICULOS, REDIRECCIONA
    url(r'^bajaArticulo2/$', views.DarBajaArticulo, name="bajaArticulo2"),
    #URL PARA MODIFICAR ARTICULOS, REDIRECCIONA
    url(r'^modificarArticulo2/$', views.ModificarArticulo2, name="modificarArticulo2"),
    # esta URL es para registrar nueva incidencia, redirecciona a registrar_incidencia.html
    url(r'^nuevaIncidenciaArt/$', views.nuevaIncidenciaArticulo, name='nuevaIncidenciaArt'),
    # ALERTA DE EXISTENCIAS
    url(r'^alerta/$', login_required(views.AlertaExistencias.as_view()),
        name="alerta"),
    # ===========================  URL DE ENTRADAS =====================================
    # ENTRADAS QUE SE VAN A MODIFICAR
    #Lista el mobiliario que un empleado tiene asignado
    url(r'^verMobiliarioPE3/', login_required(views.VerMobiliarioP3.as_view()), name="verMobiliarioPE3"),
    #URL DE LAS ENTRADAS QUE SE VAN A MODIFICAR
    url(r'^verEntradaModificar/', login_required(views.VerEntradasModificar.as_view()), name="verEntradaModificar"),
    #URL PARA LISTAR LAS ENTRADAS
    url(r'^verEntrada/', login_required(VerEntradas.as_view()), name="entradas"),
    # url de entradas_fecha.html
    url(r'^verEntradaFecha/', login_required(views.VerEntradaFecha.as_view()), name="verEntradaFecha"),
    #URL PARA MODIFICAR LAS ENTRADAS, REDIRECCIONAR
    url(r'^modificarEntradas2/', views.ModificarEntrada2, name="modificarEntradas2"),

    # ======================== URL DE SALIDAS ===============================
    #URL PARA REGISTRAR NUEVA SALIDA
    url(r'^nuevaSalida/', views.nuevaSalida, name="nuevaSalida"),
    #URL PARA VER TODA LAS SALIDAS
    url(r'^verSalidas/', login_required(VerSalidas.as_view()), name="verSalidas"),
    # url de salidas_fecha.html
    url(r'^verSalidaFecha/', login_required(views.VerSalidaFecha.as_view()), name="verSalidaFecha"),

    # ==================  URL DE MOBILIARIO  ========================
    #URL PARA REGISTRAR NUEVO MOBILIARIO
    url(r'^nuevoMobiliario/', views.nuevoMobiliario, name="nuevoMobiliario"),
    #URL PARA ASIGNAR NUEVO MOBILIARIO
    url(r'^asignarMobiliario/', views.asignarMobiliario, name="asignarMobiliario"),
    #URL PARA DESCARGAR MOBILIARIO
    url(r'^descargarMobiliario/', views.descargarMobiliario, name="descargarMobiliario"),
    #buscar mobiliario asignago a empleado
    url(r'^mobiliarioPorEmpleado/',login_required(views.BuscarEmpleadoMobiliarioAsignado.as_view()), name="mobiliarioPorEmpleado"),
    #URL PARA BUSCAR MOBILIARIO
    url(r'^buscarMobiliario/', login_required(BuscarMobiliario.as_view()), name="buscarMobiliario"),
    #URL PARA BUSCAR MOBILIARIO PRESTADO
    url(r'^BuscarMobiliarioPrestado/', login_required(BuscarMobiliarioPrestado.as_view()),
        name="BuscarMobiliarioPrestado"),
    #URL QUE MUESTRA SOLAMENTE EL MOBILIARIO
    url(r'^buscarMobiliarioIndex/', login_required(views.BuscarMobiliarioIndex.as_view()),
        name="buscarMobiliarioIndex"),
    # esta url direcciona hacia buscar_mobiliario2.html es la que asgina el mobiliario
    url(r'^buscarMobiliario2/', login_required(BuscarMobiliario2.as_view()), name="buscarMobiliario2"),
    #URL DE MOBILIARIO POR AGENCIA
    url(r'^agenciaMobiliario/', login_required(views.ListarAgenciasMobiliario.as_view()),
        name="agenciaMobiliario"),
    #URL DE INVENTARIO DE MOBILIARIO POR AGENCIA
    url(r'^inventarioMobiliarioAgencia', login_required(views.ListarAgenciasMobiliario2.as_view()),
        name="inventarioMobiliarioAgencia"),
    # listar_mobiliario_modificar
    url(r'^modificarMobiliario/', login_required(views.ListarModificarMobiliario.as_view()),
        name="modificarMobiliario"),
    #URL DE MOFIDICAR MOBILIARO
    url(r'^modificarMobiliario2/', views.ModificarMobiliario2,
        name="modificarMobiliario2"),
    # empleado para detalle mobiliario
    url(r'^empleadoMobiliario10/', login_required(views.BuscarEmpleado10.as_view()),
        name="empleadoMobiliario10"),
    # mobiliario detalle
    url(r'^asignarMobiliario11/', login_required(views.MobiliarioDetalle11.as_view()),
        name="asignarMobiliario11"),
    #URL PARA DAR DE BAJA A MOBILIARIO
    url(r'^bajaMobiliario/', login_required(views.ListarMobiliarioDarDeBaja.as_view()),
        name="bajaMobiliario"),
    #URL PARA DAR DE BAJA A MOBILIARIO , REDIRECCIONA
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
    #REPORTE PDF DE EXISTENCIAS
    url(r'^reporte_existencias_pdf/$', login_required(views.ReportePersonasPDF.as_view()), name="reporte_personas_pdf"),
    #REPORTE PDF DE INVENTARIO DE MOBILIARIO
    url(r'^reporte_mobiliario_pdf/$', login_required(views.ReporteMobiliarioPDF.as_view()),
        name="reporte_mobiliario_pdf"),
    #URL DE REPORTE DE ARTICULOS DETALLE
    url(r'^reporte_articulos_detalle_pdf/$', Print_PDF, name="reporte_articulos_detalle_pdf"),
    #URL DE REPORTE PDF DE SALIDAS
    url(r'^salidas_pdf/$', PDFSalida, name="salidas_pdf"),
    #URL DE REPORTE PDF DE ENTRADAS
    url(r'^entradas_PDF/$', PDF_Bitacora_Salida, name="entradas_PDF"),
    #URL DE REPORTE PDF DE BITACORA DE SALIDAS
    url(r'^salidas_PDF/$', PDF_Bitacora_Salida2, name="salidas_PDF"),
    #URL DE REPORTE PDF DE BITACORA DE MOBILIARIO
    url(r'^mobiliario_PDF/$', PDF_Bitacora_Mobiliario, name="mobiliario_PDF"),
    #URL PDF DE BITACORAS DE VEHICULOS
    url(r'^vehiculo_PDF/$', PDF_Bitacora_Vehiculo, name="vehiculo_PDF"),
    #URL DE REPORTE DE BITACORAS DE INMUEBLE
    url(r'^inmueble_PDF/$', PDF_Bitacora_Inmueble, name="inmueble_PDF"),
    #URL DE ACTA DE ASIGNAR MOBILIARIO
    url(r'^pdf_asignarMobiliario/$', PDFEnregaMobiliario, name="pdf_asignarMobiliario"),
    #URL DE REPORTE DE INICIO DE SESION EN PDF
    url(r'^login_PDF/$', PDF_Bitacora_Login, name="login_PDF"),
    #URL BITACORA DE LOGIN PDF
    url(r'^PDF_entradas/$', PDF_entradas, name="PDF_entradas"),
    #URL DE ENTRADAS POR FECHA BITACORA
    url(r'^PDF_entradasfecha/$', PDF_entradas_fecha, name="PDF_entradasfecha"),
    #URL DE PDF SALIDAS
    url(r'^PDF_salidas/$', PDF_salidas, name="PDF_salidas"),
    #URL DE REPORTE DE SALIDAS POR FECHA
    url(r'^PDF_salidas_fecha/$', PDF_salidas_fecha, name="PDF_salidas_fecha"),
    #URL DE EXISTENCIAS DE ARTICULOS PDF
    url(r'^PDF_existencias2/$', PDF_Total_Existencias, name="PDF_existencias2"),
    #URL DE PDF DE MOBILIARIO ASIGNADO
    url(r'^PDF_MobiliarioP/$', PDF_MobiliarioP, name="PDF_MobiliarioP"),

    # ======================= URL DE INMUEBLES ===========================================
    #URL PARA NUEVO INMUEBLE
    url(r'^nuevoInmueble/$', views.nuevoInmueble, name="nuevoInmueble"),
    #URL DE ASIGNAR NUEVO INMUEBLE
    url(r'^asignarInmueble/$', login_required(views.ListarInmuebleAsignar.as_view()),
        name="asignarInmueble"),
    #URL PARA LISTAR INMUEBLE
    url(r'^listarInmueble/$', login_required(views.ListarInmueble.as_view()),
        name="listarInmueble"),
    #URL DE ASIGNAR INMUEBLE,
    url(r'^asignaInmueble/$', views.asignarInmueble, name="asignaInmueble"),
    #URL DE LISTAR EMPLEADO PARA INMUEBLE
    url(r'^listarInmuebleEmpleado/$', login_required(views.ListarEmpleadoInmueble.as_view()),
        name="listarInmuebleEmpleado"),
    #URL PARA DESCARGAR INMUEBLE
    url(r'^descargarInmuebleLista/$', login_required(views.ListarDescargarInmueble.as_view()),
        name="descargarInmuebleLista"),

    # MODIFICAR INMUEBLE
    url(r'^modificarInmueble/$', login_required(views.ListarInmuebleModificar.as_view()),
        name="modificarInmueble"),
    url(r'^modificarInmueble2/$', views.ModificarInmueble2, name="modificarInmueble2"),
    # DESCARGAR INMUEBLE
    url(r'^descargarInmueble/$', views.descargarInmueble, name="descargarInmueble"),

    # ======================= URL DE EXCEL ============================================
    #EXCEL DE ENTRADAS
    url(r'^export/xls/$', views.export_users_xls, name='export_users_xls'),
    #EXCEL DE TODOS LOS MOBIBILIARIOS
    url(r'^export/xlsmoobiliarioall/$', views.export_mobiliario_excel, name='xlsmoobiliarioall'),
    #EXCEL DE TODAS LAS ENTRADAS
    url(r'^export/xlsentradaall/$', export_entrada_excel, name='xlsentradaall'),
    #EXCEL DE TODAS LAS SALIDAS
    url(r'^export/xlssalidaall/$', export_salida_excel, name='xlssalidaaall'),
    #EXCEL DE TODOS LOS ARTICULOS
    url(r'^export/xlsarticuloall/$', export_articulo_excel, name='xlsarticuloaall'),
    #EXCEL DE TODOS LOS VEHICULOS
    url(r'^export/xlsvehiculoall/$', export_vehiculo_excel, name='xlsvehiculoall'),
    #EXCEL DE TODAS LAS ENTRADAS POR FECHA
    url(r'^export/xlsentradafecha/$', export_entrada_fechas_excel, name='xlsentradafecha'),
    #EXCEL DE TODAS LAS SALIDAS POR FECHA
    url(r'^export/xlssalidafecha/$', export_salida_fecha_excel, name='xlssalidafecha'),
    #EXCEL DEL INVENTARIO DE MOBILIARIO DE AGENCIAS DETALLE
    url(r'^export/xlsinventarioagencia/$', export_mobiliario_agencia_excel, name='xlsinventarioagencia'),
    #EXCEL DE BITACORAS DE  DETALLE ENTRADAS
    url(r'^export/xlsbitacoraDetEnt/$', export_bitacora_detalle_art_excel, name='xlsbitacoraDetEnt'),
    #EXCEL DE BITACORAS DE ENTRADAS
    url(r'^export/xlsbitacoraEntrada/$', export_bitacora_entrada_excel, name='xlsbitacoraEntrada'),
    #EXCEL DE BITACORAS DE SALIDAS
    url(r'^export/xlsbitacoraSalida/$', export_bitacora_salida_excel, name='xlsbitacoraSalida'),
    #EXCEL DE BITACAROAS DE VEHICULOS
    url(r'^export/xlsbitacoraVehiculo/$', export_bitacora_vehiculo_excel, name='xlsbitacoraVehiculo'),
    #EXCEL DE BITACORA DE MOBILIARIO
    url(r'^export/xlsbitacoraMobiliario/$', export_bitacora_mobiliario_excel, name='xlsbitacoraMobiliario'),
    # excel de bitacoras DE MOBILIARIO POR FECHA
    url(r'^export/xlsbitacoraMobiliarioFecha/$', export_bitacora_mobiliario_fecha_excel,
        name='xlsbitacoraMobiliarioFecha'),
    #EXCEL DE BITACORA DE VEHICULOS POR FECHA
    url(r'^export/xlsbitacoraVehiculoFecha/$', export_bitacora_vehiculo_fecha_excel, name='xlsbitacoraVehiculoFecha'),
    #EXCEL DE BITACORA DE ENTRADA POR FECHA
    url(r'^export/xlsbitacoraEntradaFecha/$', export_bitacora_entrada_fecha_excel, name='xlsbitacoraEntradaFecha'),
    #EXCEL DE BITACORA DE ENTRADAS POR FECHA
    url(r'^export/xlsbitacoraSalidaFecha/$', export_bitacora_salida_fecha_excel, name='xlsbitacoraEntradaFecha'),
    #EXCEL DE INVENTARIO DE INMUEBLES
    url(r'^export/xlsinmueble/$', export_inmueble_excel, name='xlsinmueble'),
    #EXCEL DE BITACORA DE INICIO DE SESION
    url(r'^export/xlslogin/$', export_bitacora_login_excel, name='xlslogin'),
    #URL DE EXCEL DE MOBILIARIO PRESTADO
    url(r'^export/xlsmprestado/$', export_mobiliario_prestado2_excel, name='xlsmprestado'),

    # ======================================= URL DE BITACORAS ===========================================
    #URL DE BITACORA DE MOBILIARIO
    url(r'^bitacoraMobiliario/$', login_required(views.BitacoraMobiliario.as_view()),
        name="bitacoraMobiliario"),
    #URL DE BITACORA DE DETALLE DE ENTRADA
    url(r'^bitacoraDetEntrada/$', login_required(views.BitacoraDetEntrada.as_view()),
        name="bitacoraDetEntrada"),
    #URL DE BITACORA DE ENTRADA
    url(r'^bitacoraEntrada/$', login_required(views.BitacoraEntrada.as_view()),
        name="bitacoraEntrada"),
    #URL DE BITACORA DE SALIDA
    url(r'^bitacoraSalida/$', login_required(views.BitacoraSalida.as_view()),
        name="bitacoraSalida"),
    #URL DE BITACORA DE INICIO DE SESION
    url(r'^bitacoraLogin/$', login_required(views.BitacoraLogin.as_view()),
        name="bitacoraLogin"),
    #URL DE BITACORA DE VEHICULO
     url(r'^bitacoraVehiculo/$', login_required(views.BitacoraVehiculo.as_view()),
        name="bitacoraVehiculo"),
    #URL DE BITACORA DE MOBILIARIO POR FECHA
    url(r'^bitacoraMobiliarioFecha/$', login_required(views.BitacoraMobiliarioFecha.as_view()),
        name="bitacoraMobiliarioFecha"),
    #URL DE BITACORA DE VEHICULO POR FECHA
    url(r'^bitacoraVehiculoFecha/$', login_required(views.BitacoraVehiculoFecha.as_view()),
        name="bitacoraVehiculoFecha"),
    #URL DE BITACCORA DE ENTRADA POR FECHA
    url(r'^bitacoraEntradaFecha/$', login_required(views.BitacoraEntradaFecha.as_view()),
        name="bitacoraEntradaFecha"),
    #URL DE BITACORA DE SALIDA POR FECHA
    url(r'^bitacoraSalidaFecha/$', login_required(views.BitacoraSalidaFecha.as_view()),
        name="bitacoraSalidaFecha"),
    #URL DE NUEVO DETALLE DE SALIDA
    url(r'^nuevoDetSalida/$', views.detalleSalida, name='nuevoDetSalida'),
    #URL DE NUEVO DETALLE DE SALIDA 2 LA CONTINUACION
    url(r'^nuevoDetalleSalida2/$', views.nuevoDetalleSalida2, name='nuevoDetalleSalida2'),
    #URL DE NUEVO PROVEEDOR
    url(r'^nuevoProveedor/$', views.nuevoProveedor, name='nuevoProveedor'),
    #URL PARA LISTAR TODOS LOS PROVEEDORES
    url(r'^listarProveedor/$', login_required(views.ListarProveedor.as_view()), name='listarProveedor'),
    #URL PARA MODIFICAR PROVEEDOR
    url(r'^modificarProveedor/$', login_required(views.ListarProveedorModificar.as_view()), name='modificarProveedor'),
    url(r'^modificarProveedor2/$', login_required(views.AuthorUpdate.as_view()), name='modificarProveedor2'),

]
#SI EL DEBUG ES TRUE ENTONCES QUE TOME LA CARPETA STATIC_URL, DE LO CONTRARIO QUE UTILIZE LA CARPETA MEDIA_URL
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
