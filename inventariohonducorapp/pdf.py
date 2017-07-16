import datetime

from django.db import connection
from django.db.models import Sum, F, FloatField
from django.http import HttpResponse
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors, styles
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table

from InventarioHONDUCOR import settings
from inventariohonducorapp.models import tb_Mobiliario, tb_entrada, tb_salida, tb_DetalleArticulo, tb_Articulo, \
    tb_CategoriaMobiliario, tb_Empleado, User
import time


def Print_PDF(request):
    # TIPO DE ARCHIVO A CREAR
    response = HttpResponse(content_type='application/pdf')
    # NOMBRE DEL ARCHIVO
    response['Content-Disposition'] = 'attachment; filename="resume.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # TIPO DE FUENTES
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 8)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(225, 790, "BITÁCORA DETALLE DE ENTRADAS")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    # ENCABEZADO


    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 740
    # TABLA QUE SE LLENA
    # ABRIR CONEXCION A BD
    cur = connection.cursor()
    cur.execute("select* from  inventariohonducorapp_tb_audit_det_articulo")
    rowA = cur.fetchall()
    # CERRAR CONEXCION A BD
    cur.close()

    # DIBUJA LOS ENCABEZADOS EN EL PDF
    linea = "________________________________________________________________________________________________________________________________________"
    p.drawString(20, 750,
                 "ID      FECHA                      TABLA                                          ACCION               USUARIO")

    # DIBUJA LOS DATOS EN EL PDF
    p.drawString(20, contador, linea)
    for row in rowA:
        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[2])
        str4 = str(row[3])
        str5 = str(row[6])
        str6 = str(row[5])
        if str4 == "None":
            str4 = "NONE                                                                             "
        if str3 == "I":
            str3 = "INSERTAR"
        elif str3 == "U":
            str3 = "MODIFICAR"
        elif str3 == "D":
            str3 = "ELIMINAR"
        strlarge = str1 + " - " + str6 + " - " + str2 + " - " + str3 + " - " + str5
        contador = contador - 20

        p.drawString(20, contador, strlarge)
        p.drawString(20, contador - 6, linea)
        if contador <= 20:
            p.showPage()
            contador = 740
            p.drawString(20, contador, linea)

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# PDF DE SALIDA
def PDFSalida(request):
    # DEFINE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # NOMBRE DEL ARCHIVO
    response['Content-Disposition'] = 'attachment; filename="resume.pdf"'
    encabezados = ('      ID', '      CODIGO DE BARRAS', 'CANTIDAD', 'ARTICULO')
    # Creamos una lista de tuplas que van a contener a las personas
    # FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 8)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/encabezado_honducor.png'
    p.drawImage(archivo_imagen, 120, 770, 370, 65, preserveAspectRatio=True)
    # TITULO

    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    nombre_recibe = request.GET.get('personal_recibe')
    agencia_recibe = request.GET.get('agencia')
    registro = request.GET.get('cod_salida')
    usuario_regis = tb_salida.objects.filter(id=request.GET.get('cod_salida')).values('usuario_regis')
    # DATOS A USAR
    detalle_articulo = tb_DetalleArticulo.objects.all()
    row_articulo = tb_Articulo.objects.all()
    for sub in usuario_regis:
        for key in sub:
            sub[key] = sub[key]
            usuario = sub[key]

    # DIBUJA LOS DATOS EN EL PDF

    p.drawString(10, 750, "FECHA: " + str(fecha))
    p.drawString(10, 730, "PARA: " + str(nombre_recibe) + " / " + agencia_recibe)
    p.drawString(10, 710, "REGISTRADO POR: " + str(request.user))
    p.drawString(450, 750, "REGISTRO N°: " + str(registro))
    p.drawString(10, 690,
                 "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    p.drawString(10, 680,
                 "ID      CÓDIGO DE BARRAS                     CANTIDAD                                               NOMBRE DEL ARTÍCULO")
    p.drawString(10, 672,
                 "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

    # ENCABEZADO

    codigo_b = request.GET.get('cod_salida')
    # establece conexion a la bd
    cur = connection.cursor()
    # cur.callproc("retornacodbarras", (codigo,))
    # llamada a procedimiento almacenado
    cur.execute("select*from inventariohonducorapp_tb_detalle_salida where cod_salida_id=%s;", (codigo_b,))
    # recupera el valor del procedimiento almacenado
    rowA = cur.fetchall()

    # cierra la conexcion a la bd
    cur.close()
    contador = 665
    for row in rowA:
        str_id = str(row[0])
        str_cod_barras = str(row[3])
        str_cant = str(row[2])
        str_large = str_id + "     " + str_cod_barras + "                                                " + str_cant + "          "
        contador = contador - 20

        for det in detalle_articulo:
            if det.id == row[8]:
                for art in row_articulo:
                    if art.id == det.cod_articulo_id:
                        str_articulo = art.nombre_art
                        p.drawString(10, contador,
                                     str_large + "                                             " + str_articulo)

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# ----------------------------------------------------------------------

def PDFEnregaMobiliario(request):
    # DEFINE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # NOMBRE DEL ARCHIVO
    response['Content-Disposition'] = 'attachment; filename="acta_entrega.pdf"'
    encabezados = ('      ID', '      CODIGO DE BARRAS', 'CANTIDAD', 'ARTICULO')
    # Creamos una lista de tuplas que van a contener a las personas
    # FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 11)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/encabezado_honducor.png'
    p.drawImage(archivo_imagen, 120, 770, 370, 65, preserveAspectRatio=True)
    # TITULO

    mobiliario = tb_Mobiliario.objects.get(id=request.GET.get("mobip"))
    fecha = time.strftime('%d %b %y')
    dia = time.strftime('%d')
    mes = time.strftime('%b')
    anio = time.strftime('%y')
    # fecha que se genera
    # DIBUJA LOS DATOS EN EL PDF
    p.drawString(150, 730, "ADMINISTRACION POSTAL TONCONTÍN, TEGUCIGALPA")
    p.drawString(250, 710, "ACTA DE ENTREGA")
    p.drawString(60, 660,
                 "Yo, " + str(request.GET.get('nombre')) + ", con número de identidad " + str(request.GET.get('cod_e')))
    p.drawString(60, 640, "he recibido de Bienes Nacionales el siguiente equipo para uso de la oficina siendo ")
    p.drawString(60, 620, ", responsable de su cuidado y conservación.")
    p.drawString(60, 600, "Lo presentaré al ser requeridos por la autoridad competente en caso de que resulte ")
    p.drawString(60, 580, "responsable de bienes faltantes o dañados. De no hacerme responsable por el valor ")
    p.drawString(60, 560, "monetario de los mismos, autorizo a que se deduzca de mi salario, la cantidad ")
    p.drawString(60, 540, "correspondiente.")
    # campos de el mobiliario

    # DIBUJA LOS DATOS EN EL PDF
    p.drawString(210, 530, "DESCRIPCIÓN DE MOBILIARIO ")
    p.drawString(60, 500, "MARCA: " + mobiliario.marca)
    p.drawString(60, 480, "MODELO: " + mobiliario.modelo)
    p.drawString(60, 460, "SERIE: " + mobiliario.serie)
    p.drawString(60, 440, "CÓDIGO  DE INVENTARIO: " + mobiliario.cod_inventario)
    p.drawString(60, 420, "COSTO UNITARIO: lps " + str(mobiliario.costo_uni))
    p.drawString(60, 400, "DESCRIPCIÓN: " + mobiliario.descripccion)
    p.drawString(60, 380, "CATEGORÍA: " + str(mobiliario.cod_cat_mobiliario))
    p.drawString(40, 170, "Y para los fines que el interesado estime conveniente, se le extiende la presente en la ")
    p.drawString(40, 150, "Ciudad de Tegucigalpa, M.D.C a los " + str(dia) + " dias del mes de " + str(
        mes) + " de " + "20" + str(anio) + ".")
    p.drawString(40, 100, "_____________________________")
    p.drawString(40, 85, "     Personal que entrega")

    p.drawString(360, 100, "_____________________________")
    p.drawString(360, 85, "     Personal que recibe")
    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# ================================================================================PDF BITACORA ENTRADA
def PDF_Bitacora_Salida(request):
    # DEFINE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # NOMBRE DEL ARCHIVO
    response['Content-Disposition'] = 'attachment; filename="bitacora_entrada.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 8)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(225, 790, "BITÁCORA DE ENTRADAS")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    # ENCABEZADO


    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 740
    # TABLA QUE SE LLENA

    cur = connection.cursor()
    cur.execute("select* from  inventariohonducorapp_tb_audit_entrada")
    rowA = cur.fetchall()
    cur.close()

    # DIBUJA LOS DATOS EN EL PDF
    linea = "________________________________________________________________________________________________________________________________________"
    p.drawString(20, 750,
                 "ID      FECHA                      TABLA                                                               ACCION                                     USUARIO")

    p.drawString(20, contador, linea)
    for row in rowA:
        str1 = str(row[0])
        str2 = str(row[
                       1] + "                                                                                                             ")
        str3 = str(row[2] + "                                                           ")
        str4 = str(row[3])
        str5 = str(row[6])
        str6 = str(row[5])
        if str4 == "None":
            str4 = "NONE                                                                             "
        if str3 == "I" + "                                                           ":
            str3 = "INSERTAR" + "                                                           "
        if str3 == "U" + "                                                           ":
            str3 = "MODIFICAR" + "                                                           "
        if str3 == "D" + "                                                           ":
            str3 = "ELIMINAR" + "                                                           "
        if str2 == "inventariohonducorapp_tb_entrada" + "                                                                                                             ":
            str2 = "inventariohonducorapp_tb_entrada" + "                                                                                                                    "
            strlarge = str1 + " - " + str6 + " - " + str2[:52] + " - " + str3[:240] + "   - " + str5
            contador = contador - 20

            p.drawString(20, contador, strlarge)
            p.drawString(20, contador - 6, linea)
        else:
            strlarge = str1 + " - " + str6 + " - " + str2[:50] + " - " + str3[:240] + " - " + str5

        contador = contador - 20

        # DIBUJA LOS DATOS EN EL PDF

        p.drawString(20, contador, strlarge)
        p.drawString(20, contador - 6, linea)
        if contador <= 20:
            p.showPage()
            pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))

            p.setFont('Vera', 8)
            contador = 740
            p.drawString(20, 750,
                         "ID      FECHA                      TABLA                                                               ACCION                                     USUARIO")

            p.drawString(20, contador, linea)

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# ================================================================================PDF BITACORA SALIDA
def PDF_Bitacora_Salida2(request):
    # DEFINE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # NOMBRE DEL ARCHIVO
    response['Content-Disposition'] = 'attachment; filename="bitacora_salida.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 8)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(225, 790, "BITÁCORA DE SALIDAS")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    # ENCABEZADO


    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 740
    # TABLA QUE SE LLENA

    cur = connection.cursor()
    cur.execute("select* from  inventariohonducorapp_tb_audit_salida")
    rowA = cur.fetchall()
    cur.close()

    # DIBUJA LOS DATOS EN EL PDF

    linea = "________________________________________________________________________________________________________________________________________"
    p.drawString(20, 750,
                 "ID      FECHA                      TABLA                                          ACCIÓN               USUARIO")

    p.drawString(20, contador, linea)
    for row in rowA:
        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[2])
        str4 = str(row[3])
        str5 = str(row[6])
        str6 = str(row[5])
        if str4 == "None":
            str4 = "NONE                                                                             "
        if str3 == "I":
            str3 = "INSERTAR"
        elif str3 == "U":
            str3 = "MODIFICAR"
        elif str3 == "D":
            str3 = "ELIMINAR"
        strlarge = str1 + " - " + str6 + "  - " + str2 + "      - " + str3 + "      -       " + str5
        contador = contador - 20

        p.drawString(20, contador, strlarge)
        p.drawString(20, contador - 6, linea)
        if contador <= 20:
            p.showPage()
            contador = 740
            p.setFont('Vera', 8)
            p.drawString(20, contador, linea)

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# =================================== PDF BITACORA MOBILIAARIO
def PDF_Bitacora_Mobiliario(request):
    # DEFINE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # NOMBRE DEL ARCHIVO
    response['Content-Disposition'] = 'attachment; filename="bitacora_mobiliario.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 8)

    contadorP = 1
    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(225, 790, "BITÁCORA DE MOBILIARIO")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    p.drawString(550, 800, "Pag." + str(contadorP))
    # ENCABEZADO


    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 740
    # TABLA QUE SE LLENA

    cur = connection.cursor()
    cur.execute("select* from  inventariohonducorapp_tb_audit_mobiliario")
    rowA = cur.fetchall()
    cur.close()

    # DIBUJA LOS DATOS EN EL PDF

    linea = "________________________________________________________________________________________________________________________________________"
    p.drawString(20, 750,
                 "ID      FECHA                      TABLA                                                         ACCION                 USUARIO")

    p.drawString(20, contador, linea)
    for row in rowA:
        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[2] + "                                                      ")
        str4 = str(row[3])
        str5 = str(row[6])
        str6 = str(row[5])
        if str4 == "None":
            str4 = "NONE                                                                             "
        if str3 == "I" + "                                                      ":
            str3 = "INSERTAR"
        elif str3 == "U" + "                                                      ":
            str3 = "MODIFICAR"
        elif str3 == "D" + "                                                      ":
            str3 = "ELIMINAR"

        if str2 == "inventariohonducorapp_tb_mobiliario":
            str2 = " inventariohonducorapp_tb_mobiliario             "
        strlarge = str1 + " - " + str6 + "  - " + str2[:60] + "- " + str3 + "      - " + str5

        contador = contador - 20

        # DIBUJA LOS DATOS EN EL PDF

        p.drawString(20, contador, strlarge)
        p.drawString(20, contador - 6, linea)
        if contador <= 20:
            p.showPage()
            p.setFont('Vera', 8)
            p.drawString(20, contador, linea)

            contadorP = contadorP + 1
            p.drawString(550, 800, "Pag." + str(contadorP))
            contador = 740
            p.drawString(20, 740, linea)
            p.drawString(20, 750,
                         "ID      FECHA                      TABLA                                                         ACCION                 USUARIO")

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# =================================== PDF BITACORA VEHIUCLO
def PDF_Bitacora_Vehiculo(request):
    # DEFINE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # NOMBRE DEL ARCHIVO
    response['Content-Disposition'] = 'attachment; filename="bitacora_vehiculo.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 8)
    contadorP = 1
    p.drawString(550, 800, "Pag." + str(contadorP))

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(225, 790, "BITÁCORA DE VEHÍCULO")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    # ENCABEZADO


    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 740
    # TABLA QUE SE LLENA

    cur = connection.cursor()
    cur.execute("select* from  inventariohonducorapp_tb_audit_det_vehiculo")
    rowA = cur.fetchall()
    cur.close()

    # DIBUJA LOS DATOS EN EL PDF
    linea = "________________________________________________________________________________________________________________________________________"
    p.drawString(20, 750,
                 "ID      FECHA                      TABLA                                                         ACCION                 USUARIO")

    p.drawString(20, contador, linea)
    for row in rowA:
        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[2] + "                                                      ")
        str4 = str(row[3])
        str5 = str(row[6])
        str6 = str(row[5])
        if str4 == "None":
            str4 = "NONE                                                                             "
        if str3 == "I" + "                                                      ":
            str3 = "INSERTAR"
        elif str3 == "U" + "                                                      ":
            str3 = "MODIFICAR"
        elif str3 == "D" + "                                                      ":
            str3 = "ELIMINAR"

        if str2 == "inventariohonducorapp_tb_vehiculo":
            str2 = " inventariohonducorapp_tb_vehiculo                   "
            strlarge = str1 + " - " + str6 + "  - " + str2[:45] + " - " + str3 + "      - " + str5
        else:
            strlarge = str1 + " - " + str6 + "  - " + str2[:40] + " - " + str3 + "      - " + str5

        contador = contador - 20

        # DIBUJA LOS DATOS EN EL PDF
        p.drawString(20, contador, strlarge)
        p.drawString(20, contador - 6, linea)
        if contador <= 20:
            p.showPage()
            contadorP = contadorP + 1
            contador = 740
            p.setFont('Vera', 8)
            p.drawString(20, contador, linea)
            p.drawString(550, 800, "Pag." + str(contadorP))
            p.drawString(20, 750,
                         "ID      FECHA                      TABLA                                                         ACCION                 USUARIO")

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# =================================== PDF BITACORA INMUEBLE
def PDF_Bitacora_Inmueble(request):
    # DEFINE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # NOMBRE DEL ARCHIVO
    response['Content-Disposition'] = 'attachment; filename="bitacora_inmueble.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 8)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(225, 790, "BITACORA DE INMUEBLE")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    # ENCABEZADO


    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 740
    # TABLA QUE SE LLENA

    cur = connection.cursor()
    cur.execute("select* from  inventariohonducorapp_tb_audit_inmueble")
    rowA = cur.fetchall()
    cur.close()

    # DIBUJA LOS DATOS EN EL PDF

    linea = "________________________________________________________________________________________________________________________________________"
    p.drawString(20, 750,
                 "ID      FECHA                      TABLA                                          ACCION               USUARIO")

    p.drawString(20, contador, linea)
    for row in rowA:
        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[2])
        str4 = str(row[3])
        str5 = str(row[6])
        str6 = str(row[5])
        if str4 == "None":
            str4 = "NONE                                                                             "
        if str3 == "I":
            str3 = "INSERTAR"
        elif str3 == "U":
            str3 = "MODIFICAR"
        elif str3 == "D":
            str3 = "ELIMINAR"
        strlarge = str1 + " - " + str6[:5] + "  - " + str2[:60] + "      - " + str3 + "      - " + str5
        contador = contador - 20

        p.drawString(20, contador, strlarge)
        p.drawString(20, contador - 6, linea)
        if contador <= 20:
            p.showPage()
            contador = 740
            p.setFont('Vera', 8)
            p.drawString(20, contador, linea)

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# =================================== PDF BITACORA INICIO DE SESION
def PDF_Bitacora_Login(request):
    # DEFINE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # NOMBRE DEL ARCHIVO
    response['Content-Disposition'] = 'attachment; filename="bitacora_login.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 8)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(225, 790, "BITÁCORA DE INICIO DE SESIÓN")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    # ENCABEZADO

    contadorP = 1
    p.drawString(550, 800, "Pag." + str(contadorP))
    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 740
    # TABLA QUE SE LLENA

    cur = connection.cursor()
    cur.execute("select* from  inventariohonducorapp_tb_audit_login")
    rowA = cur.fetchall()
    cur.close()

    # DIBUJA LOS DATOS EN EL PDF
    linea = "________________________________________________________________________________________________________________________________________"
    p.drawString(20, 750,
                 "ID          ACCIÓN                      FECHA        USUARIO               ")

    p.drawString(20, contador, linea)
    for row in rowA:
        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[2])
        str4 = str(row[3])

        if str4 != "AnonymousUser":
            strlarge = str1 + " - " + str2 + "  - " + str3 + "      - " + str4
            if str2 == "CERRAR SESION":
                strlarge = str1 + " - " + str2[:20] + "  - " + str3 + "      - " + str4
            else:
                strlarge = str1 + " - " + str2[:20] + "      - " + str3 + "      - " + str4

            contador = contador - 20

            p.drawString(20, contador, strlarge)
            p.drawString(20, contador - 6, linea)

        if contador <= 20:
            p.showPage()
            contadorP = contadorP + 1
            p.setFont('Vera', 8)
            p.drawString(550, 800, "Pag." + str(contadorP))
            p.drawString(20, 750,
                         "ID          ACCIÓN                      FECHA        USUARIO               ")
            contador = 740

            p.drawString(20, contador, linea)

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# =============================================================================================================================
# PDF DE TODAS LAS ENTRADAS
def PDF_entradas(request):
    # DEFINE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # NOMBRE DEL ARCHIVO
    response['Content-Disposition'] = 'attachment; filename="entradas.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 10)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(200, 790, "REPORTE DE ENTRADAS REGISTRADAS")
    p.drawString(240, 780, "ALMACÉN HONDUCOR")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    # ENCABEZADO


    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 740
    # TABLA QUE SE LLENA

    cur = connection.cursor()
    cur.execute("select* from  inventariohonducorapp_tb_entrada order by id asc")
    rowA = cur.fetchall()
    cur.close()

    # DIBUJA LOS DATOS EN EL PDF
    articulos = tb_Articulo.objects.all()
    linea = "_______________________________________________________________________________________________________________"
    p.drawString(20, 750,
                 "ID      FECHA                      CÓDIGO DE BARRAS               CANTIDAD          ARTÍCULO      ")

    p.drawString(20, contador, linea)
    for row in rowA:
        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[3])
        str4 = str(row[2])
        str5 = row[5]
        str6 = str(row[4])
        for art in articulos:
            if art.id == str5:
                str1a = str1 + "       "
                str2a = str2 + "                                             "
                str3a = str3 + "                                                                           "
                str4a = str4 + "                                                                                      "
                str5a = art.nombre_art + "                                                                 "
                str6a = str6 + "                                                                 "

                strlarge = str1a[:5] + str2a[:30] + str3a[:35] + str4a[:30] + str5a[:30]
                contador = contador - 20
                p.drawString(20, contador, strlarge)
                p.drawString(20, contador - 6, linea)
                if contador <= 20:
                    p.showPage()
                    p.setFont('Vera', 10)
                    p.drawString(20, 750,
                                 "ID      FECHA                      CODIGO DE BARRAS               CANTIDAD          ARTICULO      ")

                    contador = 740
                    p.drawString(20, contador, linea)

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# PDF DE TODAS LAS SALIDAS
def PDF_entradas_fecha(request):
    # DEFINE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # DEFINE NOMBRE DEL ARCHIVO
    response['Content-Disposition'] = 'attachment; filename="entradas_fecha.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 10)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(200, 790, "REPORTE DE ENTRADAS REGISTRADAS")
    p.drawString(240, 780, "ALMACÉN HONDUCOR")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    # ENCABEZADO

    fecha_inicial = str(datetime.datetime.strptime(request.GET.get('starfecha'), "%m/%d/%Y"))
    fecha_final = str(datetime.datetime.strptime(request.GET.get('endfecha'), "%m/%d/%Y"))
    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 740
    # TABLA QUE SE LLENA
    # ABRIR BD
    cur = connection.cursor()
    cur.execute(
        "select* from  inventariohonducorapp_tb_entrada where fecha_registro_entrada  between '" + fecha_inicial + "' and '" + fecha_final + "' order by id asc")
    rowA = cur.fetchall()
    # CERRAR BD
    cur.close()
    # DATOS A USAR
    articulos = tb_Articulo.objects.all()
    # DIBUJA LOS DATOS EN EL PDF
    linea = "_____________________________________________________________________________________________________________"
    p.drawString(20, 750,
                 "ID      FECHA                      CÓDIGO DE BARRAS               CANTIDAD          ARTÍCULO      ")

    p.drawString(20, contador, linea)
    for row in rowA:
        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[3])
        str4 = str(row[2])
        str5 = row[5]
        str6 = str(row[4])
        for art in articulos:
            if art.id == str5:
                str1a = str1 + "       "
                str2a = str2 + "                                             "
                str3a = str3 + "                                                                           "
                str4a = str4 + "                                                                                      "
                str5a = art.nombre_art + "                                                                 "
                str6a = str6 + "                                                                 "

                strlarge = str1a[:5] + str2a[:30] + str3a[:35] + str4a[:30] + str5a[:30]
                contador = contador - 20
                p.drawString(20, contador, strlarge)
                p.drawString(20, contador - 6, linea)
                if contador <= 20:
                    p.showPage()
                    p.setFont('Vera', 10)
                    p.drawString(20, 750,
                                 "ID      FECHA                      CODIGO DE BARRAS               CANTIDAD          ARTICULO      ")

                    contador = 740
                    p.drawString(20, contador, linea)

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# ==============================================================================================================
# PDF DE TODAS LAS SALIDAS
def PDF_salidas(request):
    # DEFINE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # DEFINE EL NOMBRE DEL PDF
    response['Content-Disposition'] = 'attachment; filename="salidas.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # DEFINE FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 10)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(200, 790, "REPORTE DE SALIDAS REGISTRADAS")
    p.drawString(240, 780, "ALMACÉN HONDUCOR")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    # ENCABEZADO


    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 740
    # TABLA QUE SE LLENA
    # ABRIR BD
    cur = connection.cursor()
    cur.execute("select* from  inventariohonducorapp_tb_detalle_salida order by id asc")
    rowA = cur.fetchall()
    # CERRAR BD
    cur.close()

    # DATOS A USAR
    articulos = tb_Articulo.objects.all()
    detalle = tb_DetalleArticulo.objects.all()
    # DIBUJA LOS DATOS EN EL PDF
    linea = "______________________________________________________________________________________________________________"
    p.drawString(20, 750,
                 "ID      FECHA            CÓDIGO DE BARRAS        CANTIDAD          ARTÍCULO                        PARA")

    p.drawString(20, contador, linea)
    for row in rowA:
        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[3])
        str4 = str(row[2])
        str5 = row[8]
        str6 = str(row[7])
        for art in articulos:
            for det in detalle:
                if det.id == str5:
                    if art.id == det.cod_articulo_id:
                        str1a = str1 + "       "
                        str2a = str2 + "                                             "
                        str3a = str3 + "                                                                           "
                        str4a = str4 + "                                                                                      "
                        str5a = art.nombre_art + "                                                                 "
                        str6a = "      " + str6 + "                                                                 "

                        strlarge = str1a[:5] + str2a[:15] + str3a[:35] + str4a[:25] + str5a[:20] + str6a[:20]
                        contador = contador - 20
                        p.drawString(20, contador, strlarge)
                        p.drawString(20, contador - 6, linea)
                        if contador <= 20:
                            p.showPage()
                            p.setFont('Vera', 10)
                            p.drawString(20, 750,
                                         "ID      FECHA             CODIGO BARRAS        CANTIDAD          ARTICULO                        PARA")

                            contador = 740
                            p.drawString(20, contador, linea)

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# PDF DE TODAS LAS SALIDAS FECHAS
def PDF_salidas_fecha(request):
    # DEFINE EL TIPO DE ARCHIVO, EN ESTA CASO PDF
    response = HttpResponse(content_type='application/pdf')
    # DEFINE EL NOMBRE DEL PDF
    response['Content-Disposition'] = 'attachment; filename="salidas.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # DEFINE LAS FUENTES A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 10)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(200, 790, "REPORTE DE SALIDAS REGISTRADAS")
    p.drawString(240, 780, "ALMACÉN HONDUCOR")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    # ENCABEZADO
    fecha_inicial = str(datetime.datetime.strptime(request.GET.get('starfecha'), "%m/%d/%Y"))
    fecha_final = str(datetime.datetime.strptime(request.GET.get('endfecha'), "%m/%d/%Y"))

    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 740
    # TABLA QUE SE LLENA
    # ABRIR BD
    cur = connection.cursor()
    cur.execute(
        "select* from  inventariohonducorapp_tb_detalle_salida where fecha_registro_salida  between '" + fecha_inicial + "' and '" + fecha_final + "' order by id asc")
    rowA = cur.fetchall()
    # CERRAR BD
    cur.close()

    # DATOS A UTILIZAR
    articulos = tb_Articulo.objects.all()
    detalle = tb_DetalleArticulo.objects.all()
    # DIBUJA LOS DATOS EN EL PDF
    linea = "____________________________________________________________________________________________________________"
    p.drawString(20, 750,
                 "ID      FECHA            CÓDIGO DE BARRAS        CANTIDAD          ARTÍCULO                        PARA")

    p.drawString(20, contador, linea)
    for row in rowA:
        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[3])
        str4 = str(row[2])
        str5 = row[8]
        str6 = str(row[7])
        for art in articulos:
            for det in detalle:
                if det.id == str5:
                    if art.id == det.cod_articulo_id:
                        str1a = str1 + "       "
                        str2a = str2 + "                                             "
                        str3a = str3 + "                                                                           "
                        str4a = str4 + "                                                                                      "
                        str5a = art.nombre_art + "                                                                 "
                        str6a = "      " + str6 + "                                                                 "

                        strlarge = str1a[:5] + str2a[:15] + str3a[:35] + str4a[:25] + str5a[:20] + str6a[:20]
                        contador = contador - 20
                        p.drawString(20, contador, strlarge)
                        p.drawString(20, contador - 6, linea)
                        if contador <= 20:
                            p.showPage()
                            p.setFont('Vera', 10)
                            p.drawString(20, 750,
                                         "ID      FECHA             CODIGO BARRAS        CANTIDAD          ARTICULO                        PARA")

                            contador = 740
                            p.drawString(20, contador, linea)

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# PDF DE TOTAL DE EXISTENCIAS EN EL ALMACEN
# PDF DE TODAS LAS SALIDAS
def PDF_Total_Existencias(request):
    # DEFINE EL TIPO DE ARCHIVO A CREAR, EN ESTE CASO UN PDF
    response = HttpResponse(content_type='application/pdf')
    # DEFINE EL NOMBRE DEL PDF
    response['Content-Disposition'] = 'attachment; filename="total_existencias.pdf"'
    encabezados = ('        CODIGO', '      INVENTARIO', 'MARCA', 'MODELO', 'SERIE')
    # Creamos una lista de tuplas que van a contener a las personas
    # DEFINE EL TIPO DE FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 10)

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/honducorP.png'
    p.drawImage(archivo_imagen, 30, 770, 60, 45, preserveAspectRatio=True)
    # TITULO
    p.drawString(200, 790, "REPORTE DE VALOR EN EXISTENCIAS ")
    p.drawString(240, 775, "ALMACÉN HONDUCOR")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 790, fecha)
    # ENCABEZADO


    rows = tb_entrada.objects.values_list('id').order_by('id')
    contador = 700
    # TABLA QUE SE LLENA
    # ABRIR CONEXCION A BD
    cur = connection.cursor()
    cur.execute(
        "select a.id,a.nombre_art,a.existencia, sum(d.unidades*d.precio_unitario)from inventariohonducorapp_tb_detallearticulo d,inventariohonducorapp_tb_articulo a where d.cod_articulo_id=a.id group by a.nombre_art,a.id,a.existencia order by a.id")
    rowA = cur.fetchall()
    # CERRAR CONEXCION
    cur.close()

    articulos = tb_DetalleArticulo.objects.values('cod_articulo_id').annotate(
        total=Sum(F('unidades') * F('precio_unitario'), output_field=FloatField()))
    detalle = tb_DetalleArticulo.objects.all()
    linea = "_____________________________________________________________________________________________________________"
    p.drawString(20, 707,
                 "ID                            ARTÍCULO                                       EXISTENCIA                    VALOR LPS EN EXISTENCIA        ")

    p.drawString(20, contador, linea)
    super_contador = 0

    # DIBUJA LOS DATOS EN EL PDF
    for row in rowA:
        super_contador = super_contador + row[3]

        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[2])
        str4 = str(row[3])
        str1a = str1 + "              "
        str2a = "                                   " + str2
        str3a = "                                    " + "                                                       " + str3 + "                   "
        str4a = "                                    " + "                                                       " + "                                                       " + str4 + "                                        "

        strlarge = str1a[:10]
        contador = contador - 20
        p.drawString(20, contador, strlarge)
        p.drawString(20, contador, str2a[:65])
        p.drawString(20, contador, str3a[:160])
        p.drawString(20, contador, str4a[:260])

        p.drawString(20, contador - 6, linea)
        if contador <= 20:
            p.showPage()
            p.setFont('Vera', 10)
            p.drawString(20, 710,
                         "ID                            ARTÍCULO                                       EXISTENCIA                    VALOR LPS EN EXISTENCIA        ")

            contador = 700
            p.drawString(20, contador, linea)

    p.drawString(20, contador - 30, "TOTAL EN EXISTENCIAS LPS: " + str(super_contador))
    p.save()
    # REGRESA UN ARCHIVO PDF
    return response


