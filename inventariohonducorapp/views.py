import datetime
import time
import dateparser
import xlwt

import psycopg2
from django.db import connection
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponse, request
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.urls import reverse
from django.views import generic
from django.views.generic import DetailView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import TableStyle, Table, SimpleDocTemplate

"""
EN ESTA SECCION SE PRESENTAN TODAS LAS VISTAS DEL SISTEMA, DESDE AQUI ES DONDE SE REALIZA LA MAYORIA DE PROGRAMACION
VALIDACION, ORDENES, ETC... EN EL SISTEMA

"""

from inventariohonducorapp.models import tb_Articulo, tb_DetalleArticulo, tb_entrada, tb_Mobiliario, \
    tb_CategoriaMobiliario, tb_MobiliarioPrestado, tb_Empleado, tb_salida, tb_Jefatura, Agencia, tb_MobiliarioDevuelto, \
    tb_incidenciaArticulo, tb_Vehiculo, tb_VehiculoAsignado, tb_VehiculoDescargado, tb_Inmueble, tb_Admin_Inmueble, \
    tb_audit_det_articulo, tb_audit_det_vehiculo, tb_audit_entrada, tb_audit_mobiliario, tb_audit_salida, \
    tb_detalle_salida, tb_InmuebleDescargado, tb_audit_login, tb_proveedor
# FORMULARIOS DEL PROYECTO
from inventariohonducorapp.forms import Tb_ArticuloForm, Tb_DetalleArtForm, Tb_MobiliarioForm, \
    Tb_MobiliarioPrestadoForm, Tb_SalidaForm, Tb_DescargarMobiliarioForm, Tb_IncidenciaArticulo, Tb_NuevoVehiculo, \
    Tb_NuevoVehiculoAsignado, Tb_DescargarVehiculoForm, Tb_NuevoInmuebleForm, Tb_AsignarInmuebleForm, \
    Tb_ModificarMobiliario, \
    Tb_NuevoDetalleSalida, Tb_nuevoDetalleSalida2, Tb_ModificarArticulo, Tb_ModificarVehiculo, Tb_ModificarInmueble, \
    Tb_DescargarInmueble, Tb_ProveedorForm

# FUNCIONES DEL PROYECTO
from django.db.models import F, Count, Sum, FloatField

# ELEMNTOS PARA LOS REPORTES
from django.conf import settings
from io import BytesIO
from reportlab.pdfgen import canvas
from django.views.generic import View
import json


# Create your views here.
# ================ VISTAS SENCILLAS ==================================================================
# VISTA MAIN PAGINA PRINCIPAL DEL SITIO
@login_required()
def main(request):
    existencia_menor = tb_Articulo.objects.filter(existencia__lte=10)
    contador = tb_Articulo.objects.filter(existencia__lte=10).count()
    print(contador)

    return render(request, 'index.html', {'existencia': existencia_menor, 'alerta': contador})


# CALENDARIO DEL SITIO
@login_required()
def Calendario(request):
    return render(request, 'pages_calendar.html', {})


# VISTA DE DOCUMENTACION
@login_required()
def Documentacion(request):
    return render(request, 'static/manual_usuario.pdf', {})


# VISTA LOGIN, pertenece a la clase de django auth.login, se encarga de redireccionar a el archivo base
# login los datos para realizar la autenticacion
def login(request):
    return render(request, 'login.html', {})


# FUNCION TOP 10 PRODUCOTS CON MAS EXISTENCIAS
@login_required()
def graficos(request):
    # PRIMERA CONEXION
    cur = connection.cursor()
    # llamada a procedimiento almacenado
    cur.execute("select nombre_art, MAX(existencia) from inventariohonducorapp_tb_articulo GROUP BY  nombre_art;")
    # recupera el valor del procedimiento almacenado
    row = cur.fetchall()

    # cierra la conexcion a la bd
    cur.close()
    # RECUPERA LA FECHA ACTUAL
    fecha = time.strftime('%m')

    # SEGUNDA CONEXION
    cur2 = connection.cursor()

    # llamada a procedimiento almacenado
    cur2.execute(
        "select a.nombre_art,count(s.cantidad) from inventariohonducorapp_tb_detalle_salida s,inventariohonducorapp_tb_detallearticulo d,inventariohonducorapp_tb_articulo a where s.fecha_registro_salida  between '2017-" + fecha + "-1' and '2017-" + fecha + "-30' and s.codigo_barras=d.codigo_barras and a.id= d.cod_articulo_id group by a.nombre_art")
    # recupera el valor del procedimiento almacenado
    row2 = cur2.fetchall()
    # cierra la conexcion a la bd
    cur2.close()

    # lleNar json para enviar a template
    jsona2 = json.dumps([['articulos', 'TOP SALIDAS PARA ESTE MES']] + row2)
    # SEGUNDO JSON PARA ENVIAR LAS EXISTENCIAS
    jsona = json.dumps([['articulos', 'existencias']] + row)

    return render(request, 'graficos.html', {'array': jsona, 'array2': jsona2})


# GRAFICO DE AGENCIAS
@login_required()
def grafico_agencia(request):
    cur = connection.cursor()

    # cur.callproc("retornacodbarras", (codigo,))
    # llamada a procedimiento almacenado
    cur.execute(
        "select s.agencia,SUM(CAST (d.precio_unitario as float) * s.cantidad) as TOTAL from inventariohonducorapp_tb_detallearticulo d,inventariohonducorapp_tb_articulo a,inventariohonducorapp_tb_detalle_salida s where s.cod_det_art_id=d.id and a.id= d.cod_articulo_id and s.fecha_registro_salida  between '2017-06-19' and '2017-06-19' group by s.agencia order by  TOTAL desc")
    # recupera el valor del procedimiento almacenado
    row = cur.fetchall()

    # cierra la conexcion a la bd
    cur.close()
    jsona = json.dumps(row)
    # si el metodo es post puede realizar las operacion, sino regresa a el formulario que lo llamo
    if request.method == 'POST':
        fecha = str(datetime.datetime.strptime(request.POST['startfecha'], "%m/%d/%Y"))
        fecha2 = str(datetime.datetime.strptime(request.POST['endfecha'], "%m/%d/%Y"))
        cur2 = connection.cursor()

        # cur.callproc("retornacodbarras", (codigo,))
        # llamada a procedimiento almacenado
        cur2.execute(
            "select s.agencia,SUM(CAST (d.precio_unitario as float) * s.cantidad) as TOTAL from inventariohonducorapp_tb_detallearticulo d,inventariohonducorapp_tb_articulo a,inventariohonducorapp_tb_detalle_salida s where s.cod_det_art_id=d.id and a.id= d.cod_articulo_id and s.fecha_registro_salida  between '" + fecha + "' and '" + fecha2 + "' group by s.agencia order by  TOTAL desc ")
        # recupera el valor del procedimiento almacenado
        row2 = cur2.fetchall()

        # cierra la conexcion a la bd
        cur2.close()

        # llenar json para enviar a template
        jsona2 = json.dumps(row2)

        return render(request, 'grafico_2.html', {'array': jsona2})
    else:

        return render(request, 'grafico_2.html', {'array': jsona})


# ================================================= graficos mobiliarios
@login_required()
def graficosMobiliario(request):
    # PRIMERA CONEXION
    cur = connection.cursor()

    # llamada a procedimiento almacenado
    cur.execute(
        "select c.nombre_categoria,SUM(m.costo_uni)as TOTAL from inventariohonducorapp_tb_mobiliario m,inventariohonducorapp_tb_categoriamobiliario c where m.cod_cat_mobiliario_id = c.id group by c.nombre_categoria;")
    # recupera el valor del procedimiento almacenado
    row = cur.fetchall()

    # cierra la conexcion a la bd
    cur.close()
    # LLENAR JSON PARA ENVIAR EXISTENCIAS
    jsona = json.dumps([['articulos', 'existencias']] + row)

    return render(request, 'grafico_mobiliario.html', {'array': jsona})


# ============================== GRAFICO DE MOBILIARIOS 2

@login_required()
# GRAFICO DE MOBILIARIO POR AGENCIA
def grafico_mobiliario_agencia(request):
    cur2 = connection.cursor()

    # llamada a procedimiento almacenado
    cur2.execute(
        "select m.ubicacion_actual,SUM(m.costo_uni)as TOTAL from inventariohonducorapp_tb_mobiliario m,inventariohonducorapp_tb_categoriamobiliario c where m.cod_cat_mobiliario_id = c.id group by m.ubicacion_actual")
    # recupera el valor del procedimiento almacenado
    row2 = cur2.fetchall()

    # cierra la conexcion a la bd
    cur2.close()
    # lleNAR el json para enviar al template
    jsona2 = json.dumps(row2)

    return render(request, 'grafico_mobiliario2.html', {'array': jsona2})


# GRAFICOS PARA VEHICULOS
def graficosVehiculo(request):
    # PRIMERA CONEXION
    cur = connection.cursor()

    # llamada a procedimiento almacenado
    cur.execute(
        "select tipo_vehiculo, count(costo)as total from inventariohonducorapp_tb_vehiculo group by tipo_vehiculo;")
    # recupera el valor del procedimiento almacenado
    row = cur.fetchall()

    # cierra la conexcion a la bd
    cur.close()

    # llana json para enviar a template
    jsona = json.dumps([['articulos', 'existencias']] + row)

    return render(request, 'grafico_vehiculo.html', {'array': jsona})


# ========================================== INSERTAR EN FORMULARIOS ===============================
@login_required()
# esta vista sirve para registrar un nuevo articulo
def nuevoArticulo(request):
    # si el metodo es post deja pasar y realizar las funciones,sino regresa al formulario que lo llamo
    if request.method == "POST":
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_ArticuloForm(request.POST or None, request.FILES or None)
        # si el formulario es valido deja realizar el registro
        if form.is_valid():
            # la excepcion controla que en caso de que la imagen venga vacia
            # se agregue una imagen por default del sistema

            try:
                # nueva instancia de el modelo tb_articulo para registrar los datos del formulario HTML
                newArticulo = tb_Articulo(
                    nombre_art=request.POST["nombre_art"],
                    descrip=request.POST["descrip"],
                    imagen_art=request.FILES['imagen_art'],
                    existencia="0",
                    cod_categoria_id=request.POST["cod_categoria"],
                    estado_articulo="activo",
                    usuario_regis=request.user
                )
                # REGISTRA UN NUEVO ARTICULO
                newArticulo.save(form)
            except Exception:
                # nueva instancia de el modelo tb_articulo para registrar los datos del formulario HTML
                newArticulo = tb_Articulo(
                    nombre_art=request.POST["nombre_art"],
                    descrip=request.POST["descrip"],
                    imagen_art="/imagenes/melamina_blanca-3.jpg",
                    existencia="0",
                    cod_categoria_id=request.POST["cod_categoria"],
                    estado_articulo="activo",
                    usuario_regis=request.user
                )
                # realiza el registro con los datos del formulario
                newArticulo.save(form)
                # MENSAJE DE CONFIRMACION QUE LA OPERACION SE REALIZO CON EXITO
            messages.success(request, "REGISTRADO EXITOSAMENTE")
            # REGRESA AL INICIO
            return redirect("/add_post")

    else:
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_ArticuloForm()
    # REGRESA A A LA PAGINA NUEVO ARTICULO Y CARGA LOS DATOS DEL FORMULARIO
    return render(request, 'nuevo_articulo.html', {'form': form})


