# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Voluntario.dia_estudo'
        db.add_column('voluntario_voluntario', 'dia_estudo',
                      self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Voluntario.dia_estudo'
        db.delete_column('voluntario_voluntario', 'dia_estudo')


    models = {
        'paciente.paciente': {
            'Meta': {'ordering': "['nome']", 'object_name': 'Paciente'},
            'acompanhante': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['paciente.Paciente']", 'null': 'True', 'blank': 'True'}),
            'acompanhante_crianca': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'acompanhantecrianca'", 'null': 'True', 'to': "orm['paciente.Paciente']"}),
            'bairro': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'casado_com': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'casadocom'", 'null': 'True', 'to': "orm['paciente.Paciente']"}),
            'cep': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'cidade': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'data_nascimento': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'detalhe_ficha': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'endereco': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'escolaridade': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'estado': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'estado_civil': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'frequencia': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'hora_nascimento': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_nascimento': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'observacao': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'pais': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'profissao': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'saude': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sexo': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'telefones': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'tem_ficha': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'tratamento.sala': {
            'Meta': {'object_name': 'Sala'},
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'tratamento.tratamento': {
            'Meta': {'object_name': 'Tratamento'},
            'descricao_basica': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'descricao_completa': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dia_semana': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'horario_limite': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_agendamentos': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sala': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tratamento.Sala']", 'null': 'True', 'blank': 'True'})
        },
        'voluntario.agendatrabalho': {
            'Meta': {'object_name': 'AgendaTrabalho'},
            'data': ('django.db.models.fields.DateField', [], {}),
            'hora_chegada': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'hora_saida': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'voluntario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voluntario.Voluntario']"})
        },
        'voluntario.funcao': {
            'Meta': {'object_name': 'Funcao'},
            'descricao': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tratamento': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tratamento.Tratamento']", 'null': 'True', 'blank': 'True'})
        },
        'voluntario.funcaovoluntario': {
            'Meta': {'object_name': 'FuncaoVoluntario'},
            'funcao': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voluntario.Funcao']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'voluntario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voluntario.Voluntario']"})
        },
        'voluntario.trabalho': {
            'Meta': {'object_name': 'Trabalho'},
            'data': ('django.db.models.fields.DateField', [], {}),
            'funcao': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voluntario.Funcao']"}),
            'hora_final': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'hora_inicio': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'voluntario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voluntario.Voluntario']"})
        },
        'voluntario.voluntario': {
            'Meta': {'ordering': "['paciente__nome']", 'object_name': 'Voluntario'},
            'ativo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'data_fim': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_inicio': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'dia_estudo': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'paciente': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['paciente.Paciente']"}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        }
    }

    complete_apps = ['voluntario']