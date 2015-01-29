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
            name='AgendaAtendimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(blank=True, max_length=1, null=True, choices=[(b'A', b'Aberto'), (b'C', b'Cancelado'), (b'F', b'Fechado')])),
                ('data_criacao', models.DateField(null=True, blank=True)),
                ('agenda_tratamento', models.ForeignKey(to='tratamento.AgendaTratamento')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Atendimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hora_chegada', models.TimeField(null=True, blank=True)),
                ('hora_atendimento', models.TimeField(null=True, blank=True)),
                ('status', models.CharField(blank=True, max_length=1, null=True, choices=[(b'C', b'CHECK-IN'), (b'I', b'IMPRESSO'), (b'X', b'CHAMADO'), (b'A', b'ATENDIDO'), (b'N', b'NAO-ATENDIDO')])),
                ('prioridade', models.BooleanField()),
                ('observacao_prioridade', models.CharField(max_length=100, null=True, blank=True)),
                ('observacao', models.TextField(null=True, blank=True)),
                ('senha', models.IntegerField(null=True, blank=True)),
                ('instancia_tratamento', models.ForeignKey(to='tratamento.InstanciaTratamento')),
                ('paciente', models.ForeignKey(to='paciente.Paciente')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descricao', models.CharField(max_length=200)),
                ('ativo', models.BooleanField()),
                ('fixo', models.BooleanField()),
                ('data_criacao', models.DateField(null=True, blank=True)),
                ('data_validade', models.DateField(null=True, blank=True)),
                ('impressao', models.BooleanField()),
                ('tela_checkin', models.BooleanField()),
                ('prazo_num', models.SmallIntegerField(null=True, blank=True)),
                ('prazo_unidade', models.CharField(blank=True, max_length=1, null=True, choices=[(b'D', b'Dias'), (b'S', b'Semanas'), (b'M', b'Meses')])),
                ('qtd_atendimentos', models.SmallIntegerField(null=True, blank=True)),
                ('atendimento', models.ForeignKey(blank=True, to='atendimento.Atendimento', null=True)),
                ('paciente', models.ForeignKey(to='paciente.Paciente')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='agendaatendimento',
            name='atendimento_origem',
            field=models.ForeignKey(related_name='atendimentoorigem', blank=True, to='atendimento.Atendimento', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agendaatendimento',
            name='atendimento_realizado',
            field=models.ForeignKey(related_name='atendimentorealizado', blank=True, to='atendimento.Atendimento', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='agendaatendimento',
            name='paciente',
            field=models.ForeignKey(to='paciente.Paciente'),
            preserve_default=True,
        ),
    ]