@login_required()
# esta funcion sirve para agregar un nuevo registro a las tablas tb_DetalleArticulo, tb_entrada, y actualiza la tabla de articulos
def nuevoDetalleArticulo(request):
    if request.method == "POST":
        # NUEVA INSTANCIA DE FORMULARIO PARA DETALLE FORM
        form = Tb_DetalleArtForm(request.POST or None, request.FILES or None)
        # establece conexion a la bd

        cur = connection.cursor()
        codigo = request.POST['codigo_barras']
        # cur.callproc("retornacodbarras", (codigo,))
        # llamada a procedimiento almacenado
        cur.execute("select verificacodbarras(%s);", (codigo,))
        # recupera el valor del procedimiento almacenado
        row = cur.fetchone()
        newID = row[0]
        # cierra la conexcion a la bd
        cur.close()

        # segundo procedimiento almacenado
        # ========================================================================================
        cur2 = connection.cursor()
        codigoA = int(request.POST['cod_articulo'])
        # cur.callproc("retornacodbarras", (codigo,))
        # llamada a procedimiento almacenado
        cur2.execute("select verificodigoarticulo(%s);", (codigoA,))
        # recupera el valor del procedimiento almacenado
        row2 = cur2.fetchone()
        newID2 = row2[0]

        # cierra la conexcion a la bd
        cur2.close()

        if newID == 1:
            # VERIFICA QUE EL CODIGO DE BARRAS QUE SE INGRESA NO EXISTA
            # SE VERIFICA PARA QUE NO EXISTAN DUPLICACIONES EN LA BD
            messages.error(request,
                           "ESTE CODIGO DE BARRAS YA EXISTE, PREGUNTE AL ADMINISTRADOR DEL SISTEMA SOBRE ESTE ERROR")
            return redirect("/nuevoDetalleArticuloLista")
        elif newID2 == 0:
            # VERIFICA QUE EL CODIGO DEL ARTICULO EXISTA
            messages.error(request, "EL CODIGO DEL ARTICULO NO EXISTE")
        else:
            if form.is_valid():
                # mediante esta declaracion se inserta un nuevo registro en la tabla tb_DetalleArticulo
                # LA VARIABLE HORA OBTIENE LA FECHA ACTUAL
                hora = time.strftime('%Y-%m-%d')
                # crea una nueva instancia del modelo tb_DetalleArticulo para realizar un registro
                new_detalle_articulo = tb_DetalleArticulo(
                    valor=request.POST['valor'],
                    codigo_barras=request.POST['codigo_barras'],
                    numero_referencia="1",
                    precio_unitario=request.POST['precio_unitario'],
                    garantia=request.POST['garantia'],
                    especificaciones=request.POST['especificaciones'],
                    estado="activo",
                    fecha_ingreso=hora,
                    fecha_compra=datetime.datetime.strptime(request.POST['fecha_compra'], "%m/%d/%Y"),
                    unidades=request.POST['unidades'],
                    nivel=request.POST['nivel'],
                    estante=request.POST['estante'],
                    cod_articulo=tb_Articulo.objects.get(id=request.POST['cod_articulo']),
                    estado_det_art="activo",
                    usuario_regis=request.user

                )
                # REGISTRA UN NUEVO DETALLE DE ARTICULO
                new_detalle_articulo.save(form)

                # mediante esta declaracion de realiza una actualizacion en la tabla articulos
                # para aumentar las existencias de ese articulo
                articulo = tb_Articulo.objects.get(id=request.POST['cod_articulo'])
                articulo.existencia = F('existencia') + request.POST['unidades']
                # SALVA EL UPDATE QUE SE ACABA DE REALIZAR EN LOS ARTICULOS, ACTUALIZANDO LAS EXISTENCIAS
                articulo.save()

                # mediante esta declaracion se inserta un nuevo registro en la tabla entrada
                entrada = tb_entrada(
                    fecha_registro_entrada=hora,
                    cantidad=request.POST['unidades'],
                    codigo_barras=request.POST['codigo_barras'],
                    cod_art=tb_Articulo.objects.get(id=request.POST['cod_articulo']),
                    estado_entrada="activo",
                    usuario_regis=request.user
                )
                # GUARDA UNA NUEVA ENTRADA DE ARTICULOS
                entrada.save()
                # SI TODOS HA SALIDA BIEN, RETORNA UN MENSAJE CONFIRMANDO LA INSERCCION
                messages.success(request, "REGISTRADO EXITOSAMENTE")
            return redirect("/add_post")


    else:
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_DetalleArtForm()
    # RETORNA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'nuevo_detalle_articulo.html', {'form': form})


# ===========================   NUEVO MOBILIARIO ============================================================
# ESTA VISTA REALIZA LA FUNCION DE INGRESAR UN NUEVO MOBILIARIO
@login_required()
def nuevoMobiliario(request):
    # PRIMERA VALIDACION, SI EL METODO ES POST PASA
    if request.method == "POST":
        # NUEVA ISNTANCIA DE FORMULARIO
        form = Tb_MobiliarioForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            # nuevo cursor
            cur = connection.cursor()
            codigo = request.POST['cod_inventario']

            # llamada a procedimiento almacenado
            cur.execute("select verificacodinventario(%s);", (codigo,))
            row = cur.fetchone()
            newID = row[0]
            # cierra la conexcion a la bd
            cur.close()
            # SI LA RESPUESTA ES 1 QUIERE DECIR QUE EL CODIGO INGRESADO YA EXISTE
            if newID == 1:
                # RETORNA UN MENSAJE DE ALERA DE QUE EL CODIGO DE INVENTARIO YA EXISTE
                messages.success(request, "CODIGO DE INVENTARIO YA EXISTE")
                return redirect("/add_post")
            else:
                # crea una nueva instancia del modelo tb_Mobiliario para realizar un registro
                new_mobiliari = tb_Mobiliario(
                    marca=request.POST['marca'],
                    modelo=request.POST['modelo'],
                    serie=request.POST['serie'],
                    color=request.POST['color'],
                    estado="disponible",
                    cod_inventario=request.POST['cod_inventario'],
                    observacion=request.POST['observacion'],
                    costo_uni=request.POST['costo_uni'],
                    descripccion=request.POST['descripccion'],
                    anio_modelo=request.POST['anio_modelo'],
                    fecha_registro=datetime.datetime.strptime(request.POST['fecha_registro'], "%m/%d/%Y"),
                    imagen=request.FILES['imagen'],
                    cod_cat_mobiliario=tb_CategoriaMobiliario.objects.get(id=request.POST['cod_cat_mobiliario_id']),
                    estado_mobiliario="activo",
                    usuario_regis=request.user,
                    ubicacion_actual=""

                )  # REGISTRA UN NUEVO MOBILIARIO
                new_mobiliari.save()
                # SI SALIO BIEN REGRESA A LA PAGINA PRINCIPAL Y MUESTRA UN MENSAJE CONFIRMADO QUE SE REGISTRO EXITOSAMENTE
                messages.success(request, "REGISTRADO EXITOSAMENTE")
                return redirect("/add_post")



    else:
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_MobiliarioForm()
    # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'nuevo_mobiliario.html', {'form': form})


# ========================= ASIGNAR MOBILIARIO ============================
# ESTA VISTA SIRVE PARA ASIGNAR UN MOBILIARIO A UN EMPLEADO
@login_required()
def asignarMobiliario(request):
    # SI EL METODO ES POST PASA
    if request.method == "POST":
        # NUEVA INSTANCIA DE FORMULARIO BASADO EN Tb_MobiliarioPrestadoForm
        form = Tb_MobiliarioPrestadoForm(request.POST or None, request.FILES or None)

        # establece conexion a la bd
        cur = connection.cursor()
        codigo = request.POST['cod_empleado']

        # llamada a procedimiento almacenado
        cur.execute("select verificacodempleado(%s);", (codigo,))
        # recupera el valor del procedimiento almacenado
        row = cur.fetchone()
        newID = row[0]
        # cierra la conexcion a la bd
        cur.close()

        # =================================================================================================================
        # establece conexion a la bd
        cur = connection.cursor()

        codigo = request.POST['cod_mobiliario']

        # llamada a procedimiento almacenado
        cur.execute("select verificacodmobiliario(%s);", (codigo,))
        # recupera el valor del procedimiento almacenado
        row2 = cur.fetchone()
        newID2 = row2[0]
        # cierra la conexcion a la bd
        cur.close()

        # =====================================================================================================
        # NUEVO ARRAY DE MOBILIARIO
        mobi_usado = tb_Mobiliario.objects.filter(id=request.POST['cod_mobiliario']).values("estado")
        for sub in mobi_usado:
            for key in sub:
                sub[key] = sub[key]
                disponibilidad = sub[key]
        # SI LA RESPUESTA ES CERO EL CODIGO DE EMPLEADO YA SE ENCUENTRA EN EL SISTEMA
        if newID == 0:
            # REGRESA UN MENSAJE DE ERROR
            messages.error(request, "CODIGO DE EMPLEADO NO EXISTE")
        # SI LA RESPUESTA ES CERO EL CODIGO DE MOBILIARIO NO EXISTE
        elif newID2 == 0:
            # REGRESA UN MENSAJE DE ERROR
            messages.error(request, "CODIGO DE MOBILIARIO NO EXISTE")
        elif disponibilidad == "ocupado":

            # validar que el mobiliario no esta en uso
            # mobi_usado = tb_Mobiliario.objects.get(id=tb_Mobiliario.objects.filter(id=request.POST['cod_mobiliario']))
            messages.error(request, "ESTE MOBILIARIO YA SE ENCUENTRA ASIGNAGO")
        else:
            # SI EL FORMULARIO ES VALIDO DE ACUERDO AL HTML ENTONCES PASA
            if form.is_valid():
                try:
                    # NUEVA INSTANCIA DE MOBILIARIO PRESTADO
                    new_asig_mobi = tb_MobiliarioPrestado(
                        fecha_prestado=datetime.datetime.strptime(request.POST['fecha_prestado'], "%m/%d/%Y"),
                        estado=request.POST['estado'],
                        descripccion=request.POST['descripccion'],
                        gerencia=request.POST['gerencia'],
                        departamento=request.POST['departamento'],
                        levanto_inventario=request.POST['levanto_inventario'],
                        telefono=request.POST['telefono'],
                        cod_empleado=tb_Empleado.objects.get(id=request.POST['cod_empleado']),
                        cod_mobiliario=tb_Mobiliario.objects.get(id=request.POST['cod_mobiliario']),
                        estado_mp="activo",
                        usuario_regis=request.user

                    )
                    # REALIZA LA INSERCION
                    new_asig_mobi.save()
                    # NUEVA INSTANCIA DE TIPO MOBILIARIO, REALIZA UN UPDATE
                    mobiliario = tb_Mobiliario.objects.get(id=request.POST['cod_mobiliario'])
                    mobiliario.estado = request.POST['estado']
                    mobiliario.ubicacion_actual = request.POST['gerencia']
                    # SALVA LAACTUALIZACION EN LA TABLA MOBILIARIO
                    mobiliario.save()
                    messages.success(request, "REGISTRADO EXITOSAMENTE")
                    codigo_b = "true"
                    fecha_prestado = datetime.datetime.strptime(request.POST['fecha_prestado'], "%m/%d/%Y")

                    descripccion = request.POST['descripccion']
                    gerencia = request.POST['gerencia'],
                    departamento = request.POST['departamento']
                    levanto_inventario = request.POST['levanto_inventario']
                    telefono = request.POST['telefono']
                    cod_empleado = tb_Empleado.objects.all().filter(id=request.POST['cod_empleado'])

                    cod_mobiliario = tb_Mobiliario.objects.all().filter(id=request.POST['cod_mobiliario'])
                    return render(request, "asignar_mobiliario.html",
                                  {'codigo_boton': codigo_b, 'cod_empleado': cod_empleado, 'fecha_p': fecha_prestado,
                                   'gerencia': gerencia, 'mobiliario': cod_mobiliario})


                except Exception:
                    messages.error(request, "VERIFIQUE LOS CAMPOS CODIGO DE EMPLEADO Y DE MOBILIARIO")



    else:
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_MobiliarioPrestadoForm()
    # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'asignar_mobiliario.html', {'form': form})


# ================================ ASIGNAR MOBILIARIO ============================================

@login_required()
# ESTA FUNCION SIRVE PARA REALIZAR DESCARGAS DE LOS MOBILIARIOS A LOS EMPLEADOS
def descargarMobiliario(request):
    # SI EL METODO ES POST PASA LA VALIDACION
    if request.method == "POST":
        # NUEVA INSTANCIA DE FORMULARIO  Tb_DescargarMobiliarioForm
        form = Tb_DescargarMobiliarioForm(request.POST or None, request.FILES or None)
        # establece conexion a la bd
        cur = connection.cursor()
        codigo = request.POST['cod_empleado']
        # llamada a procedimiento almacenado
        cur.execute("select verificacodempleado(%s);", (codigo,))
        # recupera el valor del procedimiento almacenado
        row = cur.fetchone()
        newID = row[0]
        # cierra la conexcion a la bd
        cur.close()

        # =================================================================================================================

        # establece conexion a la bd
        cur = connection.cursor()
        codigo = request.POST['cod_mobiliario']
        # llamada a procedimiento almacenado
        cur.execute("select verificacodmobiliario(%s);", (codigo,))
        # recupera el valor del procedimiento almacenado
        row2 = cur.fetchone()
        newID2 = row2[0]
        # cierra la conexcion a la bd
        cur.close()

        # =====================================================================================================
        # EN CASO DE QUE SEA CERO EL CODIGO DE EMPLEADO NO EXISTE
        if newID == 0:
            # REGRESA UN MENSAJE DE ERROR
            messages.error(request, "CODIGO DE EMPLEADO NO EXISTE")
        # EN CASO DE QUE LA RESPUESTA SEA CERO EL CODIGO DE MOBILIARIO NO EXISTE
        elif newID2 == 0:
            # REGRESA UN MENSAJE DE ERROR
            messages.error(request, "CODIGO DE MOBILIARIO NO EXISTE")
        else:
            # SI EL FORMULARIO ES VALIDO RESPECTO AL HTML ENTONCES SE PUEDE REALIZAR LA OPERACION
            if form.is_valid():
                try:
                    # NUEVA INSTACIA DE MOBILIARIO DEVUELTO
                    new_descargar_mobi = tb_MobiliarioDevuelto(
                        fecha_devolucion=datetime.datetime.strptime(request.POST['fecha_devolucion'], "%m/%d/%Y"),
                        estado=request.POST['estado'],
                        descripccion=request.POST['descripccion'],

                        cod_empleado=tb_Empleado.objects.get(id=request.POST['cod_empleado']),
                        cod_mobiliario=tb_Mobiliario.objects.get(id=request.POST['cod_mobiliario']),
                        estado_md="activo",
                        usuario_regis=request.user

                    )
                    # REALIZA LA OPERACION DE INSERTAR EN TB_MOBILIARIODEVUELTO
                    new_descargar_mobi.save(form)
                    # NUEVA INSTANCIA DE MOBILIARIO Y CAMBIA EL ESTADO A DISPONIBLE
                    mobiliario = tb_Mobiliario.objects.get(id=request.POST['cod_mobiliario'])
                    mobiliario.estado = "disponible"
                    # SALVA EL UPDATE DE MOBILIARIO
                    mobiliario.save()
                    # NUEVA INSTANCIA DE MOBILIARIO PRESTADO Y UPDATE

                    mobiprest = tb_MobiliarioPrestado.objects.get(
                        id=tb_MobiliarioPrestado.objects.filter(cod_mobiliario=request.POST['cod_mobiliario'],
                                                                estado="ocupado"),
                        cod_empleado=request.POST['cod_empleado'])
                    mobiprest.estado = "devuelto"
                    # SALVA EL UPDATE EN MOBILIARIO PRESTADO
                    mobiprest.save()
                    # SI HA SALIDO BIEN MUESTRA UN MENSAJE DE CONFIRMACION Y RETORNA A LA PAGINA PRINCIPAL
                    messages.success(request, "REGISTRADO EXITOSAMENTE")
                    return redirect("/add_post")

                except Exception:
                    # MUESTRA UN MENSAJE DE ERROR
                    messages.error(request, "VERIFIQUE LOS CAMPOS CODIGO DE EMPLEADO Y DE MOBILIARIO")




    else:
        # NUEVA INSTANCIA DE FORMULARIO Tb_DescargarMobiliarioForm
        form = Tb_DescargarMobiliarioForm
    # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'descargar_mobiliario.html', {'form': form})


