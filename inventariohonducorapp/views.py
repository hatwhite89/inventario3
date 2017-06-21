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

from inventariohonducorapp.models import tb_Articulo, tb_DetalleArticulo, tb_entrada, tb_Mobiliario, \
    tb_CategoriaMobiliario, tb_MobiliarioPrestado, tb_Empleado, tb_salida, tb_Jefatura, Agencia, tb_MobiliarioDevuelto, \
    tb_incidenciaArticulo, tb_Vehiculo, tb_VehiculoAsignado, tb_VehiculoDescargado, tb_Inmueble, tb_Admin_Inmueble, \
    tb_audit_det_articulo, tb_audit_det_vehiculo, tb_audit_entrada, tb_audit_mobiliario, tb_audit_salida, \
    tb_detalle_salida,tb_InmuebleDescargado,tb_audit_login,tb_proveedor

from inventariohonducorapp.forms import Tb_ArticuloForm, Tb_DetalleArtForm, Tb_MobiliarioForm, \
    Tb_MobiliarioPrestadoForm, Tb_SalidaForm, Tb_DescargarMobiliarioForm, Tb_IncidenciaArticulo, Tb_NuevoVehiculo, \
    Tb_NuevoVehiculoAsignado, Tb_DescargarVehiculoForm, Tb_NuevoInmuebleForm, Tb_AsignarInmuebleForm, Tb_ModificarMobiliario, \
    Tb_NuevoDetalleSalida, Tb_nuevoDetalleSalida2, Tb_ModificarArticulo,Tb_ModificarVehiculo,Tb_ModificarInmueble,Tb_DescargarInmueble,Tb_ProveedorForm

from django.db.models import F, Count, Sum, FloatField

# para los reportes
from django.conf import settings
from io import BytesIO
from reportlab.pdfgen import canvas
from django.views.generic import View
import json

# variables globales para conexcion

# Create your views here.
# ================ VISTAS SENCILLAS ==================================================================
@login_required()
def main(request):
    existencia_menor= tb_Articulo.objects.filter(existencia__lte=10)
    contador=tb_Articulo.objects.filter(existencia__lte=10).count()
    print(contador)


    return render(request, 'Inventario/index.html', {'existencia':existencia_menor,'alerta':contador})


@login_required()
def Calendario(request):
    return render(request, 'Inventario/pages_calendar.html', {})


def login(request):


    return render(request, 'Inventario/login.html', {})

#FUNCION TOP 10 PRODUCOTS CON MAS EXISTENCIAS
@login_required()
def graficos(request):
    #PRIMERA CONEXION
    cur = connection.cursor()

    # cur.callproc("retornacodbarras", (codigo,))
    # llamada a procedimiento almacenado
    cur.execute("select nombre_art, MAX(existencia) from inventariohonducorapp_tb_articulo GROUP BY  nombre_art;")
    # recupera el valor del procedimiento almacenado
    row = cur.fetchall()

    # cierra la conexcion a la bd
    cur.close()
    fecha = time.strftime('%m')

    #SEGUNDA CONEXION
    cur2 = connection.cursor()

    # llamada a procedimiento almacenado
    cur2.execute("select a.nombre_art,count(s.cantidad) from inventariohonducorapp_tb_detalle_salida s,inventariohonducorapp_tb_detallearticulo d,inventariohonducorapp_tb_articulo a where s.fecha_registro_salida  between '2017-"+fecha+"-18' and '2017-"+fecha+"-18' and s.codigo_barras=d.codigo_barras and a.id= d.cod_articulo_id group by a.nombre_art")
    # recupera el valor del procedimiento almacenado
    row2 = cur2.fetchall()
    # cierra la conexcion a la bd
    cur2.close()


    jsona2=json.dumps([['articulos', 'TOP SALIDAS PARA ESTE MES']]+row2)
    print(jsona2)
    jsona=json.dumps([['articulos', 'existencias']]+row)

    return render(request,'Inventario/graficos.html',{'array':jsona,'array2':jsona2})

#GRAFICO DE AGENCIAS
@login_required()
def grafico_agencia(request):
    cur = connection.cursor()

    # cur.callproc("retornacodbarras", (codigo,))
    # llamada a procedimiento almacenado
    cur.execute("select s.agencia,SUM(CAST (d.precio_unitario as float) * s.cantidad) as TOTAL from inventariohonducorapp_tb_detallearticulo d,inventariohonducorapp_tb_articulo a,inventariohonducorapp_tb_detalle_salida s where s.cod_det_art_id=d.id and a.id= d.cod_articulo_id and s.fecha_registro_salida  between '2017-06-19' and '2017-06-19' group by s.agencia order by  TOTAL desc")
    # recupera el valor del procedimiento almacenado
    row = cur.fetchall()

    # cierra la conexcion a la bd
    cur.close()
    jsona = json.dumps(row)

    if request.method=='POST':
        fecha =str(datetime.datetime.strptime(request.POST['startfecha'], "%m/%d/%Y"))
        fecha2 = str(datetime.datetime.strptime(request.POST['endfecha'], "%m/%d/%Y"))
        cur2 = connection.cursor()

        # cur.callproc("retornacodbarras", (codigo,))
        # llamada a procedimiento almacenado
        cur2.execute(
            "select s.agencia,SUM(CAST (d.precio_unitario as float) * s.cantidad) as TOTAL from inventariohonducorapp_tb_detallearticulo d,inventariohonducorapp_tb_articulo a,inventariohonducorapp_tb_detalle_salida s where s.cod_det_art_id=d.id and a.id= d.cod_articulo_id and s.fecha_registro_salida  between '"+fecha+"' and '"+fecha2+"' group by s.agencia order by  TOTAL desc ")
        # recupera el valor del procedimiento almacenado
        row2 = cur2.fetchall()

        # cierra la conexcion a la bd
        cur2.close()
        print(row2)

        jsona2 = json.dumps(row2)

        return render(request, 'Inventario/grafico_2.html', {'array': jsona2})
    else:

        return render(request, 'Inventario/grafico_2.html',{'array':jsona})

#================================================= graficos mobiliarios
def graficosMobiliario(request):
    #PRIMERA CONEXION
    cur = connection.cursor()

    # cur.callproc("retornacodbarras", (codigo,))
    # llamada a procedimiento almacenado
    cur.execute("select c.nombre_categoria,SUM(m.costo_uni)as TOTAL from inventariohonducorapp_tb_mobiliario m,inventariohonducorapp_tb_categoriamobiliario c where m.cod_cat_mobiliario_id = c.id group by c.nombre_categoria;")
    # recupera el valor del procedimiento almacenado
    row = cur.fetchall()

    # cierra la conexcion a la bd
    cur.close()




    jsona=json.dumps([['articulos', 'existencias']]+row)

    return render(request,'Inventario/grafico_mobiliario.html',{'array':jsona})

#============================== GRAFICO DE MOBILIARIOS 2

@login_required()
def grafico_mobiliario_agencia(request):


    cur2 = connection.cursor()

    # cur.callproc("retornacodbarras", (codigo,))
    # llamada a procedimiento almacenado
    cur2.execute(
        "select m.ubicacion_actual,SUM(m.costo_uni)as TOTAL from inventariohonducorapp_tb_mobiliario m,inventariohonducorapp_tb_categoriamobiliario c where m.cod_cat_mobiliario_id = c.id group by m.ubicacion_actual")
    # recupera el valor del procedimiento almacenado
    row2 = cur2.fetchall()

    # cierra la conexcion a la bd
    cur2.close()
    print(row2)

    jsona2 = json.dumps(row2)

    return render(request, 'Inventario/grafico_mobiliario2.html', {'array': jsona2})

