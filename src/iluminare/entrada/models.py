from django.db import models

class Pessoa(models.Model):
    nome = models.CharField(max_length=200)
    data_nascimento = models.DateField()

    def __unicode__(self):
        return self.nome

class Presenca(models.Model):
    pessoa = models.ForeignKey(Pessoa)

    hora_chegada = models.DateTimeField('hora de chegada')
    hora_atendimento = models.DateTimeField('hora do atendimento')

    def __unicode__(self):
        return self.pessoa.nome + ' ' + self.hora_chegada.strftime("%d/%m/%y")
# Create your models here.