# ============================================== REGISTRAR NUEVA SALIDA ===========================================
@login_required()
# ESTA VISTA SIRVE PARA REALIZAR UNA NUEVA SALIDA, EL PROCESO DE SALIDA CONSUME DOS VISTAS, ESTA ES LA PRIMERA DE LAS DOS
def nuevaSalida(request):
    if request.method == "POST":
        # establece conexion a la bd
        cur = connection.cursor()

        codigo = request.POST['codigo_barras']
        # llamada a procedimiento almacenado
        cur.execute("select retornacodbarras(%s);", (codigo,))
        # recupera el valor del procedimiento almacenado
        row = cur.fetchone()
        newID = row[0]
        # cierra la conexcion a la bd
        cur.close()

        # llamada a procedimiento almacenado de verificar existencias
        cur = connection.cursor()
        cur.execute("select verifica_existencias_detallearticulo(%s);", (codigo,))
        rowc = cur.fetchone()
        valor_cod = rowc[0]
        cur.close
        # NUEVA INSTANCIA DE FORMULARIO Tb_SalidaForm
        form = Tb_SalidaForm(request.POST or None, request.FILES or None)
        # MANEJA LAS EXISTENCIAS REALES
        exis_real = 0
        existencia = int(request.POST['cantidad'])
        existencia_real = tb_DetalleArticulo.objects.filter(codigo_barras=request.POST['codigo_barras']).values(
            "unidades")
        # recupera las existencias reales de el articulo

        for sub in existencia_real:
            for key in sub:
                sub[key] = int(sub[key])
                exis_real = sub[key]

        # si la el procedimiento almacenado retorna 0 entonces no exisste el codigo de barras
        # luego este pasa por un filtro en los if para corroborrarlo
        if newID == 0:
            # MUESTA MENSAJE DE ERROR
            messages.error(request, 'CODIGO DE BARRAS NO EXISTE, INTENTE NUEVAMENTE')

        # si la existencia real es mayor a la que se requiere, deja continuar con la solicitud
        elif valor_cod == 0:
            # MUESTA MENSAJE DE ERROR
            messages.error(request, 'NO EXISTEN EXISTENCIAS DE ESTE ARTICULO')
        # SI LA EXISTENCIA ENVIADA ES MAYOR QUE LA REAL DEVUELVE UN MENSAJE DE ERROR DANDO LA ADVERTENCIA
        elif existencia > exis_real:
            messages.error(request, 'LA CANTIDAD A ENVIAR SOBREPASA LAS EXISTENCIAS')

        else:
            # SI EL FORMULARIO CUMPLE LOS REQUISITOS PASA
            if form.is_valid():
                try:

                    # registra una nueva entrada en la tabla tb_salida
                    # NUEVA INSTANCIA PARA UNA SALIDA
                    new_salida = tb_salida(
                        fecha_registro_salida=datetime.datetime.strptime(request.POST['fecha_registro_salida'],
                                                                         "%m/%d/%Y"),
                        cantidad=request.POST['cantidad'],
                        codigo_barras=request.POST['codigo_barras'],
                        personal_entregado=request.POST['personal_entregado'],
                        usuario_regis=request.user,
                        departamento=tb_Jefatura.objects.get(id=request.POST['departamento']),
                        agencia=Agencia.objects.get(id=request.POST['agencia']),
                        cod_det_art=tb_DetalleArticulo.objects.get(
                            id=tb_DetalleArticulo.objects.filter(codigo_barras=request.POST['codigo_barras'])),
                        estado_salida="activo"

                    )
                    # REGISTRA LA NUEVA SALIDA
                    new_salida.save(form)
                    # recupera el codigo del detalle del articulo
                    id_art = tb_DetalleArticulo.objects.filter(codigo_barras=request.POST['codigo_barras']).values(
                        'cod_articulo')
                    # recupera el codigo del articulo, una vez que se ha recuperado entonces realiza un update a la tabla articulo
                    # el update es para descargar unidades del inventario
                    articulo = tb_Articulo.objects.get(id=id_art)
                    articulo.existencia = F('existencia') - request.POST['cantidad']
                    articulo.save()
                    # recupera el id del detalle articulo y luego realiza un update a la tabla detalle articulo para descargar las unidades
                    # del inventario
                    detalle_art = tb_DetalleArticulo.objects.get(
                        id=tb_DetalleArticulo.objects.filter(codigo_barras=request.POST['codigo_barras']))
                    detalle_art.unidades = F('unidades') - request.POST['cantidad']
                    detalle_art.save()

                    # regresa a la pagina de inicio si ha realizado un registro exitoso

                    messages.success(request, "REGISTRADO EXITOSAMENTE")
                    return redirect("/add_post")
                    # EN CASO DE UNA QUE EL CODIGO DE BARRAS NO EXISTA, RETORNA A LA PAGINA
                except Exception:
                    messages.error(request, 'CODIGO DE BARRAS NO EXISTE, INTENTE NUEVAMENTE')


    else:
        # fin del primer if
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_SalidaForm
    # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'nueva_salida.html', {'form': form})


# ========================================= REGISTRAR NUEVA INCIDENCIA  =========================

@login_required()
# ESTA VISTA REGISTRA UN NUEVO INCIDENTE DE UN ARTICULO
def nuevaIncidenciaArticulo(request):
    # SI EL METODO ES POST ENTONCES PUEDE CONTINUAR
    if request.method == "POST":
        # CREA UNA INSTANCIA DE FORMULARIO DE Tb_IncidenciaArticulo
        form = Tb_IncidenciaArticulo(request.POST or None, request.FILES or None)

        # registra nueva incidencia
        # INSTANCIA DE INCIDENCIA ARTICULO
        incidencia = tb_incidenciaArticulo(
            tipo=request.POST['tipo'],
            descripccion_inc=request.POST['descripccion_inc'],
            fecha_registro_inc=datetime.datetime.strptime(request.POST['fecha_registro_inc'], "%m/%d/%Y"),

            cod_det_art=tb_DetalleArticulo.objects.get(id=request.POST['cod_det_art_id']),
            estado_inc_art="activo",
            usuario_regis=request.user

        )
        # REGISTRA LA NUEVA INCIDENCIA
        incidencia.save(form)
        # SI SALE BIEN ENTONCES MUESTRA UN MENSAJE DE CONFIRMACION
        messages.success(request, "REGISTRADO EXITOSAMENTE")
        return redirect("/add_post")

    else:
        # NUEVA INSTANCIA DE UN FORMULARIO
        form = Tb_IncidenciaArticulo
    # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'registrar_incidencia_articulo.html', {'form': form})


# ================================= NUEVO VEHICULO ========================================

# funcion para pedir datos de sesion
@login_required()
# ESTA VISTA REGISTRA UN NUEVO VEHICULO
def nuevoVehiculo(request):
    # SI EL METODO ES POST CONTINUA
    if request.method == "POST":
        # NUEVA INSTANCIA DE FORMULARIO PARA TB_NUEVOVEHICULO
        form = Tb_NuevoVehiculo(request.POST or None, request.FILES or None)
        if form.is_valid():
            # CREA UNA NUEVA INSTANCIA PARA AGREGAR UN VEHICULO
            new_vehi = tb_Vehiculo(
                marca=request.POST['marca'],
                modelo=request.POST['modelo'],
                color=request.POST['color'],
                serie=request.POST['serie'],
                serie_motor=request.POST['serie_motor'],
                placa=request.POST['placa'],
                estado=request.POST['estado'],
                anio_modelo=request.POST[
                    'anio_modelo'],
                tipo_vehiculo=
                request.POST['tipo_vehiculo'],
                costo=request.POST['costo'],
                descripccion=request.POST['descripccion'],
                observacion=request.POST['observacion'],
                cod_inventario=request.POST['cod_inventario'],
                imagen_vehi=request.FILES['imagen_vehi'],
                estado_vehi="activo", usuario_regis=request.user
            )
            # SALVA UN NUEVO VEHICULO
            new_vehi.save()
            messages.success(request, "REGISTRADO EXITOSAMENTE")
            return redirect("/add_post")

    else:
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_NuevoVehiculo()
    # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'nuevo_vehiculo', {'form': form})


# ============================= ASIGNAR VEHICULO ===================================================
# funcion para pedir datos de sesion
@login_required()
# ESTA VISTA SIRVE PARA ASIGNAR UN VEHICULO A UN EMPLEADO
def asignarVehiculo(request):
    # SI EL METODO ES POST ENTONCES PUEDE CONTINUAR
    if request.method == "POST":
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_NuevoVehiculoAsignado(request.POST or None, request.FILES or None)
        if form.is_valid():
            # CREA UNA INSTANCIA PARA VEHICULO ASIGNADO
            new_vehi = tb_VehiculoAsignado(
                fecha_registro=datetime.datetime.strptime(request.POST['fecha_registro'], "%m/%d/%Y"),
                estado="ocupado",
                descripccion=request.POST['descripccion'],
                cod_empleado=tb_Empleado.objects.get(id=request.POST['cod_empleado_id']),
                cod_vehiculo=tb_Vehiculo.objects.get(id=request.POST['cod_vehiculo_id']),
                estado_vehi_asig="activo", usuario_regis=request.user
            )
            # REGISTRAR UN NUEVO VEHICULO ASIGNADO
            new_vehi.save()
            # CREA UNA NUEVA ISNTANCIA DE VEHICULO Y REALIZA UNA ACTUALIZACION EN EL ESTADO
            vehi = tb_Vehiculo.objects.get(id=request.POST['cod_vehiculo_id'])
            vehi.estado = "ocupado"
            # GUARDA EL UPDATE DEL VEHICULO
            vehi.save()
            messages.success(request, "REGISTRADO EXITOSAMENTE")
            return redirect("/add_post")

    else:
        # NUEVA ISNTANCIA DE FORMULARIO
        form = Tb_MobiliarioForm()
    # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'asignar_vehiculo.html', {'form': form})


