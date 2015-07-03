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
        ('M','Mensal'),
        ('O','Outro'))

    ESTADO_CIVIL = (
        ('1', 'Solteiro'),
        ('2', 'Casado'),
        ('3', 'Separado'),
        ('4', 'Divorciado'),
        ('5', 'Viúvo'))

    ESCOLARIDADE = (
        ('1', 'Ensino Básico'),
        ('2', 'Ensino Fundamental'),
        ('3', 'Ensino Médio'),
        ('4', 'Ensino Técnico'),
        ('5', 'Curso Superior'),
        ('6', 'Especialização'),
        ('7', 'Mestrado'),
        ('8', 'Doutorado'))

    ESTADO = (
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AM', 'Amanozas'),
        ('AP', 'Amapá'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MG', 'Minas Gerais'),
        ('MS', 'Mato Grosso do Sul'),
        ('MT', 'Mato Grosso'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('PR', 'Paraná'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande no Norte'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('RS', 'Rio Grande do Sul'),
        ('SC', 'Santa Catarina'),
        ('SE', 'Sergipe'),
        ('SP', 'São Paulo'),
        ('TO', 'Tocantins'))

    nome                    = models.CharField(max_length=100, blank = False, null = False)
    sexo                    = models.CharField(max_length=1, choices = SEXO , null= True, blank = True)
    telefones               = models.CharField(max_length=45, blank = True, null = True)
    endereco                = models.CharField(max_length=300, blank = True, null = True)
    bairro                  = models.CharField(max_length=300, blank = True, null = True)
    cidade                  = models.CharField(max_length=300, blank = True, null = True)
    estado                  = models.CharField(max_length=2, choices = ESTADO , null= True, blank = True)
    pais                    = models.CharField(max_length=300, blank = True, null = True)
    cep                     = models.CharField(max_length=15, blank = True, null = True)
    email                   = models.EmailField(max_length=100, null=True, blank=True)
    data_nascimento         = models.DateField(blank = True, null = True)
    hora_nascimento         = models.TimeField(blank = True, null = True)
    local_nascimento        = models.CharField(max_length=100, blank = True, null = True)
    escolaridade            = models.CharField(max_length=1, choices = ESCOLARIDADE, null= True, blank = True)
    estado_civil            = models.CharField(max_length=1, choices = ESTADO_CIVIL, null= True, blank = True)
    frequencia              = models.CharField(max_length=1, choices = FREQUENCIA, null=True, blank=True)
    observacao              = models.CharField(max_length=200, blank = True, null = True)
    profissao               = models.CharField(max_length=100, blank = True, null = True)
    tem_ficha               = models.BooleanField(blank=True, default=False)
    detalhe_ficha           = models.CharField(max_length=200, blank = True, null = True)
    saude                   = models.TextField(null=True, blank=True)
    acompanhante            = models.ForeignKey('self', null=True, blank=True)
    acompanhante_crianca    = models.ForeignKey('self', null=True, blank=True, related_name='acompanhantecrianca')
    casado_com              = models.ForeignKey('self', null=True, blank=True, related_name='casadocom')

    class Meta:
        ordering = ['nome']

    def __unicode__(self):
        return self.nome

    def get_tratamentos(self):
        return self.tratamentopaciente_set.filter(status='A', paciente=self)

    def is_voluntario(self):
        from iluminare.voluntario.models import Voluntario
        return Voluntario.objects.filter(paciente = self, ativo=True) == True

    def get_last_atendimento(self):
        from iluminare.tratamento.models import InstanciaTratamento
        result = None
        try:
            result =  InstanciaTratamento.objects.raw("""select it.* from paciente_paciente as p
                join atendimento_atendimento as ate
                    on p.id = ate.paciente_id
                join tratamento_instanciatratamento as it
                    on ate.instancia_tratamento_id = it.id
                where p.id = %d and ate.status = 'A'
                order by it.data desc
                limit 1;""" % paciente.id)[0]
        except:
            return result

    def checked_in_today(self):
        import datetime
        from iluminare.tratamento.models import InstanciaTratamento
        jtc = False
        try:
            # para o caso de já ter algum checkin hoje...
            it_jtc = InstanciaTratamento.objects.raw("""select it.* from paciente_paciente as p
                join atendimento_atendimento as ate
    	            on p.id = ate.paciente_id
                join tratamento_instanciatratamento as it
    	            on ate.instancia_tratamento_id = it.id
                where p.id = %d
                order by it.data desc
                limit 1;""" % self.id)[0]
            if it_jtc.data == datetime.datetime.today().date():
                jtc = True
        except:
            pass

        return jtc

class DetalhePrioridade(models.Model):
    TIPO = (
        ('P', 'Prioridade'),
        ('G', 'Grávida'),
        ('L', 'Lactante'),
        ('C', 'Crianca'),
        ('B', 'Baixa Imunidade'))

    paciente        = models.ForeignKey(Paciente, null = False, blank = False)
    tipo            = models.CharField(max_length=1, choices = TIPO, null = True, blank = True)
    data_inicio     = models.DateField(blank = True, null = True)

    # ajustar
    def __unicode__(self):
        return "%s - %s - %s" % (self.paciente.nome, self.get_tipo_display(), str(self.data_inicio))
