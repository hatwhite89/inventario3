# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-09 14:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventariohonducorapp', '0024_tb_departamento_usuario_regis'),
    ]

    operations = [
        migrations.AddField(
            model_name='agencia',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_admin_inmueble',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_articulo',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_categoria_art',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_categoriamobiliario',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_incidenciaarticulo',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_incidenciamobiliario',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_incidenciavehiculo',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_inmueble',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_mobiliario',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_mobiliariodevuelto',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_mobiliarioprestado',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_municipio',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_vehiculo',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_vehiculoasignado',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tb_vehiculodescargado',
            name='usuario_regis',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