# ============================================= DESCARGAR VEHICULO ===============================
@login_required()
# ESTA VISTA SIRVE PARA REALIZAR UNA DESCARGA DE VEHICULO A UN EMPLEADO
def descargarVehiculo(request):
    if request.method == "POST":
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_DescargarVehiculoForm(request.POST or None, request.FILES or None)
        # NUEVA INSTANCIA DE DESCARGA DE VEHICULO
        new_des = tb_VehiculoDescargado(
            fecha_devolucion=datetime.datetime.strptime(request.POST['fecha_devolucion'], "%m/%d/%Y"),
            estado=request.POST['estado'],
            descripccion=request.POST['descripccion'],
            cod_empleado=tb_Empleado.objects.get(id=request.POST['cod_empleado_id']),
            cod_vehiculo=tb_Vehiculo.objects.get(id=request.POST['cod_vehiculo_id']),
            estado_vehi_des="activo", usuario_regis=request.user

        )
        # REGISTRA UNA NUEVA DESCARGA DE VEHICULO
        new_des.save()
        # REALIZA UNA NUEVA ACTUALIZACION EN LA TABLA VEHICULO
        new_vehiculo = tb_Vehiculo.objects.get(id=request.POST['cod_vehiculo_id'])
        new_vehiculo.estado = "disponible"
        new_vehiculo.save()
        # REALIZA UNA MODIFICACION A LA TABLA VEHICULO ASIGNADO
        new_descar_vehi = tb_VehiculoAsignado.objects.get(
            id=tb_VehiculoAsignado.objects.filter(cod_vehiculo=request.POST['cod_vehiculo_id'], estado="ocupado",
                                                  cod_empleado=request.POST['cod_empleado_id']))
        new_descar_vehi.estado = "devuelto"
        new_descar_vehi.save()
        # MUESTRA UN MENSAJE DE CONFIRMACION QUE HA SALIDO BIEN
        messages.success(request, "REGISTRADO EXITOSAMENTE")
        return redirect("/add_post")

    else:
        # NUEVA INSTANCIA DE UN FORMULARIO
        form = Tb_DescargarVehiculoForm()
        # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'descargar_vehiculo.html', {'form': form})


# =========================== NUEVO INMUEBLE

@login_required()
def nuevoInmueble(request):
    # SI EL METODO ES POST PUEDE CONTINUAR
    if request.method == "POST":
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_NuevoInmuebleForm(request.POST or None, request.FILES or None)
        # NUEVA INSTANCIA PARA REGISTRA UN NUEVO INMUEBLE
        new_inmueble = tb_Inmueble(
            ubicacion=request.POST['ubicacion'],
            destino_actual=request.POST['destino_actual'],
            numero_instrumento=request.POST['numero_instrumento'],
            fecha_otorgamiento=datetime.datetime.strptime(request.POST['fecha_otorgamiento'], "%m/%d/%Y"),
            notario_otorgante=request.POST['notario_otorgante'],
            otorgante=request.POST['otorgante'],
            valor_adq=request.POST['valor_adquisicion'],
            forma_adquisicion=request.POST['forma_adquisicion'],
            fecha_acuerdo=datetime.datetime.strptime(request.POST['fecha_acuerdo'], "%m/%d/%Y"),
            observaciones=request.POST['observaciones'],
            num_registro_propiedad=request.POST['num_registro_propiedad'],
            folio_registro_propiedad=request.POST['folio_registro_propiedad'],
            tomo_registro_propiedad=request.POST['tomo_registro_propiedad'],
            num_catastro=request.POST['num_catastro'],
            estado_inmueble="activo",
            usuario_regis=request.user,
            estado="disponible",
            ciudad=request.POST['ciudad']
        )
        # REGISTRA UN NUEVO INMUEBLE
        new_inmueble.save()
        # MENSAJE DE CONFIRMACION QUE SALIO BIEN EL REGISTRO
        messages.success(request, "REGISTRADO EXITOSAMENTE")
        return redirect("/add_post")

    else:
        # NUEVA INSTANCIA DE INMUEBLE
        form = Tb_NuevoInmuebleForm()
        # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'nuevo_inmueble.html', {'form': form})


# ====================================== ASIGNAR INMUEBLE ==============================
@login_required()
# ESTA VISTA SIRVE PARA ASIGNAR UN INMUBELE A UN EMPLEADO
def asignarInmueble(request):
    # SI EL METODO ES POST PUEDE CONTINUAR
    if request.method == "POST":
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_AsignarInmuebleForm(request.POST or None, request.FILES or None)

        new_asig_inm = tb_Admin_Inmueble(
            fecha_registro=datetime.datetime.strptime(request.POST['fecha_prestado'], "%m/%d/%Y"),
            cod_empleado=tb_Empleado.objects.get(id=request.POST['cod_empleado']),
            cod_inmueble=tb_Inmueble.objects.get(id=request.POST['cod_inmueble']),
            estado_admin_inmueble="activo",
            usuario_regis=request.user,
            estado="ocupado",
            descripcion=request.POST['descripcion']
        )
        # REGISTRA UNA NUEVA ASIGNACION DE INMUEBLE
        new_asig_inm.save()
        # REALIZA UNA ACTUALIZACION DEL ESTADO DEL INMUEBLE
        new_inmueble_update = tb_Inmueble.objects.get(id=request.POST['cod_inmueble'])
        new_inmueble_update.estado = "ocupado"
        new_inmueble_update.save()
        # MUESTRA UN MENSAJE DE CONFIRMACION
        messages.success(request, "REGISTRADO EXITOSAMENTE")
        return redirect("/add_post")


    else:
        ##CREA UNA NUEVA INSTANCIA DE FORMULARIO
        form = Tb_AsignarInmuebleForm()
    # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'asignar_inmueble.html', {'form': form})


# DESCARGAR INMUEBLE

@login_required()
# ESTA VISTA SIRVE PARA REALIZAR UNA DESCARGA DE UN INMUEBLE
def descargarInmueble(request):
    # SI EL METODO ES POST PUEDE CONTINUAR
    if request.method == "POST":
        # NUEVA ISNTANCIA DE FORMULARIO
        form = Tb_DescargarInmueble(request.POST or None, request.FILES or None)
        # NUEVA INSTANCIA PARA DESCARGAR UN INMUEBLE
        new_des = tb_InmuebleDescargado(
            fecha_devolucion=datetime.datetime.strptime(request.POST['fecha_devolucion'], "%m/%d/%Y"),
            estado="devuelto",
            descripccion=request.POST['descripccion'],
            usuario_regis=request.user,
            cod_empleado=tb_Empleado.objects.get(id=request.POST['cod_empleado_id']),
            cod_inmueble=tb_Inmueble.objects.get(id=request.POST['cod_inmueble_id'])

        )
        # REGISTRA UNA NUEVA DESCARGA DE INMUEBLE
        new_des.save()
        # INSTANCIA PARA REALIZAR UNA ACTUALIZACION SOBRE EL ESTADO DEL INMUEBLE
        update_admin = tb_Admin_Inmueble.objects.get(
            id=tb_Admin_Inmueble.objects.filter(cod_inmueble=request.POST['cod_inmueble_id'], estado="ocupado",
                                                cod_empleado=request.POST['cod_empleado_id']))
        update_admin.estado = "devuelto"
        update_admin.save()

        update_inmueble = tb_Inmueble.objects.get(id=request.POST['cod_inmueble_id'])
        update_inmueble.estado = "disponible"
        update_inmueble.save()
        # MENSAJE DE CONFIRMACION QUE SE REGISTRO EXISTOSAMENTE
        messages.success(request, "REGISTRADO EXITOSAMENTE")
        return redirect("/descargarInmuebleLista")

    else:
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_DescargarInmueble()
    # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'descargar_inmueble.html')


# DETALLE DE SALIDAS, REALIZA LAS SALIDAS DEL ALMACEN
@login_required()
# ESTA VISTA SIRVE PARA REGISTAR UN NUEVO DETALLE DE SALIDA DEL ALMANCEN
def detalleSalida(request):
    # SI EL METODO ES GET Y EL PARAMETRO FLAT ES IGUAL A TRUE, ENTONCES PUEDE CONTINUAR
    if request.GET.get('flat') == "true":
        form = Tb_NuevoDetalleSalida(request.POST or None, request.FILES or None)
        # objetos a enviar
        resultado = tb_salida.objects.all()
        # DEVUELVE LA FECHA ACTUAL
        hora = time.strftime('%Y-%m-%d')
        try:
            if request.GET.get('flat') == "true":
                # NUEVA INSTANCIA DE SALIDA
                new_salida = tb_salida(fecha_registro_salida=hora, usuario_regis=request.user)
                new_salida.save()
                # NUEVA CONEXCION A LA BD
                cur = connection.cursor()
                # EJECUTA EL SQL
                cur.execute("select count(*)from inventariohonducorapp_tb_salida;")
                rowc = cur.fetchone()
                valor_cod = rowc[0]
                # CIERRA LA CONEXION
                cur.close
                codigo = valor_cod
                # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
                return render(request, 'nuevo_detalle_salida_get.html', {'form': form, 'codigo': codigo})

        except Exception:
            hora = time.strftime('%Y-%m-%d')

    else:
        # NUEVA ISNTANCIA DE FORMUARIO
        form = Tb_NuevoDetalleSalida()
    # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'nuevo_detalle_salida_get.html')


# DETALLE DE SALIDA
@login_required()
# VISTA PARA REALIZAR UNA SALIDA, ESTA ES LA SEGUNDA PARTE, YA QUE SE UTILIZAN DOS VISTAS PARA PODER REALIZAR LA TRANSACCION

