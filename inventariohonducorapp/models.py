from django.conf import settings
from django.db import models

from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
"""
EN ESTA SECCION SE ENCUENTRAN TODOS LOS MODELOS DEL SISTEMA
LOS MODELOS SON QUIENES HACEN REPLICA Y CONEXCION CON LA BASE DE DATOS

"""

#Create your models here.

#======================= OFICINA O JEFATURA============================
#esta clase representa al modelo jefatura
class tb_Jefatura(models.Model):
    nombre_jefatura=models.CharField(max_length=40)

#esta funcion retorna el nombre de la jefatura
    def __str__(self):
     return self.nombre_jefatura

#============================== USUARIOS Y EMPLEADOS =================================
#modelo que hereda al modelo User que ya proporciona django


#esta clase representa al modelo empleado
class tb_Empleado(models.Model):

    primer_nombre = models.CharField(max_length=20)
    segundo_nombre = models.CharField(max_length=20,null=True, blank=True)
    primer_apellido = models.CharField(max_length=20,)
    segundo_apellido = models.CharField(max_length=20,null=True, blank=True)
    id_empleado = models.CharField(max_length=20)
    direccion = models.TextField(null=True, blank=True)
    tel1 = models.CharField(max_length=20 ,null=True, blank=True)
    tel2 = models.CharField(max_length=20, null=True, blank=True)
    celular = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    estado_emp=models.CharField(max_length=30, null=True,blank=True)

    foto = models.ImageField(upload_to='imagenes/')
    puesto = models.CharField(max_length=30, null=True, blank=True)



#esta funcion retorna el nombre completo de un empleado
    def __str__(self):
        return self.primer_nombre+" "+self.primer_apellido+" "+self.segundo_apellido


#===================== AGENGIAS ==========================

#clase modelo para la tabla tb_Departamento

class tb_Departamento(models.Model):
    nombre_depart=models.CharField(max_length=40)
    estado_dep=models.CharField(max_length=30,null=True,blank=True)
    usuario_regis= models.CharField(max_length=50, null=True, blank=True)

#esta funcion retorna el nombre del departamento
    def __str__(self):
      return self.nombre_depart

#modelo para la tabla municipio
class tb_Municipio(models.Model):
    nombre_municipio=models.CharField(max_length=50)
    cod_depart=models.ForeignKey(tb_Departamento)
    estado_muni=models.CharField(max_length=30,null=True,blank=True)
    usuario_regis = models.CharField(max_length=50, null=True, blank=True)
# esta funcion retorna el nombre del municipio
    def __str__(self):
      return self.nombre_municipio

#modelo para la tabla Agencia
class Agencia(models.Model):
    nombre_agencia=models.CharField(max_length=50)
    direccion=models.TextField(null=True, blank=True)
    telefono1=models.CharField(max_length=40,null=True, blank=True)
    telefono2=models.CharField(max_length=40,null=True, blank=True)
    telefono3=models.CharField(max_length=40,null=True, blank=True)
    imagen=models.FileField(upload_to='imagenes/',null=True, blank=True)
    estado_agencia=models.CharField(max_length=30,null=True,blank=True)
    tb_Municipio=models.ForeignKey(tb_Municipio)
    usuario_regis = models.CharField(max_length=50, null=True, blank=True)
# esta funcioon retorna el nombre de la agencia
    def __str__(self):
        return self.nombre_agencia
#========================== MOBILIARIO====================================================
#clase modelo para la tabla categoria mobiliario
class tb_CategoriaMobiliario(models.Model):
    nombre_categoria=models.CharField(max_length=40)
    descripccion=models.TextField()
    estado_cat_mobi=models.CharField(max_length=30,null=True,blank=True)
    usuario_regis = models.CharField(max_length=50, null=True, blank=True)

#esta funcion retorna el nombre de la categoria de un articulo
    def __str__(self):
      return self.nombre_categoria

#modelo para la tabla mobiliario
class tb_Mobiliario(models.Model):
    marca=models.CharField(max_length=40)
    modelo=models.CharField(max_length=40 ,null=True, blank=True)
    serie=models.CharField(max_length=40 ,null=True, blank=True)
    color=models.CharField(max_length=40 ,null=True, blank=True)
    estado=models.CharField(max_length=40 ,null=True, blank=True)
    cod_inventario=models.CharField(max_length=40)
    observacion=models.CharField(max_length=40 ,null=True, blank=True)
    costo_uni=models.FloatField(null=True, blank=True)
    descripccion=models.TextField(null=True, blank=True)
    anio_modelo=models.IntegerField(null=True, blank=True)
    cod_cat_mobiliario=models.ForeignKey(tb_CategoriaMobiliario)
    fecha_registro= models.DateField()
    imagen=models.ImageField(upload_to='imagenes/',null=True,blank=True)
    estado_mobiliario=models.CharField(max_length=30,null=True,blank=True)
    usuario_regis = models.CharField(max_length=50, null=True, blank=True)
    ubicacion_actual= models.CharField(max_length=50, null=True, blank=True)
