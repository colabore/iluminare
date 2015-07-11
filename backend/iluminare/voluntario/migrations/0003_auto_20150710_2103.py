# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voluntario', '0002_auto_20150128_2315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voluntario',
            name='tipo',
            field=models.CharField(max_length=1, choices=[(b'T', b'Trabalhador'), (b'A', b'Apoio')]),
            preserve_default=True,
        ),
    ]