def nuevoDetalleSalida2(request):
    bandera = request.GET.get('flag')
    # EN CASO DE QUE EL PARAMETRO DEVUELTO POR METODO GET SEA IGUAL A ELIMINAR, ENTONCES SE PUEDE EJECUTAR LA TRANSACCION
    if bandera == "eliminar":
        try:
            # NUEVA ISNTANCIA PARA ELIMINAR EL DETALLE DE UNA SALIDA
            delete_salida = tb_detalle_salida.objects.get(id=request.GET.get('cod_det_salida'))
            # ELIMINA UN DETALLE DE SALIDA
            delete_salida.delete()
            # ==================================================================================
            # recupera el codigo del detalle del articulo
            id_art = tb_DetalleArticulo.objects.filter(codigo_barras=request.GET.get('cod_barrasE')).values(
                'cod_articulo')
            # recupera el codigo del articulo, una vez que se ha recuperado entonces realiza un update a la tabla articulo
            # el update es para descargar unidades del inventario
            articulo = tb_Articulo.objects.get(id=id_art)
            articulo.existencia = F('existencia') + request.GET.get('cantidadE')
            # ACTUALIZA LAS EXISTENCIAS DE LOS ARTUCULOS
            articulo.save()
            # recupera el id del detalle articulo y luego realiza un update a la tabla detalle articulo para descargar las unidades
            # del inventario
            detalle_art = tb_DetalleArticulo.objects.get(
                id=tb_DetalleArticulo.objects.filter(codigo_barras=request.GET.get('cod_barrasE')))
            detalle_art.unidades = F('unidades') + request.GET.get('cantidadE')
            # ACTUALIZA LAS EXISTENCIAS DE LOS DETALLES DE ARTICULSO
            detalle_art.save()

            # ==================================================================================
            # VARIABLES PARA ENVIAR AL FORMULARIO CON INFORMACION SOBRE EL DETALLE DE SALIDAS QUE SE ESTA REALIZANDO
            articulo_send = tb_Articulo.objects.all()
            detalle_art_send = tb_DetalleArticulo.objects.all()
            codigo_s4 = request.GET.get('cod_salida')
            salidas = tb_detalle_salida.objects.filter(cod_salida_id=codigo_s4)
            return render(request, 'nuevo_detalle_salida.html',
                          {'salidas': salidas, 'articulos': articulo_send, 'detalle_art': detalle_art_send})
        except Exception:
            # VARIABLES PARA ENVIAR AL FORMULARIO CON INFORMACION SOBRE EL DETALLE DE LAS SALIDAS QUE SE ESTA REALIZANDO
            articulo_send = tb_Articulo.objects.all()
            detalle_art_send = tb_DetalleArticulo.objects.all()
            codigo_s4 = request.GET.get('cod_salida')
            salidas = tb_detalle_salida.objects.filter(cod_salida_id=codigo_s4)
            return render(request, 'nuevo_detalle_salida.html',
                          {'salidas': salidas, 'articulos': articulo_send, 'detalle_art': detalle_art_send})
    # EN CAOS DE QUE EL METODO SEA GET ENTONCES PUEDE CONTINUAR
    elif request.method == "GET":
        codigo = request.GET.get('cod_salida')
    # primer try, VERIFICA LOS CODIGOS DE SALIDAS Y DE BARRAS
    try:
        codigo_s = request.GET.get('cod_salida')
        codigo_b = request.GET.get('cod_barras')
        # valida que el codigo de barras si exista
        # primer if
        if codigo_b != None:

            # establece conexion a la bd
            cur = connection.cursor()
            # cur.callproc("retornacodbarras", (codigo,))
            # llamada a procedimiento almacenado
            cur.execute("select retornacodbarras(%s);", (codigo_b,))
            # recupera el valor del procedimiento almacenado
            row = cur.fetchone()
            valida_cod_barras = row[0]
            # cierra la conexcion a la bd
            cur.close()
            # RECUPERA LA EXISTENCIA REAL EN EL SISTEMA
            existencia_real = tb_DetalleArticulo.objects.filter(codigo_barras=request.GET.get('cod_barras')).values(
                "unidades")

            for sub in existencia_real:
                for key in sub:
                    sub[key] = int(sub[key])
                    exis_real = sub[key]

            existencia = int(request.GET.get('cantidad'))

            # primer if | primer if
            # VALIDA QUE EL CODIGO DE BARRAS EXISTE EN CASO CONTRARIO ENVIA UN MENSAJE CON EL TIPO DE ERROR A CORREGIR
            if valida_cod_barras == 0:
                articulo_send = tb_Articulo.objects.all()
                detalle_art_send = tb_DetalleArticulo.objects.all()
                codigo_s1 = request.GET.get('cod_salida')
                salidas = tb_detalle_salida.objects.filter(cod_salida=codigo_s1)
                messages.error(request, "EL CODIGO DE BARRAS ES INCORRECTO")

                return render(request, 'nuevo_detalle_salida.html',
                              {'salidas': salidas, 'articulos': articulo_send, 'detalle_art': detalle_art_send})
            # VERIFICA QUE LA EXISTENCIA QUE SE SOLICITA NO SEA MAYOR A LA REAL, CASO CONTRARIO ENVIA UN MENSAJE CON EL ERROR A CORREGIR
            elif existencia > exis_real:
                articulo_send = tb_Articulo.objects.all()
                detalle_art_send = tb_DetalleArticulo.objects.all()
                codigo_s2 = request.GET.get('cod_salida')
                salidas = tb_detalle_salida.objects.filter(cod_salida=codigo_s2)
                messages.error(request, "LA CANTIDAD A ENVIAR SOBREPASA LA EXISTENCIA REAL")
                return render(request, 'nuevo_detalle_salida.html',
                              {'salidas': salidas, 'articulos': articulo_send, 'detalle_art': detalle_art_send})

            else:
                codigo = request.GET.get('cod_salida')
                # aqui se va con un try
                hora = time.strftime('%Y-%m-%d')

                try:
                    # NUEVA INSTANCIA PARA DETALLE DE SALIDA
                    new_det_salida = tb_detalle_salida(
                        fecha_registro_salida=hora,
                        cantidad=request.GET.get('cantidad'),
                        codigo_barras=request.GET.get('cod_barras'),
                        personal_entregado=request.GET.get('personal_recibe'),
                        usuario_regis=request.user,
                        estado_salida="activo",
                        agencia=request.GET.get('agencia'),
                        cod_det_art=tb_DetalleArticulo.objects.get(
                            id=tb_DetalleArticulo.objects.filter(codigo_barras=request.GET.get('cod_barras'))),
                        cod_salida=tb_salida.objects.get(id=request.GET.get('cod_salida')),
                        departamento=request.GET.get('departamento')

                    )  # REGISTRA UN NUEVO DETALLE DE SALIDA
                    new_det_salida.save()
                    # recupera el codigo del detalle del articulo
                    id_art = tb_DetalleArticulo.objects.filter(codigo_barras=request.GET.get('cod_barras')).values(
                        'cod_articulo')
                    # recupera el codigo del articulo, una vez que se ha recuperado entonces realiza un update a la tabla articulo
                    # el update es para descargar unidades del inventario
                    articulo = tb_Articulo.objects.get(id=id_art)
                    articulo.existencia = F('existencia') - request.GET.get('cantidad')
                    articulo.save()
                    # recupera el id del detalle articulo y luego realiza un update a la tabla detalle articulo para descargar las unidades
                    # del inventario
                    detalle_art = tb_DetalleArticulo.objects.get(
                        id=tb_DetalleArticulo.objects.filter(codigo_barras=request.GET.get('cod_barras')))
                    detalle_art.unidades = F('unidades') - request.GET.get('cantidad')
                    detalle_art.save()
                    # REGRESA UN MENSAJE DE CONFIRMACION
                    messages.success(request, "REGISTRADO EXITOSAMENTE")
                    # VARIABLES CON LOS DETALLES DE SALIDAS QUE SE ESTAN CARGANDO EN LOS FORMULARIOS
                    articulo_send = tb_Articulo.objects.all()
                    detalle_art_send = tb_DetalleArticulo.objects.all()
                    salidas = tb_detalle_salida.objects.filter(cod_salida=codigo)
                    return render(request, 'nuevo_detalle_salida.html',
                                  {'salidas': salidas, 'articulos': articulo_send, 'detalle_art': detalle_art_send})
                except Exception:
                    # VARIABLES CON LOS DETALLES DE SALIDAS QUE SE ESTAN CARGANDO EN LOS FORMULARIO
                    articulo_send = tb_Articulo.objects.all()
                    detalle_art_send = tb_DetalleArticulo.objects.all()
                    codigo_s4 = request.GET.get('cod_salida')
                    salidas = tb_detalle_salida.objects.filter(cod_salida_id=codigo_s4)
                    return render(request, 'nuevo_detalle_salida.html',
                                  {'salidas': salidas, 'articulos': articulo_send, 'detalle_art': detalle_art_send})


    except:
        # VARIABLES CON LOS DETALLES DE SALIDAS QUE SE ESTAN CARGANDO EN LOS FORMULARIO
        articulo_send = tb_Articulo.objects.all()
        detalle_art_send = tb_DetalleArticulo.objects.all()
        codigo_s4 = request.GET.get('cod_salida')
        salidas = tb_detalle_salida.objects.filter(cod_salida_id=codigo_s4)
        return render(request, 'nuevo_detalle_salida.html',
                      {'salidas': salidas, 'articulos': articulo_send, 'detalle_art': detalle_art_send})

    else:
        # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
        return render(request, 'nuevo_detalle_salida.html')


# ============================================================================== MODIFICAR ===========================================

# ================================================================================MODIFICAR ARTICULO
# VISTA PARA MODIFICAR ARTICULOS
@login_required()
def ModificarArticulo2(request):
    # SI EL METODO ES POST PUEDE CONTINUAR
    if request.method == "POST":
        try:
            # NUEVA INSTANCIA DE FORMULARIO
            form = Tb_ModificarArticulo(request.POST or None, request.FILES or None)
            # NUEVA INSTANCIA PARA REALIZAR UNA ACTUALIZACION DE UN ARTICULO
            update_articulo = tb_Articulo.objects.get(id=request.POST['cod_art'])
            update_articulo.nombre_art = request.POST['nombre_art']
            update_articulo.descrip = request.POST['descrip']
            update_articulo.cod_categoria_id = tb_Articulo.objects.get(id=request.POST['cod_categoria'])
            update_articulo.imagen_art = request.FILES['imagen_art']
            update_articulo.usuario_regis = str(request.user)
            update_articulo.save()
            # MENSAJE DE CONFIRMACION
            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarArticulo")

        except:
            # NUEVA INSTANCIA DE FORMULARIO
            form = Tb_ModificarArticulo(request.POST or None, request.FILES or None)
            # NUEVA INSTANCIA PARA ACTUALIZAR UN ARTICULO
            update_articulo = tb_Articulo.objects.get(id=request.POST['cod_art'])
            update_articulo.nombre_art = request.POST['nombre_art']
            update_articulo.descrip = request.POST['descrip']
            update_articulo.cod_categoria_id = tb_Articulo.objects.get(id=request.POST['cod_categoria'])
            update_articulo.usuario_regis = str(request.user)
            update_articulo.save()
            bandera = "soy una bandera"
            # MENSAJE DE CONFIRMACION
            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarArticulo", {'bandera': bandera})


    else:
        # NUEVA INSTANCIA DE FORMULARIO
        form = Tb_ModificarArticulo()
        # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
        return render(request, 'modificar_articulo.html', {'form': form})


# ================================== MODIFICAR MOBILIARIO
#VISTA PARA MODIFICAR MOBILIARIO
@login_required()
def ModificarMobiliario2(request):
    #SI EL METODO ES POST PUEDE CONTINUAR
    if request.method == "POST":
        try:
            #NUEVA INSTANCIA DE FORMULARIO
            form = Tb_ModificarMobiliario(request.POST or None, request.FILES or None)
            #NUEVA INSTANCIA PARA MODIFICAR UN MOBILIARIO
            update_mobiliario = tb_Mobiliario.objects.get(id=request.POST['codigo'])
            update_mobiliario.marca = request.POST['marca']
            update_mobiliario.modelo = request.POST['modelo']
            update_mobiliario.serie = request.POST['serie']
            update_mobiliario.imagen = request.FILES['imagen']
            update_mobiliario.color = request.POST['color']
            update_mobiliario.anio_modelo = request.POST['anio_modelo']
            update_mobiliario.cod_inventario = request.POST['cod_inventario']
            update_mobiliario.costo_uni = request.POST['costo_uni']
            update_mobiliario.descripccion = request.POST['descripccion']
            update_mobiliario.observacion = request.POST['observacion']
            update_mobiliario.cod_categoria_id = tb_CategoriaMobiliario.objects.get(
                id=request.POST['cod_cat_mobiliario_id'])
            update_mobiliario.usuario_regis = str(request.user)
            update_mobiliario.save()
            #MENSAJE DE CONFIRMACION
            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarMobiliario")

        except:
            #NUEVA INSTANCIA PARA MODIFICAR UN MOBILIARIO
            form = Tb_ModificarMobiliario(request.POST or None, request.FILES or None)
            update_mobiliario = tb_Mobiliario.objects.get(id=request.POST['codigo'])
            update_mobiliario.marca = request.POST['marca']
            update_mobiliario.modelo = request.POST['modelo']
            update_mobiliario.serie = request.POST['serie']
            update_mobiliario.color = request.POST['color']
            update_mobiliario.anio_modelo = request.POST['anio_modelo']
            update_mobiliario.cod_inventario = request.POST['cod_inventario']
            update_mobiliario.costo_uni = request.POST['costo_uni']
            update_mobiliario.descripccion = request.POST['descripccion']
            update_mobiliario.observacion = request.POST['observacion']
            update_mobiliario.cod_categoria_id = tb_CategoriaMobiliario.objects.get(
                id=request.POST['cod_cat_mobiliario_id'])
            update_mobiliario.usuario_regis = str(request.user)
            update_mobiliario.save()
            #MENSAJE DE CONFIRMACION
            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarMobiliario")


    else:
        #NUEVA ISNTANCIA DE FORMULARIO
        form = Tb_ModificarMobiliario()
        # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
        return render(request, 'modificar_mobiliario.html', {'form': form})


# ================================================================== MODIFICAR VEHICULOS
@login_required()
#VISTA PARA MODIFICAR UN VEHICULO
def ModificarVehiculo2(request):
    #SI EL METODO ES POST PUEDE CONTINUAR
    if request.method == "POST":
        try:
            #NUEVA INSTANCIA DE FORMULARIO
            form = Tb_ModificarVehiculo(request.POST or None, request.FILES or None)
            update_vehiculo = tb_Vehiculo.objects.get(id=request.POST['codigo'])
            #NUEVA ISNTANCIA PARAMODIFICAR UN VEHICULO
            update_vehiculo.marca = request.POST['marca']
            update_vehiculo.modelo = request.POST['modelo']
            update_vehiculo.color = request.POST['color']
            update_vehiculo.serie = request.POST['serie']
            update_vehiculo.serie_motor = request.POST['serie_motor']
            update_vehiculo.placa = request.POST['placa']
            update_vehiculo.anio_modelo = request.POST['anio_modelo']
            update_vehiculo.costo = request.POST['costo']
            update_vehiculo.cod_inventario = request.POST['cod_inventario']
            update_vehiculo.tipo_vehiculo = request.POST['tipo_vehiculo']
            update_vehiculo.descripccion = request.POST['descripcion']
            update_vehiculo.observacion = request.POST['observacion']
            update_vehiculo.imagen_vehi = request.FILES['imagen_vehi']
            update_vehiculo.usuario_regis = str(request.user)
            update_vehiculo.save()
            #MENSAJE DE CONFIRMACION
            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarVehiculo")

        except Exception:
            form = Tb_ModificarVehiculo(request.POST or None, request.FILES or None)
            update_vehiculo = tb_Vehiculo.objects.get(id=request.POST['codigo'])
            update_vehiculo.marca = request.POST['marca']
            update_vehiculo.modelo = request.POST['modelo']
            update_vehiculo.color = request.POST['color']
            update_vehiculo.serie = request.POST['serie']
            update_vehiculo.serie_motor = request.POST['serie_motor']
            update_vehiculo.placa = request.POST['placa']
            update_vehiculo.anio_modelo = request.POST['anio_modelo']
            update_vehiculo.costo = request.POST['costo']
            update_vehiculo.cod_inventario = request.POST['cod_inventario']
            update_vehiculo.tipo_vehiculo = request.POST['tipo_vehiculo']
            update_vehiculo.descripccion = request.POST['descripcion']
            update_vehiculo.observacion = request.POST['observacion']
            update_vehiculo.usuario_regis = str(request.user)

            update_vehiculo.save()
            hola = 1
            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarVehiculo", {'codigo': hola})

    else:
        #NUAVA ISNTANCIA DE FORMULARIO
        form = Tb_ModificarArticulo()
        # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
        return render(request, 'modificar_vehiculo.html', {'form': form})


