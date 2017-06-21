#=================================== EXCEL DE ENTRADAS =========================================
import xlwt
from django.http import HttpResponse
import dateutil.parser
from inventariohonducorapp.models import tb_entrada, tb_salida, tb_Articulo,tb_Vehiculo,tb_DetalleArticulo,tb_Mobiliario,tb_CategoriaMobiliario,tb_audit_det_articulo,tb_audit_salida,tb_audit_entrada,tb_audit_mobiliario,tb_audit_det_vehiculo,tb_Inmueble,tb_detalle_salida,tb_audit_login
import datetime
#====================================== EXCEL PARA ENTRADAS
def export_entrada_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="entradas.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('entrada')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODIGO ENTRADA', 'FECHA DE REGISTRO', 'CANTIDAD', 'CODIGO DE BARRAS','CODIGO DE ARTICULO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    codigo=tb_Articulo.objects.values_list('id','nombre_art')
    rows = tb_entrada.objects.values_list('id','fecha_registro_entrada','cantidad','codigo_barras',"cod_art")
    for row in rows:
        row_num += 1


        for col_num in range(len(row)):

            if col_num==4:
                for codi in codigo:
                    if codi[0]== row[col_num]:
                     ws.write(row_num, col_num, codi[1], font_style)
            else:
             ws.write(row_num, col_num, row[col_num], font_style)


    wb.save(response)
    return response

#====================================== EXCEL PARA SALIDAS

def export_salida_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="salidas.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('salida')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODIGO SALIDA', 'FECHA DE REGISTRO', 'CANTIDAD', 'CODIGO DE BARRAS','PERSONAL ENTREGADO','USUARIO QUE REGISTRO ENTRADA']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()


    rows = tb_detalle_salida.objects.values_list('id','fecha_registro_salida','cantidad','codigo_barras',"personal_entregado","usuario_regis")
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

#====================================== EXCEL PARA ARTICULOS

def export_articulo_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="articulos.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('articulo')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODIGO ARTICULO', 'NOMBRE DEL ARTICULO', 'DESCRIPCCION', 'EXISTENCIA']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()


    rows = tb_Articulo.objects.values_list('id','nombre_art','descrip','existencia').order_by("id")
    #rows es el array de objetos del modelo
    #row es la instancia de rows
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):

            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

#====================================== EXCEL PARA VEHICULOS

def export_vehiculo_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="vehiculos.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('vehiculo')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODIGO DE VEHICULO', 'CODIGO DE INVENTARIO', 'MARCA', 'MODELO','PLACA','SERIE CHASIS','SERIE MOTOR','TIPO DE VEHICULO','COSTO UNITARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()


    rows = tb_Vehiculo.objects.values_list('id','cod_inventario','marca','modelo','placa','serie','serie_motor','tipo_vehiculo','costo').order_by("id")
    #rows es el array de objetos del modelo
    #row es la instancia de rows
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):

            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response
#====================================================== EXCEL PARA INMUEBLES


def export_inmueble_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="inmueble.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('inmueble')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODIGO DE INMUEBLE', 'UBICACION', 'DESTINO ACTUAL', 'NUMERO DE INSTRUMENTO','FECHA OTORGAMIENTO','NOTARIO OTORGANTE','VALOR DE AQUISICION','FORMA DE ADQUISICION','FECHA ACUERDO','OBSERVACIONES','NUMERO DE REGISTRO DE LA PROPIEDAD','FOLIO REGISTRO DE LA PROPIEDAD','TOMO REGISTRO DE LA PROPIEDAD','NUMERO DE CATASTRO','OTORGANTE','CIUDAD']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()


    rows = tb_Inmueble.objects.values_list('id','ubicacion','destino_actual','numero_instrumento','fecha_otorgamiento','notario_otorgante','valor_adq','forma_adquisicion','fecha_acuerdo','observaciones','num_registro_propiedad','folio_registro_propiedad','tomo_registro_propiedad','num_catastro','otorgante','ciudad').order_by("id")
    #rows es el array de objetos del modelo
    #row es la instancia de rows
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):

            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response