#essta funcion retorna el codigo de inventario de un mobiliario
    def __str__(self):
         return self.cod_inventario

#modelo para la tabla tb_MobiliarioPrestado
class tb_MobiliarioPrestado(models.Model):
    fecha_prestado= models.DateField()
    estado=models.CharField(max_length=40,null=True, blank=True)
    descripccion=models.TextField(null=True, blank=True)
    cod_empleado= models.ForeignKey(tb_Empleado)
    cod_mobiliario=models.ForeignKey(tb_Mobiliario)
    gerencia=models.CharField(max_length=40,null=True, blank=True)
    departamento=models.CharField(max_length=50,null=True, blank=True)
    levanto_inventario=models.CharField(max_length=70,null=True, blank=True)
    telefono=models.CharField(max_length=20,null=True, blank=True)
    estado_mp=models.CharField(max_length=30,null=True,blank=True)
    usuario_regis = models.CharField(max_length=50, null=True, blank=True)
    #creo que faltan unos campos mas



#modelo para la tabla tb_MobiliarioDevuelto
class tb_MobiliarioDevuelto(models.Model):
    fecha_devolucion=models.DateField()
    estado=models.CharField(max_length=40)
    descripccion=models.TextField(null=True, blank=True)
    estado_md=models.CharField(max_length=30,null=True,blank=True)
    usuario_regis = models.CharField(max_length=50, null=True, blank=True)
    #llaves foraneas

    cod_empleado=models.ForeignKey(tb_Empleado)
    cod_mobiliario=models.ForeignKey(tb_Mobiliario)



#====================================== VEHICULOS =============================================
#esta clase representa al modelo vehiculo
class tb_Vehiculo(models.Model):
    marca=models.CharField(max_length=50,)
    modelo= models.CharField(max_length=50,null=True, blank=True)
    color=models.CharField(max_length=50,null=True, blank=True)
    serie=models.CharField(max_length=50,null=True, blank=True)
    serie_motor=models.CharField(max_length=50,null=True, blank=True)
    placa=models.CharField(max_length=50,null=True, blank=True)
    estado=models.CharField(max_length=50,null=True, blank=True)
    anio_modelo=models.CharField(max_length=50,null=True, blank=True)
    tipo_vehiculo=models.CharField(max_length=50)
    costo=models.FloatField(null=True, blank=True)
    descripccion=models.TextField(null=True, blank=True)
    observacion=models.TextField(null=True, blank=True)
    cod_inventario=models.CharField(max_length=50)
    imagen_vehi=models.FileField(upload_to='imagenes/',null=True, blank=True)
    estado_vehi=models.CharField(max_length=30,null=True,blank=True)
    usuario_regis= models.CharField(max_length=50, null=True, blank=True)
    agencia= models.CharField(max_length=50, null=True, blank=True)

#esta clase representa al modelo asignar vehiculo al empleado
class tb_VehiculoAsignado(models.Model):
    fecha_registro = models.DateField()
    estado = models.CharField(max_length=40)
    descripccion = models.TextField(null=True, blank=True)
    cod_empleado=models.ForeignKey(tb_Empleado)
    cod_vehiculo=models.ForeignKey(tb_Vehiculo)
    agencia=models.CharField(max_length=50)
    estado_vehi_asig=models.CharField(max_length=30,null=True,blank=True)
    usuario_regis= models.CharField(max_length=50, null=True, blank=True)

#esta clase representa al modelo descargar vehiculo al empleado
class tb_VehiculoDescargado(models.Model):
    fecha_devolucion= models.DateField(null=True, blank=True)
    estado=models.CharField(max_length=40, null=True, blank=True)
    descripccion= models.TextField(null=True, blank=True)
    cod_vehiculo=models.ForeignKey(tb_Vehiculo)
    cod_empleado=models.ForeignKey(tb_Empleado)
    estado_vehi_des=models.CharField(max_length=30,null=True,blank=True)
    usuario_regis= models.CharField(max_length=50, null=True, blank=True)


