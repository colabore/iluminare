# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paciente', '0001_initial'),
        ('tratamento', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgendaTrabalho',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.DateField()),
                ('hora_chegada', models.TimeField(null=True, blank=True)),
                ('hora_saida', models.TimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Funcao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descricao', models.TextField()),
                ('tratamento', models.ForeignKey(blank=True, to='tratamento.Tratamento', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FuncaoVoluntario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('funcao', models.ForeignKey(to='voluntario.Funcao')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trabalho',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(blank=True, max_length=2, null=True, choices=[(b'PR', b'Presente'), (b'FA', b'Falta'), (b'FV', b'Falta por Viagem'), (b'FT', b'Falta por Trabalho'), (b'FL', b'Falta por Licen\xc3\xa7a'), (b'FS', b'Falta por Sa\xc3\xbade'), (b'NA', b'N\xc3\xa3o se Aplica'), (b'NI', b'N\xc3\xa3o Informado')])),
                ('data', models.DateField()),
                ('hora_inicio', models.TimeField(null=True, blank=True)),
                ('hora_final', models.TimeField(null=True, blank=True)),
                ('funcao', models.ForeignKey(to='voluntario.Funcao')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Voluntario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.CharField(max_length=1, choices=[(b'T', b'Trabalhador'), (b'C', b'Colaborador'), (b'A', b'Apoio')])),
                ('data_inicio', models.DateField(null=True, blank=True)),
                ('data_fim', models.DateField(null=True, blank=True)),
                ('ativo', models.BooleanField()),
                ('observacao', models.TextField(null=True, blank=True)),
                ('dia_estudo', models.CharField(blank=True, max_length=1, null=True, choices=[(b'T', b'Ter\xc3\xa7a'), (b'X', b'Sexta')])),
                ('paciente', models.ForeignKey(to='paciente.Paciente')),
            ],
            options={
                'ordering': ['paciente__nome'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='trabalho',
            name='voluntario',
            field=models.ForeignKey(to='voluntario.Voluntario'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='funcaovoluntario',
            name='voluntario',
            field=models.ForeignKey(to='voluntario.Voluntario'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agendatrabalho',
            name='voluntario',
            field=models.ForeignKey(to='voluntario.Voluntario'),
            preserve_default=True,
        ),
    ]