# GRAFICOS PARA VEHICULOS
def graficosVehiculo(request):
    #PRIMERA CONEXION
    cur = connection.cursor()

    # cur.callproc("retornacodbarras", (codigo,))
    # llamada a procedimiento almacenado
    cur.execute("select tipo_vehiculo, count(costo)as total from inventariohonducorapp_tb_vehiculo group by tipo_vehiculo;")
    # recupera el valor del procedimiento almacenado
    row = cur.fetchall()

    # cierra la conexcion a la bd
    cur.close()




    jsona=json.dumps([['articulos', 'existencias']]+row)

    return render(request,'Inventario/grafico_vehiculo.html',{'array':jsona})


# ========================================== INSERTAR EN FORMULARIOS ===============================
@login_required()
# esta vista sirve para registrar un nuevo articulo
def nuevoArticulo(request):
    if request.method == "POST":

        form = Tb_ArticuloForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            try:
                newArticulo = tb_Articulo(
                    nombre_art=request.POST["nombre_art"],
                    descrip=request.POST["descrip"],

                    imagen_art=request.FILES['imagen_art'],
                    existencia="0",
                    cod_categoria_id=request.POST["cod_categoria"],
                    estado_articulo="activo",
                    usuario_regis=request.user
                )

                newArticulo.save(form)
            except Exception:

                newArticulo = tb_Articulo(
                    nombre_art=request.POST["nombre_art"],
                    descrip=request.POST["descrip"],
                    imagen_art="/imagenes/melamina_blanca-3.jpg",
                    existencia="0",
                    cod_categoria_id=request.POST["cod_categoria"],
                    estado_articulo="activo",
                    usuario_regis=request.user
                )

                newArticulo.save(form)
            messages.success(request, "REGISTRADO EXITOSAMENTE")
            return redirect("/add_post")

    else:
        form = Tb_ArticuloForm()

    return render(request, 'Inventario/nuevo_articulo.html', {'form': form})


@login_required()
# esta funcion sirve para agregar un nuevo registro a las tablas tb_DetalleArticulo, tb_entrada, y actualiza la tabla de articulos
def nuevoDetalleArticulo(request):
    if request.method == "POST":
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
            messages.error(request, "ESTE CODIGO DE BARRAS YA EXISTE, PREGUNTE AL ADMINISTRADOR DEL SISTEMA SOBRE ESTE ERROR")
            return redirect("/nuevoDetalleArticuloLista")
        elif newID2 == 0:
            # VERIFICA QUE EL CODIGO DEL ARTICULO EXISTA
            messages.error(request, "EL CODIGO DEL ARTICULO NO EXISTE")
        else:
            if form.is_valid():
                # mediante esta declaracion se inserta un nuevo registro en la tabla tb_DetalleArticulo
                #
                hora = time.strftime('%Y-%m-%d')

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
                new_detalle_articulo.save(form)

                # mediante esta declaracion de realiza una actualizacion en la tabla articulos
                # para aumentar las existencias de ese articulo
                articulo = tb_Articulo.objects.get(id=request.POST['cod_articulo'])
                articulo.existencia = F('existencia') + request.POST['unidades']
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
                entrada.save()
                # SI TODOS HA SALIDA BIEN, RETORNA UN MENSAJE CONFIRMANDO LA INSERCCION
                messages.success(request, "REGISTRADO EXITOSAMENTE")
            return redirect("/add_post")


    else:
        form = Tb_DetalleArtForm()

    return render(request, 'Inventario/nuevo_detalle_articulo.html', {'form': form})


# ===========================   NUEVO MOBILIARIO ============================================================
@login_required()
def nuevoMobiliario(request):
    if request.method == "POST":

        form = Tb_MobiliarioForm(request.POST or None, request.FILES or None)
        if form.is_valid():
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

            )
            new_mobiliari.save()
            messages.success(request, "REGISTRADO EXITOSAMENTE")
            return redirect("/add_post")

    else:
        form = Tb_MobiliarioForm()

    return render(request, 'Inventario/nuevo_mobiliario.html', {'form': form})


# ========================= ASIGNAR MOBILIARIO ============================
@login_required()
def asignarMobiliario(request):
    if request.method == "POST":
        form = Tb_MobiliarioPrestadoForm(request.POST or None, request.FILES or None)

        # establece conexion a la bd

        cur = connection.cursor()
        codigo = request.POST['cod_empleado']
        # cur.callproc("retornacodbarras", (codigo,))
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
        # cur.callproc("retornacodbarras", (codigo,))
        # llamada a procedimiento almacenado
        cur.execute("select verificacodmobiliario(%s);", (codigo,))
        # recupera el valor del procedimiento almacenado
        row2 = cur.fetchone()
        newID2 = row2[0]
        # cierra la conexcion a la bd
        cur.close()

        # =====================================================================================================

        mobi_usado = tb_Mobiliario.objects.filter(id=request.POST['cod_mobiliario']).values("estado")
        for sub in mobi_usado:
            for key in sub:
                sub[key] = sub[key]
                disponibilidad = sub[key]
        if newID == 0:
            messages.error(request, "CODIGO DE EMPLEADO NO EXISTE")
        elif newID2 == 0:
            messages.error(request, "CODIGO DE MOBILIARIO NO EXISTE")
        elif disponibilidad == "ocupado":

            # validar que el mobiliario no esta en uso
            # mobi_usado = tb_Mobiliario.objects.get(id=tb_Mobiliario.objects.filter(id=request.POST['cod_mobiliario']))
            messages.error(request, "ESTE MOBILIARIO YA SE ENCUENTRA ASIGNAGO")
        else:

            if form.is_valid():
                try:
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
                    new_asig_mobi.save()

                    mobiliario = tb_Mobiliario.objects.get(id=request.POST['cod_mobiliario'])
                    mobiliario.estado = request.POST['estado']
                    mobiliario.ubicacion_actual = request.POST['gerencia']
                    mobiliario.save()
                    messages.success(request, "REGISTRADO EXITOSAMENTE")
                    codigo_b="true"
                    fecha_prestado = datetime.datetime.strptime(request.POST['fecha_prestado'], "%m/%d/%Y")

                    descripccion = request.POST['descripccion']
                    gerencia = request.POST['gerencia'],
                    departamento = request.POST['departamento']
                    levanto_inventario = request.POST['levanto_inventario']
                    telefono = request.POST['telefono']
                    cod_empleado = tb_Empleado.objects.all().filter(id=request.POST['cod_empleado'])

                    cod_mobiliario = tb_Mobiliario.objects.all().filter(id=request.POST['cod_mobiliario'])
                    return render(request,"inventario/asignar_mobiliario.html",{'codigo_boton':codigo_b,'cod_empleado':cod_empleado,'fecha_p':fecha_prestado,'gerencia':gerencia,'mobiliario':cod_mobiliario})


                except Exception:
                    messages.error(request, "VERIFIQUE LOS CAMPOS CODIGO DE EMPLEADO Y DE MOBILIARIO")



    else:
        form = Tb_MobiliarioPrestadoForm()

    return render(request, 'Inventario/asignar_mobiliario.html', {'form': form})


# ================================ ASIGNAR MOBILIARIO ============================================

