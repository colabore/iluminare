# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voluntario', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voluntario',
            name='ativo',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