#========================================================== EXCEL ENTRADAS FECHAS
def export_entrada_fechas_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="entradas.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('entrada')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODIGO ENTRADA', 'FECHA DE REGISTRO',  'CODIGO DE BARRAS','ARTICULO','CANTIDAD','USUARIO QUE REGISTRO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    fecha_inicial = datetime.datetime.strptime(request.GET.get('starfecha'), "%m/%d/%Y")
    fecha_final = datetime.datetime.strptime(request.GET.get('endfecha'), "%m/%d/%Y")
    codigo=tb_Articulo.objects.values_list('id','nombre_art')
    rows = tb_entrada.objects.values_list('id','fecha_registro_entrada','codigo_barras',"cod_art",'cantidad','usuario_regis').filter(fecha_registro_entrada__range=(fecha_inicial,fecha_final))
    for row in rows:
        row_num += 1


        for col_num in range(len(row)):

            if col_num==3:
                for codi in codigo:
                    if codi[0]== row[col_num]:
                     ws.write(row_num, col_num, codi[1], font_style)
            else:
             ws.write(row_num, col_num, row[col_num], font_style)


    wb.save(response)
    return response

#========================================================== EXCEL SALIDAS FECHAS
def export_salida_fecha_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="salidas.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('salida')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True


    columns = ['CODIGO SALIDA', 'FECHA DE REGISTRO', 'CANTIDAD','ARTICULO', 'CODIGO DE BARRAS','PERSONAL ENTREGADO','USUARIO QUE REGISTRO ENTRADA']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)


    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    fecha_inicial = datetime.datetime.strptime(request.GET.get('starfecha'), "%m/%d/%Y")
    fecha_final = datetime.datetime.strptime(request.GET.get('endfecha'), "%m/%d/%Y")

    entra= tb_DetalleArticulo.objects.values_list('id','cod_articulo')
    arti = tb_Articulo.objects.values_list('id', 'nombre_art')
    rows = tb_detalle_salida.objects.values_list('id','fecha_registro_salida','cantidad',"cod_det_art","codigo_barras","personal_entregado","usuario_regis").filter(fecha_registro_salida__range=(fecha_inicial,fecha_final))
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            if col_num == 3:
               for ent in entra:

                   if ent[0] == row[col_num]:
                      for articulo in arti:
                         if articulo[0] == ent[1]:
                           ws.write(row_num, col_num, articulo[1], font_style)
            else:
              ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

#================================ EXCEL AGENCIAS MOBILIARIO

def export_mobiliario_agencia_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="inventario_agencias_detalle.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('inventario_agencias_detalle')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['CODIGO MOBILIARIO', 'CATEGORIA','NUMERO DE INVENTARIO', 'MARCA', 'MODELO','SERIE','COSTO UNITARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    cat_m=tb_CategoriaMobiliario.objects.values_list('id','nombre_categoria')
    rows = tb_Mobiliario.objects.values_list('id','cod_cat_mobiliario','cod_inventario','marca','modelo','serie','costo_uni').filter(ubicacion_actual=request.GET.get('noma'))
    #rows es el array de objetos del modelo
    #row es la instancia de rows
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):

            if col_num == 1:

              for categoria in cat_m:

                if categoria[0]==row[col_num]:

                    ws.write(row_num, col_num, categoria[1], font_style)
            else:
                ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


#================================================= BITACORAS =======================================

#detalle entrada
def export_bitacora_detalle_art_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bitacora_detalle_entrada.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('bitacora_detalle_entrada')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'TABLA','OPERACION', 'VALOR ANTERIOR', 'VALOR NUEVO','FECHA','USUARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()


    rows = tb_audit_det_articulo.objects.values_list('id','TableName','Operation','OldValue','NewValue','UpdateDate','UserName')
    #rows es el array de objetos del modelo
    #row es la instancia de rows
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

# ================================ BITACORAS DE MOBILIARIO =================================================

def export_bitacora_mobiliario_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bitacora_mobiliario.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('bitacora_mobiliario')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'TABLA','OPERACION', 'VALOR ANTERIOR', 'VALOR NUEVO','FECHA','USUARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()


    rows = tb_audit_mobiliario.objects.values_list('id','TableName','Operation','OldValue','NewValue','UpdateDate','UserName')
    #rows es el array de objetos del modelo
    #row es la instancia de rows
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


# ================================ BITACORAS DE VEHICULOS=================================================
def export_bitacora_vehiculo_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bitacora_vehiculo.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('bitacora_vehiculo')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'TABLA','OPERACION', 'VALOR ANTERIOR', 'VALOR NUEVO','FECHA','USUARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()


    rows = tb_audit_det_vehiculo.objects.values_list('id','TableName','Operation','OldValue','NewValue','UpdateDate','UserName')
    #rows es el array de objetos del modelo
    #row es la instancia de rows
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