@login_required()
def descargarMobiliario(request):
    if request.method == "POST":

        form = Tb_DescargarMobiliarioForm(request.POST or None, request.FILES or None)
        # establece conexion a la bd
        cur = connection.cursor()
        codigo = request.POST['cod_empleado']
        # cur.callproc("retornacodbarras", (codigo,))
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
        # cur.callproc("retornacodbarras", (codigo,))
        # llamada a procedimiento almacenado
        cur.execute("select verificacodmobiliario(%s);", (codigo,))
        # recupera el valor del procedimiento almacenado
        row2 = cur.fetchone()
        newID2 = row2[0]
        # cierra la conexcion a la bd
        cur.close()

        # =====================================================================================================

        if newID == 0:
            messages.error(request, "CODIGO DE EMPLEADO NO EXISTE")
        elif newID2 == 0:
            messages.error(request, "CODIGO DE MOBILIARIO NO EXISTE")
        else:
            if form.is_valid():
                try:

                    new_descargar_mobi = tb_MobiliarioDevuelto(
                        fecha_devolucion=datetime.datetime.strptime(request.POST['fecha_devolucion'], "%m/%d/%Y"),
                        estado=request.POST['estado'],
                        descripccion=request.POST['descripccion'],

                        cod_empleado=tb_Empleado.objects.get(id=request.POST['cod_empleado']),
                        cod_mobiliario=tb_Mobiliario.objects.get(id=request.POST['cod_mobiliario']),
                        estado_md="activo",
                        usuario_regis=request.user

                    )
                    new_descargar_mobi.save(form)

                    mobiliario = tb_Mobiliario.objects.get(id=request.POST['cod_mobiliario'])
                    mobiliario.estado = "disponible"
                    mobiliario.save()

                    detalle_art = tb_MobiliarioPrestado.objects.get(
                        id=tb_MobiliarioPrestado.objects.filter(cod_mobiliario=request.POST['cod_mobiliario'],
                                                                estado="ocupado"),
                        cod_empleado=request.POST['cod_empleado'])
                    detalle_art.estado = "devuelto"
                    detalle_art.save()
                    messages.success(request, "REGISTRADO EXITOSAMENTE")
                    return redirect("/add_post")


                except Exception:
                    messages.error(request, "VERIFIQUE LOS CAMPOS CODIGO DE EMPLEADO Y DE MOBILIARIO")




    else:
        form = Tb_DescargarMobiliarioForm

    return render(request, 'Inventario/descargar_mobiliario.html', {'form': form})


# ============================================== REGISTRAR NUEVA SALIDA ===========================================
@login_required()
def nuevaSalida(request):
    if request.method == "POST":
        # establece conexion a la bd
        cur = connection.cursor()

        codigo = request.POST['codigo_barras']
        # cur.callproc("retornacodbarras", (codigo,))
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

        form = Tb_SalidaForm(request.POST or None, request.FILES or None)
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
            messages.error(request, 'CODIGO DE BARRAS NO EXISTE, INTENTE NUEVAMENTE')

        # si la existencia real es mayor a la que se requiere, deja continuar con la solicitud
        elif valor_cod == 0:
            messages.error(request, 'NO EXISTEN EXISTENCIAS DE ESTE ARTICULO')

        elif existencia > exis_real:
            messages.error(request, 'LA CANTIDAD A ENVIAR SOBREPASA LAS EXISTENCIAS')

        else:

            if form.is_valid():
                try:

                    # registra una nueva entrada en la tabla tb_salida
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
        form = Tb_SalidaForm

    return render(request, 'Inventario/nueva_salida.html', {'form': form})


# ========================================= REGISTRAR NUEVA INCIDENCIA  =========================

@login_required()
def nuevaIncidenciaArticulo(request):
    if request.method == "POST":

        form = Tb_IncidenciaArticulo(request.POST or None, request.FILES or None)

        # registra nueva incidencia
        incidencia = tb_incidenciaArticulo(
            tipo=request.POST['tipo'],
            descripccion_inc=request.POST['descripccion_inc'],
            fecha_registro_inc=datetime.datetime.strptime(request.POST['fecha_registro_inc'], "%m/%d/%Y"),

            cod_det_art=tb_DetalleArticulo.objects.get(id=request.POST['cod_det_art_id']),
            estado_inc_art="activo",
            usuario_regis=request.user

        )
        incidencia.save(form)
        messages.success(request, "REGISTRADO EXITOSAMENTE")
        return redirect("/add_post")

    else:

        form = Tb_IncidenciaArticulo

    return render(request, 'Inventario/registrar_incidencia_articulo.html', {'form': form})


# ================================= NUEVO VEHICULO ========================================

# funcion para pedir datos de sesion
@login_required()
def nuevoVehiculo(request):
    if request.method == "POST":

        form = Tb_NuevoVehiculo(request.POST or None, request.FILES or None)
        if form.is_valid():
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
            new_vehi.save()
            messages.success(request, "REGISTRADO EXITOSAMENTE")
            return redirect("/add_post")

    else:
        form = Tb_NuevoVehiculo()

    return render(request, 'Inventario/nuevo_vehiculo', {'form': form})


# ============================= ASIGNAR VEHICULO ===================================================
# funcion para pedir datos de sesion
@login_required()
def asignarVehiculo(request):
    if request.method == "POST":

        form = Tb_NuevoVehiculoAsignado(request.POST or None, request.FILES or None)
        if form.is_valid():
            new_vehi = tb_VehiculoAsignado(
                fecha_registro=datetime.datetime.strptime(request.POST['fecha_registro'], "%m/%d/%Y"),
                estado="ocupado",
                descripccion=request.POST['descripccion'],
                cod_empleado=tb_Empleado.objects.get(id=request.POST['cod_empleado_id']),
                cod_vehiculo=tb_Vehiculo.objects.get(id=request.POST['cod_vehiculo_id']),
                estado_vehi_asig="activo", usuario_regis=request.user
            )
            new_vehi.save()

            vehi = tb_Vehiculo.objects.get(id=request.POST['cod_vehiculo_id'])
            vehi.estado = "ocupado"
            vehi.save()
            messages.success(request, "REGISTRADO EXITOSAMENTE")
            return redirect("/add_post")

    else:
        form = Tb_MobiliarioForm()

    return render(request, 'Inventario/asignar_vehiculo.html', {'form': form})


# ============================================= DESCARGAR VEHICULO ===============================
@login_required()
def descargarVehiculo(request):
    if request.method == "POST":
        form = Tb_DescargarVehiculoForm(request.POST or None, request.FILES or None)

        new_des = tb_VehiculoDescargado(
            fecha_devolucion=datetime.datetime.strptime(request.POST['fecha_devolucion'], "%m/%d/%Y"),
            estado=request.POST['estado'],
            descripccion=request.POST['descripccion'],
            cod_empleado=tb_Empleado.objects.get(id=request.POST['cod_empleado_id']),
            cod_vehiculo=tb_Vehiculo.objects.get(id=request.POST['cod_vehiculo_id']),
            estado_vehi_des="activo", usuario_regis=request.user

        )
        new_des.save()

        new_vehiculo = tb_Vehiculo.objects.get(id=request.POST['cod_vehiculo_id'])
        new_vehiculo.estado = "disponible"
        new_vehiculo.save()

        new_descar_vehi = tb_VehiculoAsignado.objects.get(
            id=tb_VehiculoAsignado.objects.filter(cod_vehiculo=request.POST['cod_vehiculo_id'], estado="ocupado",
                                                  cod_empleado=request.POST['cod_empleado_id']))
        new_descar_vehi.estado = "devuelto"
        new_descar_vehi.save()
        messages.success(request, "REGISTRADO EXITOSAMENTE")
        return redirect("/add_post")

    else:
        form = Tb_DescargarVehiculoForm()
    return render(request, 'Inventario/descargar_vehiculo.html', {'form': form})


