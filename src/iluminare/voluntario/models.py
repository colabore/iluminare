#!/usr/bin/env python
# coding: utf-8

from django.db import models
from iluminare.paciente.models import Paciente
from iluminare.atendimento.models import Tratamento

class Trabalho(models.Model):
    funcao	        = models.ForeignKey("Funcao")
    voluntario	    = models.ForeignKey("Voluntario")
    
    data            = models.DateField(null = False, blank = False)
    hora_inicio     = models.TimeField('horario inicial do expediente', null=True, blank=True)
    hora_final      = models.TimeField('horario final do expediente', null=True, blank=True)

    def __unicode__(self):
		return "%s: %s - %s (%s - %s)" % (self.funcao.descricao, self.voluntario.paciente.nome, self. data, self.hora_inicio, self.hora_final)

class Funcao(models.Model):
    descricao       = models.TextField(null = False, blank = False)
    tratamento      = models.ForeignKey(Tratamento, null = True, blank = True)    

    def __unicode__(self):
		return self.descricao

class Voluntario(models.Model):
    TIPO = (('T', "Trabalhador"),('C',"Colaborador"))
    
    paciente	    = models.ForeignKey(Paciente, null = False, blank = False)
    tipo            = models.CharField(max_length = 1, null = False, blank = False)
    data_inicio     = models.DateField(null = True, blank = True)
    data_fim        = models.DateField(null = True, blank = True)
    ativo           = models.BooleanField(blank = True)    
    observacao      = models.TextField(null = True, blank = True)       
    
    
    def __unicode__(self):
		return "%s atividade: %s" % (self.paciente.nome, self.tipo) 

class FuncaoVoluntario(models.Model):
    funcao          = models.ForeignKey("Funcao")
    voluntario      = models.ForeignKey("Voluntario")

    def __unicode__(self):
    	return "%s : %s" % (self.funcao.descricao, self.voluntario.paciente.nome)

class AgendaTrabalho(models.Model):
    voluntario		= models.ForeignKey(Voluntario, null = False, blank = False)
    data            = models.DateField(null = False, blank = False)    
    hora_chegada	= models.TimeField(null = True, blank = True)
    hora_saida		= models.TimeField(null = True, blank = True)

    def __unicode__(self):
        return "%s - data: %s" % (self.voluntario.paciente.nome, self.data)

