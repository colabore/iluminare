# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Paciente'
        db.create_table('paciente_paciente', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sexo', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('telefones', self.gf('django.db.models.fields.CharField')(max_length=45, null=True, blank=True)),
            ('endereco', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=100, null=True, blank=True)),
            ('data_nascimento', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('hora_nascimento', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('local_nascimento', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('escolaridade', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('estado_civil', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('frequencia', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('observacao', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('profissao', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('tem_ficha', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('detalhe_ficha', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('saude', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('acompanhante', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['paciente.Paciente'], null=True, blank=True)),
            ('acompanhante_crianca', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='acompanhantecrianca', null=True, to=orm['paciente.Paciente'])),
        ))
        db.send_create_signal('paciente', ['Paciente'])

        # Adding model 'DetalhePrioridade'
        db.create_table('paciente_detalheprioridade', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('paciente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['paciente.Paciente'])),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('data_inicio', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('paciente', ['DetalhePrioridade'])


    def backwards(self, orm):
        # Deleting model 'Paciente'
        db.delete_table('paciente_paciente')

        # Deleting model 'DetalhePrioridade'
        db.delete_table('paciente_detalheprioridade')


    models = {
        'paciente.detalheprioridade': {
            'Meta': {'object_name': 'DetalhePrioridade'},
            'data_inicio': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paciente': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['paciente.Paciente']"}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'})
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
        }
    }

    complete_apps = ['paciente']