# PDF DE MOBILIARIO ASIGNADO
def PDF_MobiliarioP(request):
    # CREAR EL TIPO DE ARCHIVO A ENVIAR, EN ESTE CASO PDF
    response = HttpResponse(content_type='application/pdf')
    # DEFINE EL NOMBRE DEL PDR
    response['Content-Disposition'] = 'attachment; filename="acta_mobiliario.pdf"'
    response['Content-Disposition'] = 'attachment; filename="acta_mobiliario.pdf"'

    # Creamos una lista de tuplas que van a contener a las personas
    # DEFINE EL TIPO DE FUENTE A USAR
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    p = canvas.Canvas(response)
    p2 = canvas.Canvas(response)
    p.setFont('Vera', 10)

    # IMAGEN DE PAPEL

    # IMAGEN DE PAPEL
    archivo_imagen = settings.MEDIA_ROOT + '/imagenes/encabezado_honducor.png'
    p.drawImage(archivo_imagen, 120, 770, 370, 65, preserveAspectRatio=True)
    # TITULO

    p.drawString(200, 740, "REPORTE DE MOBILIARIO ASIGNADO ")
    p.drawString(240, 730, "BIENES HONDUCOR")
    fecha = time.strftime('%d %b %y')
    # fecha que se genera
    p.drawString(450, 760, fecha)
    # ENCABEZADO
    p.drawString(60, 710,
                 "A continuación se detalla el mobiliario que se encuentra  en condicion de prestamo, asignado a")
    p.drawString(60, 700, request.GET.get('nombrem') + ', con número de identidad ' + request.GET.get('iden') + '.')

    rows = tb_CategoriaMobiliario.objects.all()
    contador = 640
    # TABLA QUE SE LLENA
    # ABRIR CONEXCION A BD
    cur = connection.cursor()
    cur.execute(
        "select m.id,mp.fecha_prestado,m.cod_inventario,m.marca,m.modelo,m.serie,m.cod_cat_mobiliario_id from  inventariohonducorapp_tb_mobiliario m,inventariohonducorapp_tb_mobiliarioprestado mp where m.id= mp.cod_mobiliario_id and mp.estado='ocupado' and mp.cod_empleado_id=" + request.GET.get(
            'pke'))
    rowA = cur.fetchall()
    # CERRAR CONEXCION A BD
    cur.close()

    articulos = tb_DetalleArticulo.objects.values('cod_articulo_id').annotate(
        total=Sum(F('unidades') * F('precio_unitario'), output_field=FloatField()))
    detalle = tb_DetalleArticulo.objects.all()
    linea = "_______________________________________________________________________________________________________________"
    p.drawString(20, 650,
                 "ID  FECHA PRESTAMO     COD INVENTARIO        MARCA             MODELO          SERIE                CATEGORÍA")

    p.drawString(20, contador, linea)
    super_contador = 0

    # DIBUJA LOS DATOS EN EL PDF
    for row in rowA:

        str1 = str(row[0])
        str2 = str(row[1])
        str3 = str(row[2])
        str4 = str(row[3])
        str5 = str(row[4])
        str6 = str(row[5])
        str7 = row[6]
        str7a = ""
        str1a = str1
        str2a = "       " + str2
        str3a = "                                        " + str3 + "                   "
        str4a = "                                    " + "                                     " + str4
        str5a = "                                    " + "                                                            " + str5
        str6a = "                                    " + "                                                                                 " + str6
        for row1 in rows:
            if row1.id == str7:
                str7a = "                                    " + "                                                                                                                " + row1.nombre_categoria

        strlarge = str1a[:3]
        contador = contador - 20
        p.drawString(20, contador, strlarge)
        p.drawString(20, contador, str2a[:65])
        p.drawString(20, contador, str3a[:160])
        p.drawString(20, contador, str4a[:260])
        p.drawString(20, contador, str5a[:360])
        p.drawString(20, contador, str6a[:340])
        p.drawString(20, contador, str7a[:560])

        p.drawString(20, contador - 6, linea)
        if contador <= 20:
            p.showPage()
            p.setFont('Vera', 10)
            p.drawString(20, 710,
                         "ID                            ARTICULO                                       EXISTENCIA                    VALOR LPS EN EXISTENCIA        ")

            contador = 640
            p.drawString(20, contador, linea)

    p.save()
    # REGRESA UN ARCHIVO PDF
    return response
