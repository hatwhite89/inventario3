# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-06 21:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventariohonducorapp', '0017_tb_vehiculoasignado'),
    ]

    operations = [
        migrations.AddField(
            model_name='tb_inmueble',
            name='otorgante',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
    ]
