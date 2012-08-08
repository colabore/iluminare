# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Atendimento'
        db.create_table('atendimento_atendimento', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('paciente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['paciente.Paciente'])),
            ('instancia_tratamento', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tratamento.InstanciaTratamento'])),
            ('hora_chegada', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('hora_atendimento', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('prioridade', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('observacao_prioridade', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('observacao', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('senha', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('atendimento', ['Atendimento'])


    def backwards(self, orm):
        # Deleting model 'Atendimento'
        db.delete_table('atendimento_atendimento')


    models = {
        'atendimento.atendimento': {
            'Meta': {'object_name': 'Atendimento'},
            'hora_atendimento': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'hora_chegada': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instancia_tratamento': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tratamento.InstanciaTratamento']"}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'observacao_prioridade': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'paciente': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['paciente.Paciente']"}),
            'prioridade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'senha': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'})
        },
        'paciente.paciente': {
            'Meta': {'ordering': "['nome']", 'object_name': 'Paciente'},
            'acompanhante': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['paciente.Paciente']", 'null': 'True', 'blank': 'True'}),
            'acompanhante_crianca': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'acompanhantecrianca'", 'null': 'True', 'to': "orm['paciente.Paciente']"}),
            'data_nascimento': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'detalhe_ficha': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'endereco': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'escolaridade': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'estado_civil': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'frequencia': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'hora_nascimento': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_nascimento': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'observacao': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'profissao': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'saude': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sexo': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'telefones': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'tem_ficha': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'tratamento.instanciatratamento': {
            'Meta': {'object_name': 'InstanciaTratamento'},
            'coletivo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'data': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medico_espiritual': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'observacoes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'tratamento': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tratamento.Tratamento']"})
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
        }
    }

    complete_apps = ['atendimento']