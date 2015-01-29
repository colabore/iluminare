# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paciente', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgendaTratamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.DateField(null=True, blank=True)),
                ('max_agendamentos', models.SmallIntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstanciaTratamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.DateField()),
                ('medico_espiritual', models.CharField(max_length=45, null=True, blank=True)),
                ('coletivo', models.BooleanField()),
                ('observacoes', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sala',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descricao', models.CharField(max_length=45)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tratamento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descricao_basica', models.CharField(max_length=100)),
                ('descricao_completa', models.TextField(null=True, blank=True)),
                ('dia_semana', models.CharField(blank=True, max_length=1, null=True, choices=[(b'D', b'Domingo'), (b'S', b'Segunda'), (b'T', b'Ter\xc3\xa7a'), (b'Q', b'Quarta'), (b'N', b'Quinta'), (b'X', b'Sexta'), (b'B', b'S\xc3\xa1bado')])),
                ('horario_limite', models.TimeField(null=True, blank=True)),
                ('max_agendamentos', models.IntegerField(null=True, blank=True)),
                ('sala', models.ForeignKey(blank=True, to='tratamento.Sala', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TratamentoPaciente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_inicio', models.DateField(null=True, blank=True)),
                ('data_fim', models.DateField(null=True, blank=True)),
                ('status', models.CharField(blank=True, max_length=1, null=True, choices=[(b'C', b'Conclu\xc3\xaddo'), (b'A', b'Em Andamento'), (b'E', b'Encaminhado'), (b'D', b'Desistiu'), (b'T', b'Temporariamente afastado')])),
                ('paciente', models.ForeignKey(to='paciente.Paciente')),
                ('tratamento', models.ForeignKey(to='tratamento.Tratamento')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='instanciatratamento',
            name='tratamento',
            field=models.ForeignKey(to='tratamento.Tratamento'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agendatratamento',
            name='tratamento',
            field=models.ForeignKey(to='tratamento.Tratamento'),
            preserve_default=True,
        ),
    ]