#======================= INMUEBLE =================================
# esta clase representa al modelo inmueble
class tb_Inmueble(models.Model):
    ubicacion=models.CharField(max_length=40,null=True, blank=True)
    destino_actual=models.CharField(max_length=70,null=True, blank=True)
    numero_instrumento =models.CharField(max_length=20,null=True, blank=True)
    fecha_otorgamiento =models.DateField(null=True, blank=True)
    notario_otorgante =models.CharField(max_length=80,null=True, blank=True)
    notario_otorgante = models.CharField(max_length=80, null=True, blank=True)
    otorgante = models.CharField(max_length=80, null=True, blank=True)
    valor_adq=models.FloatField(null=True, blank=True)
    forma_adquisicion = models.CharField(max_length=80,null=True, blank=True)
    fecha_acuerdo = models.DateField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    num_registro_propiedad = models.CharField(max_length=60,null=True, blank=True)
    folio_registro_propiedad =models.CharField(max_length=60,null=True, blank=True)
    tomo_registro_propiedad =models.CharField(max_length=60,null=True, blank=True)
    num_catastro=models.CharField(max_length=40,null=True, blank=True)
    estado_inmueble =models.CharField(max_length=30,null=True,blank=True)
    usuario_regis= models.CharField(max_length=50, null=True, blank=True)
    estado= models.CharField(max_length=50, null=True, blank=True)
    ciudad= models.CharField(max_length=50, null=True, blank=True)


    def __str__(self):
     return self.id


#esta clase representa al adminsitrador del inmuble
class tb_Admin_Inmueble(models.Model):
    estado=models.CharField(max_length=50, null=True, blank=True)
    fecha_registro=models.DateField(null=True, blank=True)
    cod_empleado=models.ForeignKey(tb_Empleado)
    cod_inmueble=models.ForeignKey(tb_Inmueble)
    estado_admin_inmueble=models.CharField(max_length=30,null=True,blank=True)
    usuario_regis= models.CharField(max_length=50, null=True, blank=True)
    descripcion=models.TextField(null=True,blank=True)


#ALV para descargar el inmueble

class tb_InmuebleDescargado(models.Model):
    fecha_devolucion= models.DateField(null=True, blank=True)
    estado=models.CharField(max_length=40, null=True, blank=True)
    descripccion= models.TextField(null=True, blank=True)
    cod_inmueble=models.ForeignKey(tb_Inmueble)
    cod_empleado=models.ForeignKey(tb_Empleado)
    estado_inmueble_des=models.CharField(max_length=30, null=True,blank=True)
    usuario_regis= models.CharField(max_length=50, null=True, blank=True)


#=============================== Articulos / Suministros ======================================
#esta clase representa al modelo categoria de articulo
class tb_categoria_art(models.Model):
    nombre_cat=models.CharField(max_length=40)
    descripcion=models.TextField()
    estado_cat_art=models.CharField(max_length=30, null=True,blank=True)
    usuario_regis = models.CharField(max_length=50, null=True, blank=True)

#esta funcion retorna el nombre de la catecoria del articulo
    def __str__(self):
        return self.nombre_cat

#esta clase representa al modelo articulo
class tb_Articulo(models.Model):
    nombre_art= models.CharField(max_length=50)
    descrip=models.TextField(null=True, blank=True)
    imagen_art=models.FileField(upload_to='imagenes/', null=True, blank=True)
    existencia=models.IntegerField(null=True, blank=True)
    cod_categoria=models.ForeignKey(tb_categoria_art)
    estado_articulo=models.CharField(max_length=30, null=True,blank=True)
    usuario_regis = models.CharField(max_length=50, null=True, blank=True)

#retorna el nombre del articulo
    def __str__(self):
        return self.nombre_art

# esta clase representa al modelo detalle de articulos
class tb_DetalleArticulo(models.Model):
    valor = models.CharField(max_length=50, null=True, blank=True)
    codigo_barras = models.CharField(max_length=20, null=True, blank=True)
    numero_referencia=models.CharField(max_length=50, null=True, blank=True)
    precio_unitario = models.FloatField(null=True, blank=True)
    garantia = models.CharField(max_length=60, null=True, blank=True)
    especificaciones = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=30, null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    fecha_compra = models.DateField(null=True, blank=True)
    unidades = models.IntegerField(null=True, blank=True)
    nivel = models.CharField(max_length=50, null=True, blank=True)
    estante = models.CharField(max_length=50, null=True, blank=True)
    cod_articulo = models.ForeignKey(tb_Articulo)
    usuario_regis = models.CharField(max_length=20, null=True, blank=True)
    estado_det_art=models.CharField(max_length=30, null=True,blank=True)


    def __int__(self):
          return self.codigo_barras

# esta clase representa al modelo incidencias de articulos
class tb_incidenciaArticulo(models.Model):
    tipo = models.CharField(max_length=50, null=True, blank=True)
    descripccion_inc = models.TextField(null=True, blank=True)
    fecha_registro_inc= models.DateField(null=True, blank=True)
    cod_det_art=models.ForeignKey(tb_DetalleArticulo,null=True, blank=True)
    estado_inc_art=models.CharField(max_length=30, null=True, blank=True)
    usuario_regis= models.CharField(max_length=50, null=True, blank=True)