# =========================================================================== MODIFICAR INMUEBLE
@login_required()
#VISTA PARA MODIFICAR INMUEBLE
def ModificarInmueble2(request):
    #SI EL METODO ES POST PEUDE CONTINUAR
    if request.method == "POST":
        try:
            #NUEVA ISNTANCIA DE FORMULARIO
            form = Tb_ModificarInmueble(request.POST or None, request.FILES or None)
            #NUEVA INSTANCIA PARA MODIFICA RUN INMUEBLE
            update_inmueble = tb_Inmueble.objects.get(id=request.POST['cod_imb'])
            update_inmueble.ubicacion = request.POST['ubicacion']
            update_inmueble.destino_actual = request.POST['destino_actual']
            update_inmueble.numero_instrumento = request.POST['numero_instrumento']
            update_inmueble.fecha_otorgamiento = datetime.datetime.strptime(request.POST['fecha_otorgamiento'],
                                                                            "%m/%d/%Y")
            update_inmueble.notario_otorgante = request.POST['notario_otorgante']
            update_inmueble.valor_adq = request.POST['valor_adquisicion']
            update_inmueble.forma_adquisicion = request.POST['forma_adquisicion']
            update_inmueble.fecha_acuerdo = datetime.datetime.strptime(request.POST['fecha_acuerdo'], "%m/%d/%Y")
            update_inmueble.observaciones = request.POST['observacion']
            update_inmueble.num_registro_propiedad = request.POST['num_registro_propiedad']
            update_inmueble.folio_registro_propiedad = request.POST['folio_registro_propiedad']
            update_inmueble.tomo_registro_propiedad = request.POST['tomo_registro_propiedad']
            update_inmueble.num_catastro = request.POST['num_catastro']
            update_inmueble.otorgante = request.POST['otorgante']
            update_inmueble.ciudad = request.POST['ciudad']
            update_inmueble.usuario_regis = str(request.user)
            update_inmueble.save()
            #MENSAJE DE CONFIRMACION
            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarInmueble")

        except:
            #MENSAJE DE ERROR
            messages.success(request, "ERROR AL MODIFICAR INMUEBLE")
            return redirect("/modificarInmueble")


    else:
        #NUEVA INSTANCIA DE FORMULARIO
        form = Tb_ModificarInmueble()
        # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
        return render(request, 'modificar_inmueble.html', {'form': form})


# =======================================================================================================
# MODIFICAR ENTRADA
@login_required()
#VISTA PARA MODIFICAR ENTRADA
def ModificarEntrada2(request):
    #SI EL METODO ES POST PUEDE CONTINUAR
    if request.method == "POST":
        try:
            codigo_b = request.POST['codigo']
            # establece conexion a la bd
            cur = connection.cursor()
            # llamada a procedimiento almacenado
            cur.execute("select recupera_unidades_entradas(%s);", (codigo_b,))
            # recupera el valor del procedimiento almacenado
            row = cur.fetchone()
            unidades_viejas = row[0]

            # cierra la conexcion a la bd
            cur.close()
            unidades_nuevas = request.POST['unidades']
            # if unidades_viejas >= unidades_nuevas:
            # cod_articulo2
            #NUEVA INSTANCIA PARA ACTUALIZAR LAS EXISTENCIAS DE LOS ARTICULOS
            update_articulo = tb_Articulo.objects.get(id=request.POST['cod_articulo2'])
            update_articulo.existencia = F('existencia') - unidades_viejas
            update_articulo.usuario_regis = str(request.user)
            update_articulo.save()
            #INSTANCIA PARA ACTUALIZAR LOS DETALLES DE LAS EXISTENCIAS DE LOS ACTICULOS
            update_articulo2 = tb_Articulo.objects.get(id=request.POST['cod_articulo2'])
            update_articulo2.existencia = F('existencia') + unidades_nuevas
            update_articulo2.usuario_regis = str(request.user)
            update_articulo2.save()
            #INSTANCIA PARA ACTUALIZAR LAS ENTRADAS
            update_entrada = tb_DetalleArticulo.objects.get(id=request.POST['codigo'])
            update_entrada.valor = request.POST['valor']
            update_entrada.unidades = request.POST['unidades']
            update_entrada.precio_unitario = request.POST['precio_unitario']
            update_entrada.usuario_regis = str(request.user)
            update_entrada.save()
            #MENSAJE DE CONFIRMACION
            messages. \
                success(request, "LA ENTRADA HA SIDO MODIFICADA EXITOSAMENTE")
            return redirect("/verEntradaModificar")
        except Exception:
            #MENNSAJE DE ERROR
            messages.success(request, "ERROR AL MODIFICAR ENTRADA")
            return redirect("/modificarEntradas2")
    else:
        # REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
        return render(request, 'modificar_entrada.html')


# ========================================================================================================

# ============================================================= DAR DE BAJA
# DAR BAJA MOBILIARIO
@login_required()
#VISTA PARA DAR DE BAJA A UN MOBILIARIO
def DarBajaMobiliario(request):
    try:
        #INSTANCIA PARA CREAR UN UPDATE Y CAMBIAR EL ESTADO
        dar_baja = tb_Mobiliario.objects.get(id=request.GET.get('codigo'))
        dar_baja.estado_mobiliario = "bajado"
        dar_baja.save()
        #MENSAJE DE CONFIRMACION
        messages.success(request, "EL MOBILIARIO FUE DADO DE BAJA")
        return redirect("/bajaMobiliario")

    except:
        #MENSAJE DE ERROR
        messages.success(request, "ERROR AL DAR DE BAJA A MOBILIARIO")
        return redirect("/bajaMobiliario")


# DAR BAJA VEHICULOS
@login_required()
#VISTA PARA DAR DE BAJA A UN VEHICULO
def DarBajaVehiculo(request):
    try:
        #INSTANCIA PARA HACER UNA ACTUALIZACION AL ESTADO DEL VEHICULO Y CAMBIARLO POR BAJADO
        dar_baja = tb_Vehiculo.objects.get(id=request.GET.get('codigo'))
        dar_baja.estado_vehi = "bajado"
        dar_baja.save()
        #MENSAJE DE CONFIRMACION
        messages.success(request, "EL VEHICULO FUE DADO DE BAJA")
        return redirect("/bajaVehiculo")

    except:
        #MENSAJE DE ERROR
        messages.success(request, "ERROR AL DAR DE BAJA A MOBILIARIO")
        return redirect("/bajaVehiculo")


# DAR DE BAJA A UN ARTICULO
@login_required()
#VISTA PARA DAR DE BAJA A UN ARTICULO
def DarBajaArticulo(request):
    try:
        #INSTANCIA PARA ACTUALIZAR EL ESTADO DE UN ARTICULO Y CAMBIARLO POR BAJADO
        dar_baja = tb_Articulo.objects.get(id=request.GET.get('codigo'))
        dar_baja.estado_articulo = "bajado"
        dar_baja.save()
        #MENSAJE DE CONFIRMACION
        messages.success(request, "EL ARTICULO FUE DADO DE BAJA")
        return redirect("/bajaArticulo")

    except:
        #MENSJAE DE ERROR
        messages.success(request, "ERROR AL DAR DE BAJA A MOBILIARIO")
        return redirect("/bajaArticulo")

#LISTVIEW PARA LISTAR LOS DETALLES DE LAS SALIDAS
class ListaSalidaPrueba(ListView):
    model = tb_Inmueble
    template_name = 'nuevo_detalle_salida.html'
    context_object_name = 'inmuebles'


# ============================ CONSULTAS EN FORMULARIOS ===============================
# --------------------------------------------------------------------------------------

# VISTAS DE INMUBLES
#LISTVIEW PARA LISTAR AQUELLOS INMUEBLES QUE SE DESEAN ASIGNAR
class ListarInmuebleAsignar(ListView):
    model = tb_Inmueble
    template_name = 'listar_inmueble_asignar.html'
    context_object_name = 'inmuebles'
    queryset = tb_Inmueble.objects.all().filter(estado="disponible")

#LISTA TODOS LOS INMUEBLES
class ListarInmueble(ListView):
    model = tb_Inmueble
    template_name = 'listar_inmueble_index.html'
    context_object_name = 'inmuebles'
    queryset = tb_Inmueble.objects.all().filter(estado="disponible")

# LISTA LOS EMPLEADOS PARA ASIGNAR UN INMUEBLE
class ListarEmpleadoInmueble(ListView):
    model = tb_Empleado
    template_name = 'buscar_empleado_inmueble.html'
    context_object_name = 'empleado'
    queryset = tb_Empleado.objects.all().order_by('id')

#LISTVIEW PARA LOS INMUEBLES QUE SE DESEA DESCARGAR
class ListarDescargarInmueble(ListView):
    model = tb_Admin_Inmueble
    template_name = 'listar_inmueble_descargar.html'
    context_object_name = 'inmuebles'
    queryset = tb_Admin_Inmueble.objects.filter(estado="ocupado")
    #FUNCION PARA RETORNAR LOS CONTEXTOS DE MOBILIARIOS  Y EMPLEADOS AL TEMPLATE
    def get_context_data(self, **kwargs):
        context = super(ListarDescargarInmueble, self).get_context_data(**kwargs)
        context['mobiliarios'] = tb_Inmueble.objects.all()
        context['empleados'] = tb_Empleado.objects.all()

        return context
#LISTVIEW PARA LISTAR LOS INMUEBLES QUE SE VAN A MODIFICAR
class ListarInmuebleModificar(ListView):
    model = tb_Inmueble
    template_name = 'listar_inmueble_modificar.html'
    context_object_name = 'inmuebles'

# ============================================================FIN DE  VISTAS INMUEBLES

# este listview es para consultar los mobiliarios por agencia
class ListarAgenciasMobiliario(ListView):
    model = Agencia
    template_name = 'buscar_agencia_mobiliario.html'
    context_object_name = 'agencias'

# este listview es para consultar los mobiliarios por agencia
# esta clase recibe dos parametros get para realizar una consulta mas expedita
class ListarAgenciasMobiliario2(ListView):
    model = tb_Mobiliario
    template_name = 'inventario_mobiliario_agencia.html'
    context_object_name = 'mobiliarios'
    #FUNCION PARA REALIZAR UN FILTRO POR AGENCIAS DEL INVENTARIO DEL INMUEBLE
    def get_queryset(self):
        qs = super(ListarAgenciasMobiliario2, self).get_queryset()
        # la sentencia de abajo recupera el pk de la url


        return qs.filter(ubicacion_actual=self.request.GET.get('noma'), estado_mobiliario="activo")


# Listview para la pagina buscar_articulo.html
# este listview devuelve todos los articulos dentro del inventarios
class Personas(ListView):
    model = tb_Articulo
    template_name = 'buscar_articulo.html'
    context_object_name = 'personas'

# LISTAR ALERTA PARA EXISTENCIAS
class AlertaExistencias(ListView):
    model = tb_Articulo
    template_name = 'alerta_existencias.html'
    context_object_name = 'articulos'
    queryset = tb_Articulo.objects.filter(existencia__lte=10)

# LISTAR ARTICULOS DAR DE BAJA
class ListarDarBajaArticulo(ListView):
    model = tb_Articulo
    template_name = 'dar_baja_articulo.html'
    context_object_name = 'articulos'


# Listview para la pagina ver_entradas.html
# este listview devuelve todos las entradas registradas dentro del inventarios
class VerEntradas(ListView):
    model = tb_entrada
    template_name = 'ver_entradas.html'
    context_object_name = 'entradas'


# LISTAS ENTRADAS PARA SER MODIFICADAS
class VerEntradasModificar(ListView):
    model = tb_DetalleArticulo

    template_name = 'listar_entradas_modificar.html'
    context_object_name = 'entradas'


# Listview para la pagina ver_salidas.html
# este listview devuelve todos las salidas registradas dentro del inventarios
class VerSalidas(ListView):
    model = tb_detalle_salida
    template_name = 'ver_salidas.html'
    context_object_name = 'salidas'


# Listview para la pagina buscar_mobiliario.html
# este listview devuelve todos los mobiliarios que se encuentran disponibless
class BuscarMobiliario(ListView):
    model = tb_Mobiliario
    template_name = 'buscar_mobiliario.html'
    context_object_name = 'mobiliario'
    #FUNCION PARA FILTAR EL MOBILIARIO POR ESTADO DISPONIBLE
    def get_queryset(self):
        qs = super(BuscarMobiliario, self).get_queryset()
        return qs.filter(estado="bueno")


# Listview para la pagina buscar_mobiliario2.html
# este listview devuelve todos los mobiliarios que se encuentran disponibles
class BuscarMobiliario2(ListView):
    model = tb_Mobiliario
    template_name = 'buscar_mobiliario2.html'
    context_object_name = 'mobiliario'
    #FUNCION PARA FILTAR EL ESTADO DEL MOBILIARIO POR DISPONIBLE
    def get_queryset(self):
        qs = super(BuscarMobiliario2, self).get_queryset()
        return qs.filter(estado="disponible")


# LISTVIEW PARA MODIFICAR MOBILIARIO
class ListarModificarMobiliario(ListView):
    model = tb_Mobiliario
    template_name = 'listar_modificar_mobiliario.html'
    context_object_name = 'mobiliario'

