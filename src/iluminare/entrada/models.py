# -*- encoding: utf-8 -*-

from django.db import models

class Paciente(models.Model):
    nome            = models.CharField(max_length=100)
    prioridade      = models.BooleanField() 
    data_nascimento = models.DateField()
    email           = models.EmailField(max_length=100)
    saude           = models.CharField(max_length=250)

    acompanhante    = models.ForeignKey('self', null=True, blank=True)

    def __unicode__(self):
        return self.nome

class Atendimento(models.Model):
    hora_chegada    = models.DateTimeField('hora de chegada')
    observacao      = models.TextField(max_length=1000, blank=True)
    
    atendido        = models.BooleanField()
    chamado         = models.BooleanField()
    
    paciente        = models.ForeignKey(Paciente)

    def __unicode__(self):
        return "%s (%s)" % (self.paciente.nome, self.hora_chegada.strftime("%d/%m/%y"))

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
        return "%s: %s (%s)" % (self.sala, self.medico_espiritual, self.dia) 