#esta clase representa al modelo entradas
class tb_entrada(models.Model):
    fecha_registro_entrada=models.DateField(null=True, blank=True)
    cantidad=models.IntegerField(null=True, blank=True)
    codigo_barras=models.CharField(max_length=20, null=True, blank=True)
    cod_art=models.ForeignKey(tb_Articulo)
    usuario_regis=models.CharField(max_length=20, null=True, blank=True)
    estado_entrada=models.CharField(max_length=30, null=True, blank=True)



# esta clase representa al modelo salidas
class tb_salida(models.Model):
    fecha_registro_salida = models.DateField(null=True, blank=True)
    usuario_regis = models.CharField(max_length=20,null=True, blank=True)


#clase detalle salida

class tb_detalle_salida(models.Model):
    fecha_registro_salida = models.DateField(null=True, blank=True)
    cantidad = models.IntegerField(null=True, blank=True)
    codigo_barras = models.CharField(max_length=20, null=True, blank=True)
    cod_det_art = models.ForeignKey(tb_DetalleArticulo)
    usuario_regis = models.CharField(max_length=20, )
    personal_entregado = models.CharField(max_length=60, null=True, blank=True)
    usuario_regis = models.CharField(max_length=20, null=True, blank=True)
    departamento = models.CharField(max_length=20, null=True, blank=True)
    agencia = models.CharField(max_length=20, null=True, blank=True)
    estado_salida = models.CharField(max_length=30, null=True, blank=True)
    cod_salida=models.ForeignKey(tb_salida)


#======================================= combobox ==========================================================

class tb_estado(models.Model):
      nombre_estado=models.CharField(max_length=20,null=True, blank=True)
      descripcion= models.TextField(null=True, blank=True)

      def __int__(self):
          return self.nombre_estado

class tb_clasificacion_estados(models.Model):
    nombre_estado = models.CharField(max_length=20, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)

    def __int__(self):
        return self.nombre_estado
#=====================================================================================================================
#======================================== PROVEEDORES ===============================================================




class tb_proveedor(models.Model):
    nombre_empresa=models.CharField(max_length=50)
    rtn=models.CharField(max_length=50,null=True, blank=True)
    razon_social=models.CharField(max_length=50,null=True, blank=True)
    representante_legal=models.CharField(max_length=60,null=True, blank=True)
    ciudad=models.CharField(max_length=30)
    telefono1=models.CharField(max_length=20,null=True, blank=True)
    telefono2=models.CharField(max_length=20,null=True, blank=True)
    email=models.EmailField(null=True,blank=True)
    pais=models.CharField(max_length=40)
    personal_contacto=models.CharField(max_length=60,null=True, blank=True)
    sitio_web=models.CharField(max_length=50,null=True, blank=True)
    direccion= models.TextField(null=True, blank=True)


#============================================ BITACORAS DE AUDITORIA =================================================


class tb_audit_det_articulo(models.Model):

    TableName=models.CharField(max_length=45)
    Operation=models.CharField(max_length=1)
    OldValue=models.TextField( null=True, blank=True)
    NewValue=models.TextField( null=True, blank=True)
    UpdateDate=models.DateField()
    UserName=models.CharField(max_length=45)

class tb_audit_mobiliario(models.Model):

    TableName=models.CharField(max_length=45)
    Operation=models.CharField(max_length=1)
    OldValue=models.TextField( null=True, blank=True)
    NewValue=models.TextField( null=True, blank=True)
    UpdateDate=models.DateField()
    UserName=models.CharField(max_length=45)

class tb_audit_det_vehiculo(models.Model):

    TableName=models.CharField(max_length=45)
    Operation=models.CharField(max_length=1)
    OldValue=models.TextField( null=True, blank=True)
    NewValue=models.TextField( null=True, blank=True)
    UpdateDate=models.DateField()
    UserName=models.CharField(max_length=45)

class tb_audit_inmueble(models.Model):

    TableName=models.CharField(max_length=45)
    Operation=models.CharField(max_length=1)
    OldValue=models.TextField( null=True, blank=True)
    NewValue=models.TextField( null=True, blank=True)
    UpdateDate=models.DateField()
    UserName=models.CharField(max_length=45)

class tb_audit_entrada(models.Model):

    TableName=models.CharField(max_length=45)
    Operation=models.CharField(max_length=1)
    OldValue=models.TextField( null=True, blank=True)
    NewValue=models.TextField( null=True, blank=True)
    UpdateDate=models.DateField()
    UserName=models.CharField(max_length=45)

class tb_audit_salida(models.Model):

    TableName=models.CharField(max_length=45)
    Operation=models.CharField(max_length=1)
    OldValue=models.TextField( null=True, blank=True)
    NewValue=models.TextField( null=True, blank=True)
    UpdateDate=models.DateField()
    UserName=models.CharField(max_length=45)

class tb_audit_login(models.Model):

    Operation=models.CharField(max_length=1)
    UpdateDate=models.DateField()
    UserName=models.CharField(max_length=45)