# =========================== NUEVO INMUEBLE

@login_required()
def nuevoInmueble(request):
    if request.method == "POST":
        form = Tb_NuevoInmuebleForm(request.POST or None, request.FILES or None)

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

        new_inmueble.save()

        messages.success(request, "REGISTRADO EXITOSAMENTE")
        return redirect("/add_post")

    else:
        form = Tb_NuevoInmuebleForm()
    return render(request, 'Inventario/nuevo_inmueble.html', {'form': form})


# ====================================== ASIGNAR INMUEBLE ==============================
@login_required()
def asignarInmueble(request):
    if request.method == "POST":
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
        new_asig_inm.save()

        new_inmueble_update = tb_Inmueble.objects.get(id=request.POST['cod_inmueble'])
        new_inmueble_update.estado = "ocupado"
        new_inmueble_update.save()
        messages.success(request, "REGISTRADO EXITOSAMENTE")
        return redirect("/add_post")


    else:
        form = Tb_AsignarInmuebleForm()

    return render(request, 'inventario/asignar_inmueble.html', {'form': form})
#DESCARGAR INMUEBLE

@login_required()
def descargarInmueble(request):
    if request.method == "POST":
        form = Tb_DescargarInmueble(request.POST or None, request.FILES or None)

        new_des = tb_InmuebleDescargado(
            fecha_devolucion=datetime.datetime.strptime(request.POST['fecha_devolucion'], "%m/%d/%Y"),
            estado="devuelto",
            descripccion=request.POST['descripccion'],
            usuario_regis=request.user,
            cod_empleado=tb_Empleado.objects.get(id=request.POST['cod_empleado_id']),
            cod_inmueble=tb_Inmueble.objects.get(id=request.POST['cod_inmueble_id'])



        )
        new_des.save()

        update_admin=tb_Admin_Inmueble.objects.get(id=tb_Admin_Inmueble.objects.filter(cod_inmueble=request.POST['cod_inmueble_id'], estado="ocupado",
                                                  cod_empleado=request.POST['cod_empleado_id']))
        update_admin.estado="devuelto"
        update_admin.save()

        update_inmueble= tb_Inmueble.objects.get(id=request.POST['cod_inmueble_id'])
        update_inmueble.estado="disponible"
        update_inmueble.save()

        messages.success(request, "REGISTRADO EXITOSAMENTE")
        return redirect("/descargarInmuebleLista")

    else:
        form = Tb_DescargarInmueble()

    return render(request,'inventario/descargar_inmueble.html')

# DETALLE DE SALIDAS, REALIZA LAS SALIDAS DEL ALMACEN
@login_required()
def detalleSalida(request):
    if request.GET.get('flat') == "true":
        form = Tb_NuevoDetalleSalida(request.POST or None, request.FILES or None)
        # objetos a enviar
        resultado = tb_salida.objects.all()
        # conexion a bd

        hora = time.strftime('%Y-%m-%d')
        try:
            if request.GET.get('flat') == "true":
                new_salida = tb_salida(fecha_registro_salida=hora, usuario_regis=request.user)
                new_salida.save()

                cur = connection.cursor()
                cur.execute("select count(*)from inventariohonducorapp_tb_salida;")
                rowc = cur.fetchone()
                valor_cod = rowc[0]
                cur.close
                codigo = valor_cod

                return render(request, 'inventario/nuevo_detalle_salida_get.html', {'form': form, 'codigo': codigo})

        except Exception:
            hora = time.strftime('%Y-%m-%d')

    else:
        form = Tb_NuevoDetalleSalida()

    return render(request, 'inventario/nuevo_detalle_salida_get.html')


@login_required()
def nuevoDetalleSalida2(request):
    bandera = request.GET.get('flag')

    if bandera == "eliminar":
        try:
            delete_salida = tb_detalle_salida.objects.get(id=request.GET.get('cod_det_salida'))
            delete_salida.delete()
            # ==================================================================================
            # recupera el codigo del detalle del articulo
            id_art = tb_DetalleArticulo.objects.filter(codigo_barras=request.GET.get('cod_barrasE')).values(
                'cod_articulo')
            # recupera el codigo del articulo, una vez que se ha recuperado entonces realiza un update a la tabla articulo
            # el update es para descargar unidades del inventario
            articulo = tb_Articulo.objects.get(id=id_art)
            articulo.existencia = F('existencia') + request.GET.get('cantidadE')
            articulo.save()
            # recupera el id del detalle articulo y luego realiza un update a la tabla detalle articulo para descargar las unidades
            # del inventario
            detalle_art = tb_DetalleArticulo.objects.get(
                id=tb_DetalleArticulo.objects.filter(codigo_barras=request.GET.get('cod_barrasE')))
            detalle_art.unidades = F('unidades') + request.GET.get('cantidadE')
            detalle_art.save()

            # ==================================================================================
            articulo_send= tb_Articulo.objects.all()
            detalle_art_send= tb_DetalleArticulo.objects.all()
            codigo_s4 = request.GET.get('cod_salida')
            salidas = tb_detalle_salida.objects.filter(cod_salida_id=codigo_s4)
            return render(request, 'inventario/nuevo_detalle_salida.html', {'salidas': salidas,'articulos':articulo_send,'detalle_art':detalle_art_send})
        except Exception:
            articulo_send = tb_Articulo.objects.all()
            detalle_art_send = tb_DetalleArticulo.objects.all()
            codigo_s4 = request.GET.get('cod_salida')
            salidas = tb_detalle_salida.objects.filter(cod_salida_id=codigo_s4)
            return render(request, 'inventario/nuevo_detalle_salida.html', {'salidas': salidas,'articulos':articulo_send,'detalle_art':detalle_art_send})

    elif request.method == "GET":
        codigo = request.GET.get('cod_salida')
    # primer try
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

            existencia_real = tb_DetalleArticulo.objects.filter(codigo_barras=request.GET.get('cod_barras')).values(
                "unidades")

            for sub in existencia_real:
                for key in sub:
                    sub[key] = int(sub[key])
                    exis_real = sub[key]

            existencia = int(request.GET.get('cantidad'))

            # primer if | primer if
            if valida_cod_barras == 0:
                articulo_send = tb_Articulo.objects.all()
                detalle_art_send = tb_DetalleArticulo.objects.all()
                codigo_s1 = request.GET.get('cod_salida')
                salidas = tb_detalle_salida.objects.filter(cod_salida=codigo_s1)
                messages.error(request, "EL CODIGO DE BARRAS ES INCORRECTO")

                return render(request, 'inventario/nuevo_detalle_salida.html', {'salidas': salidas,'articulos':articulo_send,'detalle_art':detalle_art_send})

            elif existencia > exis_real:
                articulo_send = tb_Articulo.objects.all()
                detalle_art_send = tb_DetalleArticulo.objects.all()
                codigo_s2 = request.GET.get('cod_salida')
                salidas = tb_detalle_salida.objects.filter(cod_salida=codigo_s2)
                messages.error(request, "LA CANTIDAD A ENVIAR SOBREPASA LA EXISTENCIA REAL")
                return render(request, 'inventario/nuevo_detalle_salida.html', {'salidas':salidas,'articulos':articulo_send,'detalle_art':detalle_art_send})

            else:
                codigo = request.GET.get('cod_salida')
                # aqui se va con un try
                hora = time.strftime('%Y-%m-%d')

                try:

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

                    )
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

                    messages.success(request, "REGISTRADO EXITOSAMENTE")

                    articulo_send = tb_Articulo.objects.all()
                    detalle_art_send =tb_DetalleArticulo.objects.all()
                    salidas = tb_detalle_salida.objects.filter(cod_salida=codigo)
                    return render(request, 'inventario/nuevo_detalle_salida.html', {'salidas': salidas,'articulos':articulo_send,'detalle_art':detalle_art_send})
                except Exception:
                    articulo_send = tb_Articulo.objects.all()
                    detalle_art_send = tb_DetalleArticulo.objects.all()
                    codigo_s4 = request.GET.get('cod_salida')
                    salidas = tb_detalle_salida.objects.filter(cod_salida_id=codigo_s4)
                    return render(request, 'inventario/nuevo_detalle_salida.html', {'salidas': salidas,'articulos':articulo_send,'detalle_art':detalle_art_send})


    except:
        articulo_send = tb_Articulo.objects.all()
        detalle_art_send = tb_DetalleArticulo.objects.all()
        codigo_s4 = request.GET.get('cod_salida')
        salidas = tb_detalle_salida.objects.filter(cod_salida_id=codigo_s4)
        return render(request, 'inventario/nuevo_detalle_salida.html', {'salidas': salidas,'articulos':articulo_send,'detalle_art':detalle_art_send})

    else:

        return render(request, 'inventario/nuevo_detalle_salida.html')

