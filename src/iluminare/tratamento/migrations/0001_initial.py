# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Sala'
        db.create_table('tratamento_sala', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descricao', self.gf('django.db.models.fields.CharField')(max_length=45)),
        ))
        db.send_create_signal('tratamento', ['Sala'])

        # Adding model 'Tratamento'
        db.create_table('tratamento_tratamento', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sala', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tratamento.Sala'], null=True, blank=True)),
            ('descricao_basica', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('descricao_completa', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('dia_semana', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('horario_limite', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('max_agendamentos', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('tratamento', ['Tratamento'])

        # Adding model 'TratamentoPaciente'
        db.create_table('tratamento_tratamentopaciente', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('paciente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['paciente.Paciente'])),
            ('tratamento', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tratamento.Tratamento'])),
            ('data_inicio', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('data_fim', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
        ))
        db.send_create_signal('tratamento', ['TratamentoPaciente'])

        # Adding model 'InstanciaTratamento'
        db.create_table('tratamento_instanciatratamento', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tratamento', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tratamento.Tratamento'])),
            ('data', self.gf('django.db.models.fields.DateField')()),
            ('medico_espiritual', self.gf('django.db.models.fields.CharField')(max_length=45, null=True, blank=True)),
            ('coletivo', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('observacoes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('tratamento', ['InstanciaTratamento'])

        # Adding model 'AgendaTratamento'
        db.create_table('tratamento_agendatratamento', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('paciente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['paciente.Paciente'])),
            ('tratamento', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tratamento.Tratamento'])),
            ('data', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('tratamento', ['AgendaTratamento'])


    def backwards(self, orm):
        # Deleting model 'Sala'
        db.delete_table('tratamento_sala')

        # Deleting model 'Tratamento'
        db.delete_table('tratamento_tratamento')

        # Deleting model 'TratamentoPaciente'
        db.delete_table('tratamento_tratamentopaciente')

        # Deleting model 'InstanciaTratamento'
        db.delete_table('tratamento_instanciatratamento')

        # Deleting model 'AgendaTratamento'
        db.delete_table('tratamento_agendatratamento')


    models = {
        'paciente.paciente': {
            'Meta': {'ordering': "['nome']", 'object_name': 'Paciente'},
            'acompanhante': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['paciente.Paciente']", 'null': 'True', 'blank': 'True'}),
            'acompanhante_crianca': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'acompanhantecrianca'", 'null': 'True', 'to': "orm['paciente.Paciente']"}),
            'bairro': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
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
        'tratamento.agendatratamento': {
            'Meta': {'object_name': 'AgendaTratamento'},
            'data': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paciente': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['paciente.Paciente']"}),
            'tratamento': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tratamento.Tratamento']"})
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
        },
        'tratamento.tratamentopaciente': {
            'Meta': {'object_name': 'TratamentoPaciente'},
            'data_fim': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_inicio': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paciente': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['paciente.Paciente']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'tratamento': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tratamento.Tratamento']"})
        }
    }

    complete_apps = ['tratamento']