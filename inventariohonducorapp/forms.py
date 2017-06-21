from datetime import time

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import ModelForm, ClearableFileInput, FileInput, TextInput

from inventariohonducorapp.models import tb_Articulo, tb_categoria_art, tb_CategoriaMobiliario, tb_DetalleArticulo, \
    tb_MobiliarioPrestado, Agencia, tb_Jefatura, tb_salida,tb_MobiliarioDevuelto,tb_Empleado,tb_Mobiliario,tb_incidenciaArticulo,tb_Departamento,tb_proveedor

class Tb_ProveedorForm(ModelForm):
    class Meta:
        model = tb_proveedor
        fields = '__all__'
        widgets = {
            'pais': TextInput(attrs={"class": "gui-input"}), 'email': TextInput(attrs={"class": "gui-input"}),
            'nombre_empresa': TextInput(attrs={"class": "gui-input"}),
            'rtn': TextInput(attrs={"class": "gui-input"}),
            'razon_social': TextInput(attrs={"class": "gui-input"}),
            'representante_legal': TextInput(attrs={"class": "gui-input"}),
            'ciudad': TextInput(attrs={"class": "gui-input"}),
            'telefono1': TextInput(attrs={"class": "gui-input"}),
            'telefono2': TextInput(attrs={"class": "gui-input"}),
            'sitio_web': TextInput(attrs={"class": "gui-input"}),
            'personal_contacto': TextInput(attrs={"class": "gui-input"}),
            'direccion': TextInput(attrs={"class": "gui-input"}),
        }


class Tb_EmpleadoForm(forms.Form):
    nombre = forms.CharField(max_length=40)
    direccion = forms.CharField(widget=forms.Textarea)


class Tb_ArticuloForm(forms.Form):
    # no es necesario agregar todos los campos
    # imagen_art = forms.FileField(label='seleccion un archivo')

    cod_categoria = forms.CharField(label="CATEGORIA", widget=forms.Select(attrs={"class": "gui-input"},
        choices=tb_categoria_art.objects.all().values_list('id', 'nombre_cat')))


# activo
class Tb_DetalleArtForm(forms.Form):

    def query_static(self):
        return 1

class Tb_NuevoVehiculo(forms.Form):

    def query_static(self):
        return 1

class Tb_NuevoVehiculoAsignado(forms.Form):
    def query_static(self):
        return 1

class Tb_ArticuloForm2(ModelForm):
    class Meta:
        model = tb_Articulo
        fields = '__all__'

class Tb_IncidenciaArticulo(ModelForm):
    class Meta:
        model = tb_incidenciaArticulo
        fields = '__all__'

class Tb_MobiliarioForm(forms.Form):
    cod_cat_mobiliario_id = forms.CharField(label="CATEGORIA MOBILIARIO", widget=forms.Select(attrs={"class": "gui-input"},
        choices=tb_CategoriaMobiliario.objects.all().values_list('id', 'nombre_categoria')))


class Tb_MobiliarioPrestadoForm(forms.Form):
    #este valor carca el select en el html, retornando el nombre del empleando y devolviendo el codigo de empleado
    cod_empleado= forms.CharField(widget=forms.Select(attrs={"class": "gui-input"},choices=[ ( p.id, '{0} {1} {2} {3}'.format( p.primer_nombre,p.segundo_nombre, p.primer_apellido,p.segundo_apellido ),) for p in tb_Empleado.objects.all() ]))


    departamento = forms.CharField(label="DEPARTAMENTO/OFICINA", widget=forms.Select(attrs={"class": "gui-input"},
                                                                                     choices=tb_Jefatura.objects.all().values_list(
                                                                                         'nombre_jefatura',
                                                                                         'nombre_jefatura')))

    gerencia = forms.CharField(label="AGENCIA", widget=forms.Select(attrs={"class": "gui-input"},
                                                                    choices=Agencia.objects.all().values_list(
                                                                        'nombre_agencia', 'nombre_agencia')))

    cod_mobiliario= forms.CharField(label="CODIGO DE INVENTARIO", widget=forms.Select(attrs={"class": "gui-input"},
                                                                    choices=tb_Mobiliario.objects.values_list(
                                                                        'id', 'cod_inventario')))


class Tb_SalidaForm(forms.Form):
    departamento = forms.CharField(label="DEPARTAMENTO/OFICINA", widget=forms.Select(attrs={"class": "gui-input"},
                                                                                     choices=tb_Jefatura.objects.all().values_list(
                                                                                         'id',
                                                                                         'nombre_jefatura')))

    agencia = forms.CharField(label="AGENCIA", widget=forms.Select(attrs={"class": "gui-input"},
                                                                   choices=Agencia.objects.all().values_list(
                                                                       'id', 'nombre_agencia')))

class Tb_DescargarMobiliarioForm(forms.Form):
    cod_mobiliario = forms.CharField(label="CODIGO DE INVENTARIO", widget=forms.Select(attrs={"class": "gui-input"},
                                                                                       choices=tb_Mobiliario.objects.values_list(
                                                                                           'id', 'cod_inventario')))

    # este valor carca el select en el html, retornando el nombre del empleando y devolviendo el codigo de empleado
    cod_empleado = forms.CharField(label="EMPLEADO",widget=forms.Select(attrs={"class": "gui-input"}, choices=[
        (p.id, '{0} {1} {2} {3}'.format(p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido),) for
        p in tb_Empleado.objects.all()]))


class Tb_DescargarVehiculoForm(forms.Form):

    def query_static(self):
        return 1


class Tb_NuevoInmuebleForm(forms.Form):

    destino_actual = forms.CharField(label="DEPARTAMENTO", widget=forms.Select(attrs={"class": "gui-input"},
                                                                   choices=tb_Departamento.objects.all().values_list(
                                                                        'nombre_depart','nombre_depart')))
class Tb_AsignarInmuebleForm(forms.Form):

     def query_static(self):
        return 1

class Tb_NuevoDetalleSalida(forms.Form):




    codigo = tb_salida.objects.count()+1
    departamento = forms.CharField(label="DEPARTAMENTO/OFICINA", widget=forms.Select(attrs={"class": "gui-input"},
                                                                                     choices=tb_Jefatura.objects.all().values_list(
                                                                                         'nombre_jefatura',
                                                                                         'nombre_jefatura')))

    agencia = forms.CharField(label="AGENCIA", widget=forms.Select(attrs={"class": "gui-input"},
                                                                   choices=Agencia.objects.all().values_list(
                                                                       'nombre_agencia', 'nombre_agencia')))

class Tb_nuevoDetalleSalida2(forms.Form):
    def query_static(self):
        return 1



class Tb_ModificarArticulo(forms.Form):
    cod_categoria = forms.CharField(label="CATEGORIA", widget=forms.Select(attrs={"class": "gui-input"},
                                                                           choices=tb_categoria_art.objects.all().values_list(
                                                                               'id', 'nombre_cat')))
class Tb_ModificarMobiliario(forms.Form):
    cod_cat_mobiliario_id = forms.CharField(label="CATEGORIA MOBILIARIO",
                                            widget=forms.Select(attrs={"class": "gui-input"},
                                                                choices=tb_CategoriaMobiliario.objects.all().values_list(
                                                                    'id', 'nombre_categoria')))

class Tb_ModificarVehiculo(forms.Form):
    def query_static(self):
        return 1

class Tb_ModificarInmueble(forms.Form):
    def query_static(self):
        return 1

class Tb_DescargarInmueble(forms.Form):
    def query_static(self):
        return 1