#============================================================================== MODIFICAR ===========================================

# ================================================================================MODIFICAR ARTICULO
@login_required()
def ModificarArticulo2(request):
    if request.method == "POST":
        try:
            form = Tb_ModificarArticulo(request.POST or None, request.FILES or None)
            update_articulo = tb_Articulo.objects.get(id=request.POST['cod_art'])
            update_articulo.nombre_art = request.POST['nombre_art']
            update_articulo.descrip = request.POST['descrip']
            update_articulo.cod_categoria_id = tb_Articulo.objects.get(id=request.POST['cod_categoria'])
            update_articulo.imagen_art=request.FILES['imagen_art']
            update_articulo.usuario_regis=str(request.user)
            update_articulo.save()

            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarArticulo")

        except:
            form = Tb_ModificarArticulo(request.POST or None, request.FILES or None)
            update_articulo = tb_Articulo.objects.get(id=request.POST['cod_art'])
            update_articulo.nombre_art = request.POST['nombre_art']
            update_articulo.descrip = request.POST['descrip']
            update_articulo.cod_categoria_id = tb_Articulo.objects.get(id=request.POST['cod_categoria'])
            update_articulo.usuario_regis=str(request.user)
            update_articulo.save()
            bandera="soy una bandera"

            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarArticulo",{'bandera':bandera})


    else:
        form =Tb_ModificarArticulo()
        return render(request, 'inventario/modificar_articulo.html',{'form':form})

#================================== MODIFICAR MOBILIARIO
@login_required()
def ModificarMobiliario2(request):
    if request.method == "POST":
        try:
            form = Tb_ModificarMobiliario(request.POST or None, request.FILES or None)
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
            update_mobiliario.usuario_regis=str(request.user)
            update_mobiliario.save()

            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarMobiliario")

        except:
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
            update_mobiliario.usuario_regis=str(request.user)
            update_mobiliario.save()

            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarMobiliario")


    else:
        form =Tb_ModificarMobiliario()
        return render(request, 'inventario/modificar_mobiliario.html',{'form':form})

#================================================================== MODIFICAR VEHICULOS
@login_required()
def ModificarVehiculo2(request):
    if request.method == "POST":
        try:
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
            update_vehiculo.imagen_vehi = request.FILES['imagen_vehi']
            update_vehiculo.usuario_regis =str(request.user)
            update_vehiculo.save()

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
            update_vehiculo.usuario_regis=str(request.user)

            update_vehiculo.save()
            hola=1
            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarVehiculo",{'codigo':hola})



    else:
        form =Tb_ModificarArticulo()
        return render(request, 'inventario/modificar_vehiculo.html',{'form':form})

#=========================================================================== MODIFICAR INMUEBLE
@login_required()
def ModificarInmueble2(request):
    if request.method == "POST":
        try:
            form = Tb_ModificarInmueble(request.POST or None, request.FILES or None)
            update_inmueble = tb_Inmueble.objects.get(id=request.POST['cod_imb'])
            update_inmueble.ubicacion= request.POST['ubicacion']
            update_inmueble.destino_actual=request.POST['destino_actual']
            update_inmueble.numero_instrumento=request.POST['numero_instrumento']
            update_inmueble.fecha_otorgamiento=datetime.datetime.strptime(request.POST['fecha_otorgamiento'], "%m/%d/%Y")
            update_inmueble.notario_otorgante=request.POST['notario_otorgante']
            update_inmueble.valor_adq=request.POST['valor_adquisicion']
            update_inmueble.forma_adquisicion=request.POST['forma_adquisicion']
            update_inmueble.fecha_acuerdo=datetime.datetime.strptime(request.POST['fecha_acuerdo'], "%m/%d/%Y")
            update_inmueble.observaciones=request.POST['observacion']
            update_inmueble.num_registro_propiedad=request.POST['num_registro_propiedad']
            update_inmueble.folio_registro_propiedad=request.POST['folio_registro_propiedad']
            update_inmueble.tomo_registro_propiedad=request.POST['tomo_registro_propiedad']
            update_inmueble.num_catastro=request.POST['num_catastro']
            update_inmueble.otorgante=request.POST['otorgante']
            update_inmueble.ciudad=request.POST['ciudad']
            update_inmueble.usuario_regis=str(request.user)
            update_inmueble.save()


            messages.success(request, "MODIFICADO EXITOSAMENTE")
            return redirect("/modificarInmueble")

        except:

            messages.success(request, "ERROR AL MODIFICAR INMUEBLE")
            return redirect("/modificarInmueble")


    else:
        form =Tb_ModificarInmueble()
        return render(request, 'inventario/modificar_inmueble.html',{'form':form})

# =======================================================================================================
# MODIFICAR ENTRADA
@login_required()
def ModificarEntrada2(request):
    if request.method == "POST":
        try:
            codigo_b=request.POST['codigo']
            # establece conexion a la bd
            cur = connection.cursor()
            # cur.callproc("retornacodbarras", (codigo,))
            # llamada a procedimiento almacenado
            cur.execute("select recupera_unidades_entradas(%s);", (codigo_b,))
            # recupera el valor del procedimiento almacenado
            row = cur.fetchone()
            unidades_viejas = row[0]

            # cierra la conexcion a la bd
            cur.close()
            unidades_nuevas=request.POST['unidades']
            #if unidades_viejas >= unidades_nuevas:
            #cod_articulo2
            update_articulo=tb_Articulo.objects.get(id=request.POST['cod_articulo2'])
            update_articulo.existencia= F('existencia') - unidades_viejas
            update_articulo.usuario_regis=str(request.user)
            update_articulo.save()

            update_articulo2 = tb_Articulo.objects.get(id=request.POST['cod_articulo2'])
            update_articulo2.existencia = F('existencia') + unidades_nuevas
            update_articulo2.usuario_regis=str(request.user)
            update_articulo2.save()



            update_entrada=tb_DetalleArticulo.objects.get(id=request.POST['codigo'])
            update_entrada.valor=request.POST['valor']
            update_entrada.unidades=request.POST['unidades']
            update_entrada.precio_unitario=request.POST['precio_unitario']
            update_entrada.usuario_regis=str(request.user)
            update_entrada.save()

            messages.\
                success(request,"LA ENTRADA HA SIDO MODIFICADA EXITOSAMENTE")
            return redirect("/verEntradaModificar")
        except Exception:
            messages.success(request, "ERROR AL MODIFICAR ENTRADA")
            return redirect("/modificarEntradas2")
    else:
        return render(request, 'inventario/modificar_entrada.html')
