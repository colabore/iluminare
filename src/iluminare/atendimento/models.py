#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.db import models
from iluminare.paciente.models import *


class Tratamento(models.Model):
    DIAS = ( 
        ('D', 'Domingo'),
        ('S', 'Segunda'),
        ('T', 'Terça'),
        ('Q', 'Quarta'),
        ('N', 'Quinta'),
        ('X', 'Sexta'),
        ('B', 'Sábado')
    )
    
    sala                = models.ForeignKey("Sala")

    descricao_basica    = models.CharField(max_length=100, blank = False, null = False)
    descricao_completa  = models.TextField(blank = True, null = True)
    dia_semana          = models.CharField(max_length=1, choices = DIAS)	
    horario_limite      = models.TimeField(null = True, blank = True)
    max_agendamentos    = models.IntegerField(null = True, blank = True)

    def __unicode__(self):
        return "%s dia %s" % (self.descricao_basica, self.dia_semana)

class Sala(models.Model):
    descricao   = models.CharField(max_length = 45, blank = False, null = False)

    def __unicode__(self):
        return "%s" % self.descricao 

class Tratamento_Paciente(models.Model):
    paciente    = models.ForeignKey(Paciente, null = False, blank = False)
    tratamento  = models.ForeignKey(Tratamento, null = False, blank = False)

    data_inicio = models.DateField('data de início', null=True, blank=True)
    data_fim    = models.DateField('data de término', null=True, blank=True)

    def __unicode__(self):
        return "%s %s (%s - %s)" % (self.paciente.nome, self.tratamento, self.data_inicio, self.data_fim)

class Instancia_Tratamento(models.Model):
    tratamento			= models.ForeignKey(Tratamento_Paciente, null = False, blank = False)
    
    data                = models.DateField(null = False, blank = False)    
    medico_espiritual 	= models.CharField(max_length = 45, blank = True, null = True)
    coletivo			= models.BooleanField(blank = True)
    observacoes			= models.TextField(blank = True, null = True)

    def __unicode__(self):
		return "%s em %s" % (self.tratamento)
		

class Atendimento(models.Model):
    
    STATUS = (('C','CHECK-IN'), ('I','IMPRESSO'), ('X','CHAMADO'), ('A','ATENDIDO'), ('N','NAO-ATENDIDO'))
    paciente        		= models.ForeignKey(Paciente)
    instancia_tratamento    = models.ForeignKey(Instancia_Tratamento)    

    hora_chegada            = models.TimeField('hora de chegada', null = True, blank = True)    
    status                  = models.CharField(max_length = 1, blank = False, null = False)    
    prioridade              = models.BooleanField(blank = True) 
    detalhe_prioridade      = models.CharField(max_length = 100, blank = True, null = True)
    observacao              = models.TextField(null = True, blank = True)    
    senha                   = models.CharField(max_length=10, null = True, blank=True)    

    def __unicode__(self):
        return "%s (%s)" % (self.paciente.nome, self.hora_chegada)


class TratamentoEmAndamento(models.Model):
    paciente    = models.ForeignKey(Paciente)
    tratamento  = models.ForeignKey(Tratamento)

    data_inicio = models.DateField('data de início')

    def __unicode__(self):
        return "%s (%s - %s)" % (self.paciente.nome, self.tratamento.get_dia_display(), self.tratamento.sala)


class Agenda_Atendimento(models.Model):
    
    paciente		= models.ForeignKey(Paciente, null = False, blank = False)
    
    tratamento		= models.ForeignKey(Tratamento, null = False, blank = False)
    data            = models.DateField(null = True, blank = True)
    
    def __unicode__(self):
        return "%s %s %s" % (self.paciente, self.tratamento)


