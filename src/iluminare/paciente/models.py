#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.db import models

class Paciente(models.Model):
    SEXO = (
		('M','Masculino'), 
		('F','Feminino'))

    FREQUENCIA = (
		('S','Semanal'), 
		('Q','Quinzenal'), 
		('M','Mensal'))
    	
    nome                = models.CharField(max_length=100, blank = False, null = False)
    data_nascimento     = models.DateField(blank = True, null = True)    
    sexo 	        	= models.CharField(max_length=1, choices = SEXO , null= True, blank = True)    
    email               = models.EmailField(max_length=100, null=True, blank=True)    
    prioridade          = models.BooleanField(blank = True)     
    frequencia			= models.CharField(max_length= 1, choices = FREQUENCIA, null=True, blank=True)
    obeservacao         = models.TextField(null=True, blank=True)    
    saude               = models.TextField(null=True, blank=True)    	
    acompanhante        = models.ForeignKey('self', null=True, blank=True)
   
    def __unicode__(self):
        return self.nome
        
class TipoPrioridade(models.Model):
    paciente                = models.ForeignKey(Paciente, null = False, blank = False)

    gravida                 = models.BooleanField(blank = True)
    data_inicio_gravidez    = models.DateField(blank = True, null = True)
    lactante                = models.BooleanField(blank = True)
    data_inicio_amamentacao = models.DateField(blank = True, null = True)
    crianca                 = models.BooleanField(blank = True) 