#========================================================================================================

#============================================================= DAR DE BAJA
#DAR BAJA MOBILIARIO
@login_required()
def DarBajaMobiliario(request):

        try:

            dar_baja=tb_Mobiliario.objects.get(id=request.GET.get('codigo'))
            dar_baja.estado_mobiliario="bajado"
            dar_baja.save()


            messages.success(request, "EL MOBILIARIO FUE DADO DE BAJA")
            return redirect("/bajaMobiliario")

        except:

            messages.success(request, "ERROR AL DAR DE BAJA A MOBILIARIO")
            return redirect("/bajaMobiliario")

#DAR BAJA VEHICULOS
@login_required()
def DarBajaVehiculo(request):

        try:

            dar_baja=tb_Vehiculo.objects.get(id=request.GET.get('codigo'))
            dar_baja.estado_vehi="bajado"
            dar_baja.save()


            messages.success(request, "EL VEHICULO FUE DADO DE BAJA")
            return redirect("/bajaVehiculo")

        except:

            messages.success(request, "ERROR AL DAR DE BAJA A MOBILIARIO")
            return redirect("/bajaVehiculo")

#DAR DE BAJA A UN ARTICULO
@login_required()
def DarBajaArticulo(request):

        try:

            dar_baja=tb_Articulo.objects.get(id=request.GET.get('codigo'))
            dar_baja.estado_articulo="bajado"
            dar_baja.save()


            messages.success(request, "EL ARTICULO FUE DADO DE BAJA")
            return redirect("/bajaArticulo")

        except:

            messages.success(request, "ERROR AL DAR DE BAJA A MOBILIARIO")
            return redirect("/bajaArticulo")

class ListaSalidaPrueba(ListView):
    model = tb_Inmueble
    template_name = 'inventario/nuevo_detalle_salida.html'
    context_object_name = 'inmuebles'


# ============================ CONSULTAS EN FORMULARIOS ===============================
# --------------------------------------------------------------------------------------

# VISTAS DE INMUBLES
class ListarInmuebleAsignar(ListView):
    model = tb_Inmueble
    template_name = 'inventario/listar_inmueble_asignar.html'
    context_object_name = 'inmuebles'
    queryset = tb_Inmueble.objects.all().filter(estado="disponible")


class ListarInmueble(ListView):
    model = tb_Inmueble
    template_name = 'inventario/listar_inmueble_index.html'
    context_object_name = 'inmuebles'
    queryset = tb_Inmueble.objects.all().filter(estado="disponible")


# LISTA LOS EMPLEADOS PARA ASIGNAR UN INMUEBLE
class ListarEmpleadoInmueble(ListView):
    model = tb_Empleado
    template_name = 'inventario/buscar_empleado_inmueble.html'
    context_object_name = 'empleado'
    queryset = tb_Empleado.objects.all().order_by('id')



class ListarDescargarInmueble(ListView):
    model = tb_Admin_Inmueble
    template_name = 'inventario/listar_inmueble_descargar.html'
    context_object_name = 'inmuebles'
    queryset = tb_Admin_Inmueble.objects.filter(estado="ocupado")

    def get_context_data(self, **kwargs):
        context = super(ListarDescargarInmueble, self).get_context_data(**kwargs)
        context['mobiliarios'] = tb_Inmueble.objects.all()
        context['empleados'] = tb_Empleado.objects.all()

        return context

class ListarInmuebleModificar(ListView):
        model = tb_Inmueble
        template_name = 'inventario/listar_inmueble_modificar.html'
        context_object_name = 'inmuebles'


# ============================================================FIN DE  VISTAS INMUEBLES

# este listview es para consultar los mobiliarios por agencia
class ListarAgenciasMobiliario(ListView):
    model = Agencia
    template_name = 'inventario/buscar_agencia_mobiliario.html'
    context_object_name = 'agencias'


# este listview es para consultar los mobiliarios por agencia
# esta clase recibe dos parametros get para realizar una consulta mas expedita
class ListarAgenciasMobiliario2(ListView):
    model = tb_Mobiliario
    template_name = 'inventario/inventario_mobiliario_agencia.html'
    context_object_name = 'mobiliarios'

    def get_queryset(self):
        qs = super(ListarAgenciasMobiliario2, self).get_queryset()
        # la sentencia de abajo recupera el pk de la url


        return qs.filter(ubicacion_actual=self.request.GET.get('noma'), estado_mobiliario="activo")


# Listview para la pagina buscar_articulo.html
# este listview devuelve todos los articulos dentro del inventarios
class Personas(ListView):
    model = tb_Articulo
    template_name = 'Inventario/buscar_articulo.html'
    context_object_name = 'personas'
#LISTAR ALERTA PARA EXISTENCIAS
class AlertaExistencias(ListView):
    model = tb_Articulo
    template_name = 'inventario/alerta_existencias.html'
    context_object_name = 'articulos'
    queryset = tb_Articulo.objects.filter(existencia__lte=10)

#LISTAR ARTICULOS DAR DE BAJA
class  ListarDarBajaArticulo(ListView):
    model = tb_Articulo
    template_name = 'Inventario/dar_baja_articulo.html'
    context_object_name = 'articulos'

# Listview para la pagina ver_entradas.html
# este listview devuelve todos las entradas registradas dentro del inventarios
class VerEntradas(ListView):
    model = tb_entrada
    template_name = 'inventario/ver_entradas.html'
    context_object_name = 'entradas'

# LISTAS ENTRADAS PARA SER MODIFICADAS
class VerEntradasModificar(ListView):
    model = tb_DetalleArticulo

    template_name = 'inventario/listar_entradas_modificar.html'
    context_object_name = 'entradas'
# Listview para la pagina ver_salidas.html
# este listview devuelve todos las salidas registradas dentro del inventarios
class VerSalidas(ListView):
    model = tb_detalle_salida
    template_name = 'inventario/ver_salidas.html'
    context_object_name = 'salidas'


# Listview para la pagina buscar_mobiliario.html
# este listview devuelve todos los mobiliarios que se encuentran disponibless
class BuscarMobiliario(ListView):
    model = tb_Mobiliario
    template_name = 'inventario/buscar_mobiliario.html'
    context_object_name = 'mobiliario'

    def get_queryset(self):
        qs = super(BuscarMobiliario, self).get_queryset()
        return qs.filter(estado="bueno")


# Listview para la pagina buscar_mobiliario2.html
# este listview devuelve todos los mobiliarios que se encuentran disponibles
class BuscarMobiliario2(ListView):
    model = tb_Mobiliario
    template_name = 'inventario/buscar_mobiliario2.html'
    context_object_name = 'mobiliario'

    def get_queryset(self):
        qs = super(BuscarMobiliario2, self).get_queryset()
        return qs.filter(estado="disponible")

