# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-19 16:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventariohonducorapp', '0042_tb_audit_inmueble'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tb_incidenciamobiliario',
            name='cod_empleado',
        ),
        migrations.RemoveField(
            model_name='tb_incidenciamobiliario',
            name='cod_mobiliario',
        ),
        migrations.RemoveField(
            model_name='tb_incidenciavehiculo',
            name='cod_empleado',
        ),
        migrations.RemoveField(
            model_name='tb_incidenciavehiculo',
            name='cod_vehiculo',
        ),
        migrations.DeleteModel(
            name='tb_incidenciaMobiliario',
        ),
        migrations.DeleteModel(
            name='tb_incidenciaVehiculo',
        ),
    ]
