# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-02 23:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventariohonducorapp', '0013_auto_20170602_1704'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tb_vehiculoasignado',
            old_name='fecha_devolucion',
            new_name='fecha_registro',
        ),
        migrations.RemoveField(
            model_name='tb_vehiculoasignado',
            name='imagen',
        ),
    ]