#MODIFICAR MOBILIARIO
class ListarModificarMobiliario(ListView):
    model = tb_Mobiliario
    template_name = 'inventario/listar_modificar_mobiliario.html'
    context_object_name = 'mobiliario'

#ASIGNAR MOBILIARIO DETALLE
class MobiliarioDetalle11(ListView):
    model = tb_Mobiliario
    template_name = 'inventario/asignar_mobiliario2_detalle.html'
    context_object_name = 'mobiliarios'
#LISTAR MOBILIARIO PRESTADO
class ListarMobiliarioPrestadoSolo(ListView):

    template_name = 'inventario/listar_mobiliario_prestado_solo.html'
    context_object_name = 'mobiliarios'
    queryset = tb_Mobiliario.objects.all()

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
    template_name = 'inventario/buscar_empleado_mobiliario.html'
    context_object_name = 'empleado'

#empleado que se asigna a detalle mobiliario
class BuscarEmpleado10(ListView):
    model = tb_Empleado
    template_name = 'inventario/asignar_mobiliario2_empleado.html'
    context_object_name = 'empleado'

# Listview para la pagina buscar_empleado_mobiliario.html
# este listview devuelve todos los empleados
class BuscarEmpleadoMP(ListView):
    model = tb_Empleado
    template_name = 'inventario/buscar_empleado_mobiliarioP.html'
    context_object_name = 'empleado'

class ListarMobiliarioDarDeBaja(ListView):
    model = tb_Mobiliario
    template_name = 'inventario/dar_baja_mobiliario.html'
    context_object_name = 'mobiliario'

# ================================================================
class BuscarMobiliarioPrestado(ListView):
    template_name = 'inventario/buscar_mobiliarioPrestado.html'
    context_object_name = 'mobiliarioP'
    queryset = tb_MobiliarioPrestado.objects.filter(estado="ocupado")

    def get_context_data(self, **kwargs):
        context = super(BuscarMobiliarioPrestado, self).get_context_data(**kwargs)
        context['mobiliario'] = tb_Mobiliario.objects.all()
        context['empleados'] = tb_Empleado.objects.all()

        return context

#VER EXISTENCIAS DE LOS ARTICULOS
class VerExistenciasArticulos(ListView):
    model = tb_Articulo
    template_name = 'inventario/ver_existencias.html'
    context_object_name = 'existencias'
    queryset = tb_Articulo.objects.filter(existencia__gte=1)

#VER ARTICULOS QUE NO TIENEN EXISTENCIA
class VerSinExistenciasArticulos(ListView):
    model = tb_Articulo
    template_name = 'inventario/ver_no_existencias.html'
    context_object_name = 'existencias'
    queryset = tb_Articulo.objects.filter(existencia=0)

class VerExistenciasArticulosPDF(ListView):
    model = tb_Articulo
    template_name = 'inventario/lista_existencias_articulosPDF.html'
    context_object_name = 'existencias'


class VerExistenciasArticulosDet(ListView):
    model = tb_DetalleArticulo
    template_name = 'inventario/buscar_articulo_detalle.html'
    context_object_name = 'existencias'


class BuscarMobiliarioIndex(ListView):
    model = tb_Mobiliario
    template_name = 'inventario/buscar_mobiliario_index.html'
    context_object_name = 'existencias'


class BuscarAticulosSolamente(ListView):
    model = tb_Articulo
    template_name = 'inventario/buscar_articulos_solo.html'
    context_object_name = 'articulos'


# Listview para la pagina ver_entradas.html
# este listview devuelve todos las entradas registradas dentro del inventarios
class VerArticulosEntradas(ListView):
    model = tb_Articulo
    template_name = 'inventario/listar_articulosEntradas.html'
    context_object_name = 'existencias'


# Este Listview sirve para la url incidenciaArticulo
# sirve para listar todos los detalles de articulos

class ListaArticulosIncidentias(ListView):
    model = tb_DetalleArticulo
    template_name = 'inventario/ver_det_incidencias.html'
    context_object_name = 'existencias'


# PARA MODIFICAR ARTICULOS
class ModificarArticulo(ListView):
    model = tb_Articulo
    template_name = 'inventario/listar_modificar_articulo.html'
    context_object_name = 'articulos'


# ========================================= VISTAS DE VEHICULOS =========================================================

# VEHICULOS QUE SE VAN A DAR DE BAJA
class ListarVehiculosDarBaja(ListView):
    model = tb_Vehiculo
    template_name = 'inventario/dar_baja_vehiculo.html'
    context_object_name = 'vehiculos'

# este listview es para listar todos los vehiculos
class ListarVehiculos(ListView):
    model = tb_Vehiculo
    template_name = 'inventario/buscar_vehiculo.html'
    context_object_name = 'vehiculos'


# este listview es para listar los vehiculos que se van a asignar a los empleados
class ListarVehiculosAsignar(ListView):
    model = tb_Vehiculo
    template_name = 'inventario/listar_vehiculos_asinar.html'
    context_object_name = 'vehiculos'


# este listview es para listar los vehiculos que se van a descargara los empleados
class ListarVehiculosDescargar(ListView):
    template_name = 'inventario/lista_vehiculo_descargar.html'
    context_object_name = 'vehiculos'
    queryset = tb_Vehiculo.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ListarVehiculosDescargar, self).get_context_data(**kwargs)
        context['asignado'] = tb_VehiculoAsignado.objects.all()
        context['empleados'] = tb_Empleado.objects.all()

        return context


# lista incidentes de articulos
class ListarIncidenteArticulo2(ListView):
    template_name = 'inventario/listar_incidente_articulo.html'
    context_object_name = 'incidentes'
    queryset = tb_incidenciaArticulo.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ListarIncidenteArticulo2, self).get_context_data(**kwargs)
        context['articulo'] = tb_Articulo.objects.all()
        context['det_art'] = tb_DetalleArticulo.objects.all()

        return context


# este listview es para listar los empleados que se van a asignar a los vehiculos
class ListarEmpleadosAsignarVehi(ListView):
    model = tb_Empleado
    template_name = 'inventario/asignar_vehiculo_empleado.html'
    context_object_name = 'empleados'

#LISTAR LOS VEHICULOS QUE SE VAN A MODIFICAR
class ListarVehiculosModificar(ListView):
    model = tb_Vehiculo
    template_name = 'inventario/listar_vehiculos_modificar.html'
    context_object_name = 'vehiculos'

# ===========================================================================
class pruebaListview(ListView):
    model = tb_DetalleArticulo
    template_name = 'inventario/prueba.html'
    context_object_name = 'existencias'

    def get_context_data(self, **kwargs):
        context = super(pruebaListview, self).get_context_data(**kwargs)
        context['existencias'] = tb_DetalleArticulo.objects.values('cod_articulo_id').annotate(
            total=Sum(F('unidades') * F(('precio_unitario')), output_field=FloatField()))

        context['existencias2'] = tb_Articulo.objects.all()
        return context


class AncillaryDetail(ListView):
    model = tb_DetalleArticulo

    def get_queryset(self):
        qs = super(AncillaryDetail, self).get_queryset()

        # la sentencia de abajo recupera el pk de la url
        return qs.filter(cod_articulo_id=self.kwargs.get('pk'), unidades__gte=1)


