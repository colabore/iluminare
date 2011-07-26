# coding: utf-8
from django.db import models
from iluminare.paciente.models import *
from iluminare.atendimento.models import *

class Sala(models.Model):
    descricao   = models.CharField(max_length = 45, blank = False, null = False)

    def __unicode__(self):
        return "%s" % self.descricao 



class Tratamento(models.Model):
	
	DIAS = ( 
        ('D', 'Domingo'),
        ('S', 'Segunda'),
        ('T', 'Terça'),
        ('Q', 'Quarta'),
        ('N', 'Quinta'),
        ('X', 'Sexta'),
        ('B', 'Sábado'))
    
	sala                = models.ForeignKey(Sala, null = False, blank = False)
	descricao_basica    = models.CharField(max_length=100, blank = False, null = False)
	descricao_completa  = models.TextField(blank = True, null = True)
	dia_semana          = models.CharField(max_length=1, choices = DIAS, null = True, blank = True)	
	horario_limite      = models.TimeField(null = True, blank = True)
	max_agendamentos    = models.IntegerField(null = True, blank = True)

	def __unicode__(self):
		return "%s dia %s" % (self.descricao_basica, self.dia_semana)

class TratamentoPaciente(models.Model):
    paciente    = models.ForeignKey(Paciente, null = False, blank = False)
    tratamento  = models.ForeignKey(Tratamento, null = False, blank = False)

    data_inicio = models.DateField(null=True, blank=True)
    data_fim    = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return "%s %s (%s - %s)" % (self.paciente.nome, self.tratamento, self.data_inicio, self.data_fim)

class InstanciaTratamento(models.Model):
    tratamento			= models.ForeignKey(Tratamento, null = False, blank = False)
    
    data                = models.DateField(null = False, blank = False)    
    medico_espiritual 	= models.CharField(max_length = 45, blank = True, null = True)
    coletivo			= models.BooleanField(blank = True)
    observacoes			= models.TextField(blank = True, null = True)

    def __unicode__(self):
		return "%s em %s" % (self.tratamento, self.data)
		
class AgendaTratamento(models.Model):
    paciente		= models.ForeignKey(Paciente, null = False, blank = False)
    
    tratamento		= models.ForeignKey(Tratamento, null = False, blank = False)
    data            = models.DateField(null = True, blank = True)
    
    def __unicode__(self):
        return "%s %s %s" % (self.paciente, self.tratamento, self.data)

