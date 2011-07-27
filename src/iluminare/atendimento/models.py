#!/usr/bin/env python
# coding: utf-8

from django.db import models
from iluminare.paciente.models import *
from iluminare.tratamento.models import *

class Atendimento(models.Model):
    
    STATUS = (
        ('C','CHECK-IN'), 
        ('I','IMPRESSO'), 
        ('X','CHAMADO'), 
        ('A','ATENDIDO'), 
        ('N','NAO-ATENDIDO'))

    paciente                = models.ForeignKey(Paciente, null = False, blank = False)
    instancia_tratamento    = models.ForeignKey(InstanciaTratamento, null = False, blank = False)
    hora_chegada            = models.TimeField(null = True, blank = True)
    status                  = models.CharField(max_length=1, choices=STATUS, null= True, blank = True)
    prioridade              = models.BooleanField(blank=True) 
    observacao_prioridade   = models.CharField(max_length = 100, blank = True, null = True)
    observacao              = models.TextField(null = True, blank = True)    
    senha                   = models.CharField(max_length=10, null = True, blank=True)

    def __unicode__(self):
        return "%s (%s)" % (self.paciente.nome, self.hora_chegada)

