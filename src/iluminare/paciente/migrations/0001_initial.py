# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DetalhePrioridade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.CharField(blank=True, max_length=1, null=True, choices=[(b'P', b'Prioridade'), (b'G', b'Gr\xc3\xa1vida'), (b'L', b'Lactante'), (b'C', b'Crianca'), (b'B', b'Baixa Imunidade')])),
                ('data_inicio', models.DateField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100)),
                ('sexo', models.CharField(blank=True, max_length=1, null=True, choices=[(b'M', b'Masculino'), (b'F', b'Feminino')])),
                ('telefones', models.CharField(max_length=45, null=True, blank=True)),
                ('endereco', models.CharField(max_length=300, null=True, blank=True)),
                ('bairro', models.CharField(max_length=300, null=True, blank=True)),
                ('cidade', models.CharField(max_length=300, null=True, blank=True)),
                ('estado', models.CharField(blank=True, max_length=2, null=True, choices=[(b'AC', b'Acre'), (b'AL', b'Alagoas'), (b'AM', b'Amanozas'), (b'AP', b'Amap\xc3\xa1'), (b'BA', b'Bahia'), (b'CE', b'Cear\xc3\xa1'), (b'DF', b'Distrito Federal'), (b'ES', b'Esp\xc3\xadrito Santo'), (b'GO', b'Goi\xc3\xa1s'), (b'MA', b'Maranh\xc3\xa3o'), (b'MG', b'Minas Gerais'), (b'MS', b'Mato Grosso do Sul'), (b'MT', b'Mato Grosso'), (b'PA', b'Par\xc3\xa1'), (b'PB', b'Para\xc3\xadba'), (b'PE', b'Pernambuco'), (b'PI', b'Piau\xc3\xad'), (b'PR', b'Paran\xc3\xa1'), (b'RJ', b'Rio de Janeiro'), (b'RN', b'Rio Grande no Norte'), (b'RO', b'Rond\xc3\xb4nia'), (b'RR', b'Roraima'), (b'RS', b'Rio Grande do Sul'), (b'SC', b'Santa Catarina'), (b'SE', b'Sergipe'), (b'SP', b'S\xc3\xa3o Paulo'), (b'TO', b'Tocantins')])),
                ('pais', models.CharField(max_length=300, null=True, blank=True)),
                ('cep', models.CharField(max_length=15, null=True, blank=True)),
                ('email', models.EmailField(max_length=100, null=True, blank=True)),
                ('data_nascimento', models.DateField(null=True, blank=True)),
                ('hora_nascimento', models.TimeField(null=True, blank=True)),
                ('local_nascimento', models.CharField(max_length=100, null=True, blank=True)),
                ('escolaridade', models.CharField(blank=True, max_length=1, null=True, choices=[(b'1', b'Ensino B\xc3\xa1sico'), (b'2', b'Ensino Fundamental'), (b'3', b'Ensino M\xc3\xa9dio'), (b'4', b'Ensino T\xc3\xa9cnico'), (b'5', b'Curso Superior'), (b'6', b'Especializa\xc3\xa7\xc3\xa3o'), (b'7', b'Mestrado'), (b'8', b'Doutorado')])),
                ('estado_civil', models.CharField(blank=True, max_length=1, null=True, choices=[(b'1', b'Solteiro'), (b'2', b'Casado'), (b'3', b'Separado'), (b'4', b'Divorciado'), (b'5', b'Vi\xc3\xbavo')])),
                ('frequencia', models.CharField(blank=True, max_length=1, null=True, choices=[(b'S', b'Semanal'), (b'Q', b'Quinzenal'), (b'M', b'Mensal'), (b'O', b'Outro')])),
                ('observacao', models.CharField(max_length=200, null=True, blank=True)),
                ('profissao', models.CharField(max_length=100, null=True, blank=True)),
                ('tem_ficha', models.BooleanField()),
                ('detalhe_ficha', models.CharField(max_length=200, null=True, blank=True)),
                ('saude', models.TextField(null=True, blank=True)),
                ('acompanhante', models.ForeignKey(blank=True, to='paciente.Paciente', null=True)),
                ('acompanhante_crianca', models.ForeignKey(related_name='acompanhantecrianca', blank=True, to='paciente.Paciente', null=True)),
                ('casado_com', models.ForeignKey(related_name='casadocom', blank=True, to='paciente.Paciente', null=True)),
            ],
            options={
                'ordering': ['nome'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='detalheprioridade',
            name='paciente',
            field=models.ForeignKey(to='paciente.Paciente'),
            preserve_default=True,
        ),
    ]