# LISTVIEW ASIGNAR MOBILIARIO DETALLE
class MobiliarioDetalle11(ListView):
    model = tb_Mobiliario
    template_name = 'asignar_mobiliario2_detalle.html'
    context_object_name = 'mobiliarios'


# LISTAR MOBILIARIO PRESTADO
class ListarMobiliarioPrestadoSolo(ListView):
    template_name = 'listar_mobiliario_prestado_solo.html'
    context_object_name = 'mobiliarios'
    queryset = tb_Mobiliario.objects.all()
    #FUNCION PARA RETORNAR EL CONTEXTO DE MOBILIARIO, MOBILIARIO PRESTADO Y DE EMPLEADOS
    def get_context_data(self, **kwargs):
        context = super(ListarMobiliarioPrestadoSolo, self).get_context_data(**kwargs)
        context['mobiliario'] = tb_Mobiliario.objects.all()
        context['prestado'] = tb_MobiliarioPrestado.objects.all()
        context['empleados'] = tb_Empleado.objects.all()

        return context


# Listview para la pagina buscar_empleado_mobiliario.html
# este listview devuelve todos los empleados
class BuscarEmpleado(ListView):
    model = tb_Empleado
    template_name = 'buscar_empleado_mobiliario.html'
    context_object_name = 'empleado'

# empleado que se asigna a detalle mobiliario
class BuscarEmpleado10(ListView):
    model = tb_Empleado
    template_name = 'asignar_mobiliario2_empleado.html'
    context_object_name = 'empleado'

# Listview para la pagina buscar_empleado_mobiliario.html
# este listview devuelve todos los empleados
class BuscarEmpleadoMP(ListView):
    model = tb_Empleado
    template_name = 'buscar_empleado_mobiliarioP.html'
    context_object_name = 'empleado'

# Lista los empleados para ver que mobiliarios tiene asignagos
class BuscarEmpleadoMobiliarioAsignado(ListView):
    model = tb_Empleado
    template_name = 'busca_empleado_mobiliario_asignado2.html'
    context_object_name = 'empleadoss'

#LISTA EL MOBILIARIO QUE SERA DADO DE BAJA
class ListarMobiliarioDarDeBaja(ListView):
    model = tb_Mobiliario
    template_name = 'dar_baja_mobiliario.html'
    context_object_name = 'mobiliario'


# ================================================================
#LISTVIEW PARA LISTA EL MOBILIARIO QUE SE ENCUENTRA PRESTADO
class BuscarMobiliarioPrestado(ListView):
    template_name = 'buscar_mobiliarioPrestado.html'
    context_object_name = 'mobiliarioP'
    queryset = tb_MobiliarioPrestado.objects.filter(estado="ocupado")
    #RETORNA EL CONTEXTO DE EL MOBILIARIO Y DE LOS EMPLEADOS
    def get_context_data(self, **kwargs):
        context = super(BuscarMobiliarioPrestado, self).get_context_data(**kwargs)
        context['mobiliario'] = tb_Mobiliario.objects.all()
        context['empleados'] = tb_Empleado.objects.all()

        return context


# VER EXISTENCIAS DE LOS ARTICULOS
class VerExistenciasArticulos(ListView):
    model = tb_Articulo
    template_name = 'ver_existencias.html'
    context_object_name = 'existencias'
    queryset = tb_Articulo.objects.filter(existencia__gte=1)


# VER ARTICULOS QUE NO TIENEN EXISTENCIA
class VerSinExistenciasArticulos(ListView):
    model = tb_Articulo
    template_name = 'ver_no_existencias.html'
    context_object_name = 'existencias'
    queryset = tb_Articulo.objects.filter(existencia=0)

#LISTA LAS EXISTENCIAS DE LOS ARTICULOS
class VerExistenciasArticulosPDF(ListView):
    model = tb_Articulo
    template_name = 'lista_existencias_articulosPDF.html'
    context_object_name = 'existencias'

#LISTA POR DETALLE LAS EXISTENCIAS DE LOS ARTICULOS
class VerExistenciasArticulosDet(ListView):
    model = tb_DetalleArticulo
    template_name = 'buscar_articulo_detalle.html'
    context_object_name = 'existencias'

#LISTVIEW PARA LISTAR TODOS LOS MOBILIARIOS SOLAMENTE
class BuscarMobiliarioIndex(ListView):
    model = tb_Mobiliario
    template_name = 'buscar_mobiliario_index.html'
    context_object_name = 'existencias'

#LISTVIEW PARA LISTAR TODOS LOS ARTICULOS SOLAMENTE
class BuscarAticulosSolamente(ListView):
    model = tb_Articulo
    template_name = 'buscar_articulos_solo.html'
    context_object_name = 'articulos'


# Listview para la pagina ver_entradas.html
# este listview devuelve todos las entradas registradas dentro del inventarios
class VerArticulosEntradas(ListView):
    model = tb_Articulo
    template_name = 'listar_articulosEntradas.html'
    context_object_name = 'existencias'


# Este Listview sirve para la url incidenciaArticulo
# sirve para listar todos los detalles de articulos

class ListaArticulosIncidentias(ListView):
    model = tb_DetalleArticulo
    template_name = 'ver_det_incidencias.html'
    context_object_name = 'existencias'


#LISTVIEW PARA MODIFICAR ARTICULOS
class ModificarArticulo(ListView):
    model = tb_Articulo
    template_name = 'listar_modificar_articulo.html'
    context_object_name = 'articulos'


# ========================================= VISTAS DE VEHICULOS =========================================================

#LISTVIEW VEHICULOS QUE SE VAN A DAR DE BAJA
class ListarVehiculosDarBaja(ListView):
    model = tb_Vehiculo
    template_name = 'dar_baja_vehiculo.html'
    context_object_name = 'vehiculos'


# este listview es para listar todos los vehiculos
class ListarVehiculos(ListView):
    model = tb_Vehiculo
    template_name = 'buscar_vehiculo.html'
    context_object_name = 'vehiculos'


# este listview es para listar los vehiculos que se van a asignar a los empleados
class ListarVehiculosAsignar(ListView):
    model = tb_Vehiculo
    template_name = 'listar_vehiculos_asinar.html'
    context_object_name = 'vehiculos'


# este listview es para listar los vehiculos que se van a descargara los empleados
class ListarVehiculosDescargar(ListView):
    template_name = 'lista_vehiculo_descargar.html'
    context_object_name = 'vehiculos'
    queryset = tb_Vehiculo.objects.all()
    #FUNCION PARA RETORNAR LOS CONTEXTO DE VEHICULO ASIGNADO Y DE EMPLEADOS
    def get_context_data(self, **kwargs):
        context = super(ListarVehiculosDescargar, self).get_context_data(**kwargs)
        context['asignado'] = tb_VehiculoAsignado.objects.all()
        context['empleados'] = tb_Empleado.objects.all()

        return context


# lista incidentes de articulos
class ListarIncidenteArticulo2(ListView):
    template_name = 'listar_incidente_articulo.html'
    context_object_name = 'incidentes'
    queryset = tb_incidenciaArticulo.objects.all()
    #FUNCION PARA RETORNAR LOS CONTEXTO DE ARTICULOS Y DETALLE DE ARTICULOS
    def get_context_data(self, **kwargs):
        context = super(ListarIncidenteArticulo2, self).get_context_data(**kwargs)
        context['articulo'] = tb_Articulo.objects.all()
        context['det_art'] = tb_DetalleArticulo.objects.all()

        return context


# este listview es para listar los empleados que se van a asignar a los vehiculos
class ListarEmpleadosAsignarVehi(ListView):
    model = tb_Empleado
    template_name = 'asignar_vehiculo_empleado.html'
    context_object_name = 'empleados'


# LISTAR LOS VEHICULOS QUE SE VAN A MODIFICAR
class ListarVehiculosModificar(ListView):
    model = tb_Vehiculo
    template_name = 'listar_vehiculos_modificar.html'
    context_object_name = 'vehiculos'


# ===========================================================================
#LISTVIEW PARA MOSTAR LOS DETALLES DE LOS ARTICULOS
class pruebaListview(ListView):
    model = tb_DetalleArticulo
    template_name = 'prueba.html'
    context_object_name = 'existencias'
    #FUNCION PARA DEVOLVER LOS CONTEXTOS DE LAS EXISTENCIAS DE LOS ARTICULOS
    def get_context_data(self, **kwargs):
        context = super(pruebaListview, self).get_context_data(**kwargs)
        context['existencias'] = tb_DetalleArticulo.objects.values('cod_articulo_id').annotate(
            total=Sum(F('unidades') * F(('precio_unitario')), output_field=FloatField()))

        context['existencias2'] = tb_Articulo.objects.all()
        return context


# LISTVIEW PARA LISTAR EL DETALLE DE ARTICULOS EN EL HTML
class AncillaryDetail(ListView):
    model = tb_DetalleArticulo

    # FUNCION QUE DEVUELTE LOS DETALLES DE ARTICULOS EN EL HTML
    def get_queryset(self):
        qs = super(AncillaryDetail, self).get_queryset()

        # la sentencia de abajo recupera el pk de la url
        return qs.filter(cod_articulo_id=self.kwargs.get('pk'), unidades__gte=1)


# ======================= Ver Salidas Fecha =======================================
# LISTVIEW  PARA EL MOBILIARIO QUE SE ENCUENTRA PRESTADO
class VerMobiliarioP3(ListView):
    context_object_name = 'mobiliario'
    template_name = 'mobiliario_prestadoe3.html'
    queryset = tb_MobiliarioPrestado.objects.all()

    # FUNCION PARA FILTAR EL EMPLEADO
    def get_queryset(self):
        qs = super(VerMobiliarioP3, self).get_queryset()

        return qs.filter(cod_empleado_id=self.request.GET.get("pke"))

    # FUNCION PARA DEVOLVER DIFERENTES CONTEXTOS AL HTML
    def get_context_data(self, **kwargs):
        context = super(VerMobiliarioP3, self).get_context_data(**kwargs)
        context['mobiliarios'] = tb_Mobiliario.objects.all()
        context['mobiliariosp'] = tb_MobiliarioPrestado.objects.all().filter(
            cod_empleado_id=self.request.GET.get("pke"))

        return context


# LISTVIEW PARA VER LAS SALIDAS POR RANGO DE FECHA
class VerSalidaFecha(ListView):
    context_object_name = 'existencias'
    template_name = 'salidas_fecha.html'

    queryset = tb_detalle_salida.objects.all()

    # LAS FECHAS SON OBTENIDAS POR MEDIO DEL METODO GET EN EL REQUEST
    def get_queryset(self):
        #EN CASO DE QUE LAS FECHAS NO SEAN CORRECTAS SE EJECUTA Y SE CONTROLA LA EXCEPCION
        qs = super(VerSalidaFecha, self).get_queryset()
        try:
            fecha_inicial = datetime.datetime.strptime(self.request.GET.get('starfecha'), "%m/%d/%Y")
            fecha_final = datetime.datetime.strptime(self.request.GET.get('endfecha'), "%m/%d/%Y")
            return qs.filter(fecha_registro_salida__range=(fecha_inicial, fecha_final))

        except Exception:

            fecha_final = "2010-07-07"
            fecha_inicial = "2010-07-07"
            return qs.filter(fecha_registro_salida__range=(fecha_inicial, fecha_final))
            # FUNCION QUE DEVUELVEN LOS CONTEXTOS DE ARTICULOS Y DETALLE DE ARTICULOS AL HTML
    #FUNCION PARA DEVOLVER LOS CONTEXTOS DE ARTICULOS Y DETALLE DE ARTICULOS
    def get_context_data(self, **kwargs):
        context = super(VerSalidaFecha, self).get_context_data(**kwargs)
        context['articulos'] = tb_Articulo.objects.all()
        context['det_articulos'] = tb_DetalleArticulo.objects.all()

        return context


# ======================= Ver Entradas Fecha =======================================
# LISTVIEW PARA VER LAS   ENTRADAS POR  RANGO DE FECHA
class VerEntradaFecha(ListView):
    model = tb_entrada
    template_name = 'entradas_fecha.html'
    context_object_name = 'existencias'

    # LAS FECHAS SON OBTENIDAS POR MEDIO DEL METODO GET EN EL REQUEST
    def get_queryset(self):
        qs = super(VerEntradaFecha, self).get_queryset()
        try:
            fecha_inicial = datetime.datetime.strptime(self.request.GET.get('starfecha'), "%m/%d/%Y")
            fecha_final = datetime.datetime.strptime(self.request.GET.get('endfecha'), "%m/%d/%Y")
            return qs.filter(fecha_registro_entrada__range=(fecha_inicial, fecha_final))


        except Exception:

            fecha_final = "2010-07-07"
            fecha_inicial = "2010-07-07"
            return qs.filter(fecha_registro_entrada__range=(fecha_inicial, fecha_final))


