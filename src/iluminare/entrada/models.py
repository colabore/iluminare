# -*- encoding: utf-8 -*-

from django.db import models

class Paciente(models.Model):
    nome            = models.CharField(max_length=100)
    prioridade      = models.BooleanField() 
    data_nascimento = models.DateField()
    email           = models.EmailField(max_length=100)
    saude           = models.CharField(max_length=250)

    acompanhante    = models.ForeignKey('self', null=True, blank=True)
    tratamento      = models.ManyToManyField('Tratamento', through='TratamentoEmAndamento')

    def __unicode__(self):
        return self.nome

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

    sala    = models.CharField(max_length=50)
    dia     = models.CharField(max_length=1, choices=DIAS)

    medico_espiritual = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s: %s (%s)" % (self.sala, self.medico_espiritual, self.get_dia_display()) 

class TratamentoEmAndamento(models.Model):
    paciente    = models.ForeignKey(Paciente)
    tratamento  = models.ForeignKey(Tratamento)

    data_inicio = models.DateField('data de início')

    def __unicode__(self):
        return "%s (%s - %s)" % (self.paciente.nome, self.tratamento.get_dia_display(), self.tratamento.sala)

class Atendimento(models.Model):
    hora_chegada    = models.DateTimeField('hora de chegada')
    observacao      = models.TextField(max_length=1000, blank=True)
    
    atendido        = models.BooleanField()
    chamado         = models.BooleanField()
    
    paciente        = models.ForeignKey(Paciente)
    tratamento      = models.ForeignKey(Tratamento)

    def __unicode__(self):
        return "%s (%s)" % (self.paciente.nome, self.hora_chegada.strftime("%d/%m/%y"))
