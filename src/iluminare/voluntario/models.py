# coding: utf-8

from django.db import models
from iluminare.paciente.models import Paciente
from iluminare.tratamento.models import Tratamento

class Funcao(models.Model):
    descricao       = models.TextField(null = False, blank = False)
    tratamento      = models.ForeignKey(Tratamento, null = True, blank = True)

    def __unicode__(self):
        return self.descricao

class Voluntario(models.Model):
    # Retiramos a opcao (C, Colaborador).
    # A partir de 2014 o perfil colaborador deixou de existir.
    # A base de dados e algumas telas do sistema continuam com o colaborador para consulta.
    TIPO = (('T', "Trabalhador"),('A',"Apoio"))
    DIAS = (
        ('T', 'Terça'),
        ('X', 'Sexta'))

    paciente        = models.ForeignKey(Paciente, null = False, blank = False)
    tipo            = models.CharField(max_length = 1, choices = TIPO)
    data_inicio     = models.DateField(null = True, blank = True)
    data_fim        = models.DateField(null = True, blank = True)
    ativo           = models.BooleanField(blank = True, default=True)
    observacao      = models.TextField(null = True, blank = True)
    dia_estudo      = models.CharField(max_length=1, choices = DIAS, null = True, blank = True)

    class Meta:
        ordering = ['paciente__nome']


    def __unicode__(self):
        return "%s status: %s" % (self.paciente.nome, self.tipo)

class Trabalho(models.Model):
    STATUS = (
        ('PR', "Presente"),
        ('FA', "Falta"),
        ('FV', "Falta por Viagem"),
        ('FT', "Falta por Trabalho"),
        ('FL', "Falta por Licença"),
        ('FS', "Falta por Saúde"),
        ('NA', "Não se Aplica"),
        ('NI', "Não Informado")
    )

    funcao          = models.ForeignKey(Funcao, null = False, blank = False)
    voluntario      = models.ForeignKey(Voluntario, null = False, blank = False)
    status          = models.CharField(max_length = 2, choices = STATUS, null=True, blank=True)
    data            = models.DateField(null = False, blank = False)
    hora_inicio     = models.TimeField(null=True, blank=True)
    hora_final      = models.TimeField(null=True, blank=True)

    def __unicode__(self):
        return "%s: %s - %s (%s - %s) - %s" % (self.funcao.descricao, self.voluntario.paciente.nome, self. data, self.hora_inicio, self.hora_final, self.status)

# Dúvida.
# Mantemos no model essa classe auxiliar ou criamos um relacionamento M-N diretamente em python?
class FuncaoVoluntario(models.Model):
    funcao          = models.ForeignKey("Funcao")
    voluntario      = models.ForeignKey("Voluntario")

    def __unicode__(self):
        return "%s : %s" % (self.funcao.descricao, self.voluntario.paciente.nome)

class AgendaTrabalho(models.Model):
    voluntario      = models.ForeignKey(Voluntario, null = False, blank = False)
    data            = models.DateField(null = False, blank = False)
    hora_chegada    = models.TimeField(null = True, blank = True)
    hora_saida      = models.TimeField(null = True, blank = True)

    def __unicode__(self):
        return "%s - data: %s" % (self.voluntario.paciente.nome, self.data)