# ======================= Ver Salidas Fecha =======================================
class VerSalidaFecha(ListView):
    context_object_name = 'existencias'
    template_name = 'inventario/salidas_fecha.html'

    queryset = tb_detalle_salida.objects.all()

    def get_queryset(self):

        qs = super(VerSalidaFecha, self).get_queryset()
        try:
            fecha_inicial = datetime.datetime.strptime(self.request.GET.get('starfecha'), "%m/%d/%Y")
            fecha_final = datetime.datetime.strptime(self.request.GET.get('endfecha'), "%m/%d/%Y")
            return qs.filter(fecha_registro_salida__range=(fecha_inicial, fecha_final))


        except Exception:

            fecha_final = "2010-07-07"
            fecha_inicial = "2010-07-07"
            return qs.filter(fecha_registro_salida__range=(fecha_inicial, fecha_final))

    def get_context_data(self, **kwargs):
        context = super(VerSalidaFecha, self).get_context_data(**kwargs)
        context['articulos'] = tb_Articulo.objects.all()
        context['det_articulos'] = tb_DetalleArticulo.objects.all()

        # And so on for more models
        return context


# ======================= Ver Entradas Fecha =======================================
class VerEntradaFecha(ListView):
    model = tb_entrada
    template_name = 'inventario/entradas_fecha.html'
    context_object_name = 'existencias'

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

class BitacoraMobiliarioFecha(ListView):
    model = tb_audit_mobiliario
    template_name = 'inventario/bitacora_mobiliario_fecha.html'
    context_object_name = 'bitacoras'

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

class BitacoraVehiculoFecha(ListView):
    model = tb_audit_det_vehiculo
    template_name = 'inventario/bitacora_vehiculo_fecha.html'
    context_object_name = 'bitacoras'

    def get_queryset(self):

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

class BitacoraEntradaFecha(ListView):
    model = tb_audit_entrada
    template_name = 'inventario/bitacora_entrada_fecha.html'
    context_object_name = 'bitacoras'

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
class BitacoraSalidaFecha(ListView):
    model = tb_audit_salida
    template_name = 'inventario/bitacora_salida_fecha.html'
    context_object_name = 'bitacoras'

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

class ReportePersonasPDF(View):
    def cabecera(self, pdf):
        # Utilizamos el archivo logo_django.png que está guardado en la carpeta media/imagenes
        archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
        # Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(archivo_imagen, 40, 750, 120, 90, preserveAspectRatio=True)

        # Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 16)
        # Dibujamos una cadena en la ubicación X,Y especificada
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
        # Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        # Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer)
        # Llamo al método cabecera donde están definidos los datos que aparecen en la cabecera del reporte.
        self.cabecera(pdf)
        y = 550
        self.tabla(pdf, y)
        # Con show page hacemos un corte de página para pasar a la siguiente
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def tabla(self, pdf, y):
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('CODIGO', 'NOMBRE DEL ARTICULO', 'UNIDADES', 'VALOR LPS')
        # Creamos una lista de tuplas que van a contener a las personas

        cursor = connection.cursor()
        cursor.execute(
            "select a.id,a.nombre_art,a.existencia, sum(d.unidades*d.precio_unitario)from inventariohonducorapp_tb_detallearticulo d,inventariohonducorapp_tb_articulo a where d.cod_articulo_id=a.id group by a.nombre_art,a.id,a.existencia")

        # esta malo
        detalles = [(item[0], item[1], item[2], item[3]) for item in cursor.fetchall()]
        print(detalles)
        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 8 * cm, 3 * cm, 4 * cm])
        # Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                # Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, 1), 10),
            ]
        ))
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 60, y)


# =========================REPORTE MOBILIARIO=========================================
class ReporteMobiliarioPDF(View):
    def cabecera(self, pdf):
        # Utilizamos el archivo logo_django.png que está guardado en la carpeta media/imagenes
        archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
        # Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(archivo_imagen, 40, 750, 120, 90, preserveAspectRatio=True)

        # Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 16)
        # Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(250, 790, u"HONDUCOR")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(150, 700, u"REPORTE DE MOBILIARIO EXISTENTE")

    def get(self, request, *args, **kwargs):
        # Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        # Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer)

        # Llamo al método cabecera donde están definidos los datos que aparecen en la cabecera del reporte.
        self.cabecera(pdf)
        y = 600
        self.tabla(pdf, y)
        # Con show page hacemos un corte de página para pasar a la siguiente
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def tabla(self, pdf, y):
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('CODIGO', 'INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
        # Creamos una lista de tuplas que van a contener a las personas



        # esta malo
        detalles = [(item.id, item.cod_inventario, item.marca, item.modelo, item.serie) for item in
                    tb_Mobiliario.objects.all().filter(estado="disponible")]

        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 3 * cm, 3 * cm, 4 * cm, 4 * cm])
        # Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                # Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, 1), 10),
            ]
        ))
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 60, y)


# ================================== DOCUMENTOS EN EXCEL =========================================

def export_users_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

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

    columns = ['CODIGO MOBILIARIO', 'CATEGORIA' ,'MARCA', 'MODELO', 'SERIE', 'CODIGO DE INVENTARIO', 'COSTO UNITARIO ']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    categoria = tb_CategoriaMobiliario.objects.values_list('id', 'nombre_categoria')
    rows = tb_Mobiliario.objects.values_list('id', 'cod_cat_mobiliario', 'marca', 'modelo', 'serie', "cod_inventario",
                                             'costo_uni')
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
class BitacoraMobiliario(ListView):
    template_name = 'inventario/bitacora_mobiliario.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_mobiliario.objects.all().order_by('id').reverse()


class BitacoraDetEntrada(ListView):
    template_name = 'inventario/bitacora_det_entrada.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_det_articulo.objects.all().order_by('id').reverse()


class BitacoraEntrada(ListView):
    template_name = 'inventario/bitacora_entrada.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_entrada.objects.all().order_by('id').reverse()


class BitacoraSalida(ListView):
    template_name = 'inventario/bitacora_salida.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_salida.objects.all().order_by('id').reverse()


class BitacoraVehiculo(ListView):
    template_name = 'inventario/bitacora_vehiculo.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_det_vehiculo.objects.all().order_by('id').reverse()

class BitacoraLogin(ListView):
    template_name = 'inventario/bitacora_login.html'
    context_object_name = 'bitacoras'
    queryset = tb_audit_login.objects.all().order_by('id').reverse()
#================================================================= PROVEEDORES
#LISTAR PROVEEDORES
class ListarProveedor(ListView):
    template_name = 'inventario/listar_proveedor.html'
    context_object_name = 'proveedores'
    model=tb_proveedor

#LISTAR PROVEEDORES A MODIFICAR
class ListarProveedorModificar(ListView):
    template_name = 'inventario/listar_proveedor_modificar.html'
    context_object_name = 'proveedores'
    model=tb_proveedor

#NUEVO PROVEEDOR
@login_required()
def nuevoProveedor(request):
    if request.method == "POST":
        form = Tb_ProveedorForm(request.POST or None, request.FILES or None)
        if form.is_valid():

            new_proveedor= tb_proveedor(
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
            new_proveedor.save(form)




            messages.success(request,"REGISTRADO EXITOSAMENTE")
            return redirect("/add_post")


    else:
        form = Tb_ProveedorForm()

    return render(request, 'Inventario/nuevo_proveedor.html', {'form': form})

class AuthorUpdate(UpdateView):
    model = tb_proveedor
    fields = ['name']
    template_name_suffix = '_update_form'