#!/usr/bin/env python
# coding: utf-8

from django.db import models
from iluminare.paciente.models import Paciente
from iluminare.tratamento.models import InstanciaTratamento, AgendaTratamento

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
    hora_atendimento        = models.TimeField(null = True, blank = True)
    status                  = models.CharField(max_length=1, choices=STATUS, null= True, blank = True)
    prioridade              = models.BooleanField(blank=True) 
    observacao_prioridade   = models.CharField(max_length = 100, blank = True, null = True)
    observacao              = models.TextField(null = True, blank = True)    
    senha                   = models.IntegerField(null = True, blank=True)

    def __unicode__(self):
        return "%s - %s - %s - %s" % (self.paciente.nome, self.hora_chegada, str(self.instancia_tratamento.data), \
            self.instancia_tratamento.tratamento.descricao_basica)
class AgendaAtendimento(models.Model):
    STATUS = (
        ('A','Aberto'),
        ('C','Cancelado'),
        ('F','Fechado'))

    agenda_tratamento       = models.ForeignKey(AgendaTratamento, null = False, blank = False)

    # Podemos ter ou não o atendimento que originou o agendamento.
    # É o atendimento que originou o agendamento
    atendimento_origem      = models.ForeignKey(Atendimento, null = True, blank = True, related_name="atendimentoorigem")

    # É o atendimento que encerra o agendamento. Depois desse atendimento, o status do agendamento vai para fechado.
    atendimento_realizado   = models.ForeignKey(Atendimento, null = True, blank = True, related_name="atendimentorealizado")
    paciente                = models.ForeignKey(Paciente, null = False, blank = False)
    status                  = models.CharField(max_length=1, choices=STATUS, null = True, blank = True)

    def __unicode__(self):
        return u'%s %s %s' % (self.agenda_tratamento, self.paciente.nome, self.status)

class Notificacao(models.Model):
    UNIDADE = (
        ('D', 'Dias'),
        ('S', 'Semanas'),
        ('M', 'Meses'))

    descricao           = models.CharField(max_length=200, null = False, blank = False)
    ativo               = models.BooleanField(blank=True)
    fixo                = models.BooleanField(blank=True)
    data_criacao        = models.DateField(blank = True, null = True)
    data_validade       = models.DateField(blank = True, null = True)
    impressao           = models.BooleanField(blank=True)
    tela_checkin        = models.BooleanField(blank=True)
    prazo_num           = models.SmallIntegerField(null = True, blank = True)
    prazo_unidade       = models.CharField(max_length=1, choices = UNIDADE, null = True, blank = True)
    qtd_atendimentos    = models.SmallIntegerField(null = True, blank = True)
    paciente            = models.ForeignKey(Paciente, null = False, blank = False)
    atendimento         = models.ForeignKey(Atendimento, null = True, blank = True)

    def __unicode__(self):
        return "(Ativo: %s) %s - %s" % (self.ativo, self.paciente.nome, self.descricao)

