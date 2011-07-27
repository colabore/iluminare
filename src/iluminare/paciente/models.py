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

    ESTADO_CIVIL = (
        ('1', 'Solteiro'),
        ('2', 'Casado'), 
        ('3', 'Separado'), 
        ('4', 'Divorciado'), 
        ('5', 'Viuvo'))

    ESCOLARIDADE = (
        ('1', 'Ensino Básico'),
        ('2', 'Ensino Fundamental'),
        ('3', 'Ensino Médio'),
        ('4', 'Ensino Técnico'),
        ('5', 'Curso Superior'),
        ('6', 'Especialização'),
        ('7', 'Mestrado'),
        ('8', 'Doutorado'))

    nome                = models.CharField(max_length=100, blank = False, null = False)
    sexo                = models.CharField(max_length=1, choices = SEXO , null= True, blank = True)    
    telefones           = models.CharField(max_length=45, blank = True, null = True)
    endereco            = models.CharField(max_length=300, blank = True, null = True)
    email               = models.EmailField(max_length=100, null=True, blank=True)    
    data_nascimento     = models.DateField(blank = True, null = True)    
    hora_nascimento     = models.TimeField(blank = True, null = True)
    local_nascimento    = models.CharField(max_length=100, blank = True, null = True)
    escolaridade        = models.CharField(max_length=1, choices = ESCOLARIDADE, null= True, blank = True)    
    estado_civil        = models.CharField(max_length=1, choices = ESTADO_CIVIL, null= True, blank = True)    
    prioridade          = models.BooleanField(blank=True)     
    frequencia          = models.CharField(max_length=1, choices = FREQUENCIA, null=True, blank=True)
    observacao          = models.CharField(max_length=200, blank = True, null = True)
    profissao           = models.CharField(max_length=100, blank = True, null = True)
    tem_ficha           = models.BooleanField(blank=True)     
    detalhe_ficha       = models.CharField(max_length=200, blank = True, null = True)
    saude               = models.TextField(null=True, blank=True)    	
    acompanhante        = models.ForeignKey('self', null=True, blank=True)
	# acompanhante2?? 

    def __unicode__(self):
        return self.nome
        
class DetalhePrioridade(models.Model):
    paciente                = models.ForeignKey(Paciente, null = False, blank = False)
    gravida                 = models.BooleanField(blank = True)
    data_inicio_gravidez    = models.DateField(blank = True, null = True)
    lactante                = models.BooleanField(blank = True)
    data_inicio_amamentacao = models.DateField(blank = True, null = True)
    crianca                 = models.BooleanField(blank = True) 
    baixa_imunidade         = models.BooleanField(blank=True)

    # ajustar
    def __unicode__(self):
        return self.paciente.nome