# ================================ BITACORAS DE ENTRADA =================================================
def export_bitacora_entrada_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bitacora_entrada.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('bitacora_entrada')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'TABLA','OPERACION', 'VALOR ANTERIOR', 'VALOR NUEVO','FECHA','USUARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()


    rows = tb_audit_entrada.objects.values_list('id','TableName','Operation','OldValue','NewValue','UpdateDate','UserName')
    #rows es el array de objetos del modelo
    #row es la instancia de rows
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


# ================================ BITACORAS DE SALIDA=================================================
def export_bitacora_salida_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bitacora_salida.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('bitacora_salida')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'TABLA','OPERACION', 'VALOR ANTERIOR', 'VALOR NUEVO','FECHA','USUARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()


    rows = tb_audit_salida.objects.values_list('id','TableName','Operation','OldValue','NewValue','UpdateDate','UserName')
    #rows es el array de objetos del modelo
    #row es la instancia de rows
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

#============================================= BITACORA MOBILIARIO FECHAS
def export_bitacora_mobiliario_fecha_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bitacora_mobiiario.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('bitacora_mobiliario')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'TABLA', 'OPERACION', 'VALOR ANTERIOR', 'VALOR NUEVO', 'FECHA', 'USUARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)


    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    fecha_inicial = datetime.datetime.strptime(request.GET.get('starfecha'), "%m/%d/%Y")
    fecha_final = datetime.datetime.strptime(request.GET.get('endfecha'), "%m/%d/%Y")


    rows = tb_audit_mobiliario.objects.values_list('id','TableName','Operation','OldValue','NewValue','UpdateDate','UserName').filter(UpdateDate__range=(fecha_inicial,fecha_final))
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):

              ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

#========================================================= EXCEL BITACORA VEHICULO FECHA=============================

def export_bitacora_vehiculo_fecha_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bitacora_vehiculo.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('bitacora_vehiculo')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'TABLA', 'OPERACION', 'VALOR ANTERIOR', 'VALOR NUEVO', 'FECHA', 'USUARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)


    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    fecha_inicial = datetime.datetime.strptime(request.GET.get('starfecha'), "%m/%d/%Y")
    fecha_final = datetime.datetime.strptime(request.GET.get('endfecha'), "%m/%d/%Y")


    rows = tb_audit_det_vehiculo.objects.values_list('id','TableName','Operation','OldValue','NewValue','UpdateDate','UserName').filter(UpdateDate__range=(fecha_inicial,fecha_final))
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):

              ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


#========================== EXCEL PARA ENTRADAS AL ALMACEN ==============================================


def export_bitacora_entrada_fecha_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bitacora_entrada.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('bitacora_entrada')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'TABLA', 'OPERACION', 'VALOR ANTERIOR', 'VALOR NUEVO', 'FECHA', 'USUARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)


    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    fecha_inicial = datetime.datetime.strptime(request.GET.get('starfecha'), "%m/%d/%Y")
    fecha_final = datetime.datetime.strptime(request.GET.get('endfecha'), "%m/%d/%Y")


    rows = tb_audit_entrada.objects.values_list('id','TableName','Operation','OldValue','NewValue','UpdateDate','UserName').filter(UpdateDate__range=(fecha_inicial,fecha_final))
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):

              ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

#==================================== BITACORA EXCEL SALIDA ==========================================================
def export_bitacora_salida_fecha_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bitacora_salida.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('bitacora_salida')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'TABLA', 'OPERACION', 'VALOR ANTERIOR', 'VALOR NUEVO', 'FECHA', 'USUARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)


    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    fecha_inicial = datetime.datetime.strptime(request.GET.get('starfecha'), "%m/%d/%Y")
    fecha_final = datetime.datetime.strptime(request.GET.get('endfecha'), "%m/%d/%Y")


    rows = tb_audit_salida.objects.values_list('id','TableName','Operation','OldValue','NewValue','UpdateDate','UserName').filter(UpdateDate__range=(fecha_inicial,fecha_final))
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):

              ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

#=================================================================================EXCEL BITACORA INICIO DE SESION
def export_bitacora_login_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bitacora_login.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('bitacora_login')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID','OPERACION','FECHA','USUARIO']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()


    rows = tb_audit_login.objects.values_list('id','Operation','UpdateDate','UserName')
    #rows es el array de objetos del modelo
    #row es la instancia de rows
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            if row[3]!="AnonymousUser":
                ws.write(row_num, col_num, row[col_num], font_style)



    wb.save(response)
    return response