# ============================== BITACORA FECHA MOBILIAIO ===============================
# LISTVIEW PARA LAS BITACORAS DE MOBILIARIO POR FECHA
class BitacoraMobiliarioFecha(ListView):
    model = tb_audit_mobiliario
    template_name = 'bitacora_mobiliario_fecha.html'
    context_object_name = 'bitacoras'

    # LAS FECHAS SON OBTENIDAS POR MEDIO DEL METODO GET EN EL REQUEST
    def get_queryset(self):
        qs = super(BitacoraMobiliarioFecha, self).get_queryset()
        try:
            fecha_inicial = datetime.datetime.strptime(self.request.GET.get('starfecha'), "%m/%d/%Y")
            fecha_final = datetime.datetime.strptime(self.request.GET.get('endfecha'), "%m/%d/%Y")
            return qs.filter(UpdateDate__range=(fecha_inicial, fecha_final))


        except Exception:

            fecha_final = "2010-07-07"
            fecha_inicial = "2010-07-07"
            return qs.filter(UpdateDate__range=(fecha_inicial, fecha_final))


# ========================== BITACORA FECHA VEHICULO =======================================
# LISTVIEW DE LAS BITACORAS PARA LOS VEHICULOS
class BitacoraVehiculoFecha(ListView):
    model = tb_audit_det_vehiculo
    template_name = 'bitacora_vehiculo_fecha.html'
    context_object_name = 'bitacoras'
    #FUNCION PARA RETORNAR LA BITACORA EN RANGO DE FECHAS
    def get_queryset(self):
        # LAS FECHAS SON OBTENIDAS POR MEDIO DEL METODO GET EN EL REQUEST
        qs = super(BitacoraVehiculoFecha, self).get_queryset()
        try:
            fecha_inicial = datetime.datetime.strptime(self.request.GET.get('starfecha'), "%m/%d/%Y")
            fecha_final = datetime.datetime.strptime(self.request.GET.get('endfecha'), "%m/%d/%Y")
            return qs.filter(UpdateDate__range=(fecha_inicial, fecha_final))


        except Exception:

            fecha_final = "2010-07-07"
            fecha_inicial = "2010-07-07"
            return qs.filter(UpdateDate__range=(fecha_inicial, fecha_final))


# =============================== BITACORA ENTRADAS FECHA  =====================================================
# LISTVIEW PARA LAS BITACORAS DE ENTRADAS POR FECHA
class BitacoraEntradaFecha(ListView):
    model = tb_audit_entrada
    template_name = 'bitacora_entrada_fecha.html'
    context_object_name = 'bitacoras'

    # LAS FECHAS SON OBTENIDAS POR MEDIO DEL METODO GET EN EL REQUEST
    #FUNCION PARA RETORNAR LAS BITACORAS EN RANGO DE FECHA
    def get_queryset(self):
        qs = super(BitacoraEntradaFecha, self).get_queryset()
        try:
            fecha_inicial = datetime.datetime.strptime(self.request.GET.get('starfecha'), "%m/%d/%Y")
            fecha_final = datetime.datetime.strptime(self.request.GET.get('endfecha'), "%m/%d/%Y")
            return qs.filter(UpdateDate__range=(fecha_inicial, fecha_final))


        except Exception:

            fecha_final = "2010-07-07"
            fecha_inicial = "2010-07-07"
            return qs.filter(UpdateDate__range=(fecha_inicial, fecha_final))


# ======================================= BITACORA SALIDAS FECHAS =================================
# LISTVIEW PARA BITACORAS DE SALIDAS POR FECHA
class BitacoraSalidaFecha(ListView):
    model = tb_audit_salida
    template_name = 'bitacora_salida_fecha.html'
    context_object_name = 'bitacoras'

    # LAS FECHAS SON OBTENIDAS POR MEDIO DEL METODO GET EN EL REQUEST
    # FUNCION PARA RETORNAR LAS BITACORAS EN RANGO DE FECHA
    def get_queryset(self):

        qs = super(BitacoraSalidaFecha, self).get_queryset()
        try:
            fecha_inicial = datetime.datetime.strptime(self.request.GET.get('starfecha'), "%m/%d/%Y")
            fecha_final = datetime.datetime.strptime(self.request.GET.get('endfecha'), "%m/%d/%Y")
            return qs.filter(UpdateDate__range=(fecha_inicial, fecha_final))


        except Exception:

            fecha_final = "2010-07-07"
            fecha_inicial = "2010-07-07"
            return qs.filter(UpdateDate__range=(fecha_inicial, fecha_final))


# ==============================================================================================================
# ===================================== REPORTES ===============================================================
# ==============================================================================================================
# REPORTE DE EXISTENCIAS GENERADO EN PDF
class ReportePersonasPDF(View):
    def cabecera(self, pdf):
        archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
        pdf.drawImage(archivo_imagen, 40, 750, 120, 90, preserveAspectRatio=True)
        pdf.setFont("Helvetica", 16)

        pdf.drawString(250, 790, u"HONDUCOR")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(120, 700, u"REPORTE DE VALORES POR EXISTENCIAS DE ARTICULOS")
        cursor = connection.cursor()
        cursor.execute(
            "select a.id, sum(d.unidades*d.precio_unitario)from inventariohonducorapp_tb_detallearticulo d,inventariohonducorapp_tb_articulo a where d.cod_articulo_id=a.id group by a.id")
        contador = 0
        for id in cursor:
            contador = id[1] + contador

        pdf.drawString(100, 670, "TOTAL EN LPS: " + str(contador))

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')

        buffer = BytesIO()

        pdf = canvas.Canvas(buffer)

        self.cabecera(pdf)
        y = 550
        self.tabla(pdf, y)

        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def tabla(self, pdf, y):
        encabezados = ('CODIGO', 'NOMBRE DEL ARTICULO', 'UNIDADES', 'VALOR LPS')

        cursor = connection.cursor()
        cursor.execute(
            "select a.id,a.nombre_art,a.existencia, sum(d.unidades*d.precio_unitario)from inventariohonducorapp_tb_detallearticulo d,inventariohonducorapp_tb_articulo a where d.cod_articulo_id=a.id group by a.nombre_art,a.id,a.existencia")

        detalles = [(item[0], item[1], item[2], item[3]) for item in cursor.fetchall()]

        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 8 * cm, 3 * cm, 4 * cm])

        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),

                ('GRID', (0, 0), (-1, -1), 1, colors.black),

                ('FONTSIZE', (0, 0), (-1, 1), 10),
            ]
        ))

        detalle_orden.wrapOn(pdf, 800, 600)

        detalle_orden.drawOn(pdf, 60, y)


# =========================REPORTE MOBILIARIO=========================================
# reporte DE MOBILIARIO GENERADO EN PDF
#ESTE METODO DE PDF NO SE ESTA USANDO
class ReporteMobiliarioPDF(View):
    def cabecera(self, pdf):
        archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'

        pdf.drawImage(archivo_imagen, 40, 750, 120, 90, preserveAspectRatio=True)

        pdf.setFont("Helvetica", 16)

        pdf.drawString(250, 790, u"HONDUCOR")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(150, 700, u"REPORTE DE MOBILIARIO EXISTENTE")

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')

        buffer = BytesIO()

        pdf = canvas.Canvas(buffer)

        self.cabecera(pdf)
        y = 600
        self.tabla(pdf, y)

        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def tabla(self, pdf, y):
        encabezados = ('CODIGO', 'INVENTARIO', 'MARCA', 'MODELO', 'SERIE')

        detalles = [(item.id, item.cod_inventario, item.marca, item.modelo, item.serie) for item in
                    tb_Mobiliario.objects.all().filter(estado="disponible")]

        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 3 * cm, 3 * cm, 4 * cm, 4 * cm])

        detalle_orden.setStyle(TableStyle(
            [

                ('ALIGN', (0, 0), (3, 0), 'CENTER'),

                ('GRID', (0, 0), (-1, -1), 1, colors.black),

                ('FONTSIZE', (0, 0), (-1, 1), 10),
            ]
        ))
        detalle_orden.wrapOn(pdf, 800, 600)

        detalle_orden.drawOn(pdf, 60, y)


# ================================== DOCUMENTOS EN EXCEL =========================================
# EXCEL PARA LAS ENTRADAS
def export_users_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    # RELLENAR LOS ENCABEZADOS DEL EXCEL
    columns = ['CODIGO ENTRADA', 'NOMBRE ARTICULO', 'CODIGO DE BARRAS', 'PRECIO UNITARIO', 'UNIDADES']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = tb_DetalleArticulo.objects.filter(cod_articulo=request.GET.get('pk'), unidades__gte=1).values_list('id',
                                                                                                              'cod_articulo',
                                                                                                              'codigo_barras',
                                                                                                              'precio_unitario',
                                                                                                              "unidades").order_by(
        'id')
    # RELLENAR LAS CELDAS DEL EXCEL
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


# =================================== EXCEL DE MOBILIARIO =========================================

def export_mobiliario_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="mobiliario.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('mobiliario')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODIGO MOBILIARIO', 'CATEGORIA', 'MARCA', 'MODELO', 'SERIE', 'CODIGO DE INVENTARIO', 'COLOR',
               'DESCRIPCION', 'COSTO UNITARIO ']
    # RELLENAR LOS ENCABEZADOS DEL EXCEL
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    categoria = tb_CategoriaMobiliario.objects.values_list('id', 'nombre_categoria')
    rows = tb_Mobiliario.objects.values_list('id', 'cod_cat_mobiliario', 'marca', 'modelo', 'serie', "cod_inventario",
                                             'color',
                                             'descripccion', 'costo_uni')
    # RELLENAR LAS CELDAS DEL EXCEL
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num == 1:
                for cat in categoria:
                    if cat[0] == row[col_num]:
                        ws.write(row_num, col_num, cat[1], font_style)

            else:
                ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response


# ================================================= BITACORAS
# LISTVIEW PARA BITACORA DE MOBILIARIO
class BitacoraMobiliario(ListView):
    template_name = 'bitacora_mobiliario.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_mobiliario.objects.all().order_by('id').reverse()


# LISTVIEW BITACORA DE DETALLE DE ENTRADA
class BitacoraDetEntrada(ListView):
    template_name = 'bitacora_det_entrada.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_det_articulo.objects.all().order_by('id').reverse()


# LISTVIEW PARA BITACORAS DE ENTRADA
class BitacoraEntrada(ListView):
    template_name = 'bitacora_entrada.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_entrada.objects.all().order_by('id').reverse()


# LISTVIEW PARA BITACORAS DE SALIDA
class BitacoraSalida(ListView):
    template_name = 'bitacora_salida.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_salida.objects.all().order_by('id').reverse()


# LISTVIEW PARA BITACORA DE VEHICULOS
class BitacoraVehiculo(ListView):
    template_name = 'bitacora_vehiculo.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_det_vehiculo.objects.all().order_by('id').reverse()


# LISTVIEW PARA BITACORA DE INICIO DE SESION
class BitacoraLogin(ListView):
    template_name = 'bitacora_login.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_login.objects.all().order_by('id').reverse()


# ================================================================= PROVEEDORES
# LISTAR PROVEEDORES
class ListarProveedor(ListView):
    template_name = 'listar_proveedor.html'
    context_object_name = 'proveedores'
    model = tb_proveedor


# LISTAR PROVEEDORES A MODIFICAR
class ListarProveedorModificar(ListView):
    template_name = 'listar_proveedor_modificar.html'
    context_object_name = 'proveedores'
    model = tb_proveedor


# VISTA REGISTRAR UN NUEVO PROVEEDOR
@login_required()
#VISTA PARA NUEVO PROVEEDOR
def nuevoProveedor(request):
    #SI EL METODO ES POST PUEDE CONTINUAR
    if request.method == "POST":
        #INSTANCIA DE FORMULARIO
        form = Tb_ProveedorForm(request.POST or None, request.FILES or None)
        #SI EL FORMULARIO ES VALIDO PUEDE CONTINUAR
        if form.is_valid():
            #NUEVA ISNTANCIA PARA UN PROVEEDOR
            new_proveedor = tb_proveedor(
                nombre_empresa=request.POST['nombre_empresa'],
                rtn=request.POST['rtn'],
                razon_social=request.POST['razon_social'],
                representante_legal=request.POST['representante_legal'],
                ciudad=request.POST['ciudad'],
                telefono1=request.POST['telefono1'],
                telefono2=request.POST['telefono2'],
                email=request.POST['email'],
                pais=request.POST['pais'],
                sitio_web=request.POST['sitio_web']

            )
            #REGISTRA UN PROVEEDOR
            new_proveedor.save(form)
            #MENSAJE DE CONFIRMACION
            messages.success(request, "REGISTRADO EXITOSAMENTE")
            return redirect("/add_post")


    else:
        #NUEVA ISNTANCIA DE FORMULARIO
        form = Tb_ProveedorForm()
    #REGRESA A LA PAGINA QUE LO LLAMO Y CARGA EL FORMULARIO
    return render(request, 'nuevo_proveedor.html', {'form': form})

#PRUEBA
class AuthorUpdate(UpdateView):
    model = tb_proveedor
    fields = ['name']
    template_name_suffix = '_update_form'
