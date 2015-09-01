# coding: utf-8
from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import serializers

from paciente.models import *
from atendimento.models import *
from tratamento.models import *
from voluntario.models import *

class PacienteSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Paciente

class PacienteSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    acompanhante = PacienteSimpleSerializer(read_only=True)
    acompanhante_crianca = PacienteSimpleSerializer(read_only=True)
    casado_com = PacienteSimpleSerializer(read_only=True)

    class Meta:
        model = Paciente



class SalaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sala

class TratamentoSerializer(serializers.HyperlinkedModelSerializer):
    sala = SalaSerializer()

    class Meta:
        model = Tratamento
        fields = ('id', 'sala', 'descricao_basica', 'descricao_completa', 'dia_semana', 'horario_limite', 'max_agendamentos')

class TratamentoPacienteSerializer(serializers.HyperlinkedModelSerializer):
    paciente = PacienteSerializer()
    tratamento = TratamentoSerializer()

    class Meta:
        model = TratamentoPaciente

class InstanciaTratamentoSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    tratamento = TratamentoSerializer()

    class Meta:
        model = InstanciaTratamento
        fields = ('id', 'tratamento', 'data', 'medico_espiritual', 'coletivo', 'observacoes')

class AgendaTratamentoSerializer(serializers.HyperlinkedModelSerializer):
    tratamento = TratamentoSerializer()

    class Meta:
        model = AgendaTratamento



class AtendimentoSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    paciente = PacienteSerializer(read_only=True)
    instancia_tratamento = InstanciaTratamentoSerializer(read_only=True)

    class Meta:
        model = Atendimento

class AgendaAtendimentoSerializer(serializers.HyperlinkedModelSerializer):
    agenda_tratamento = AgendaTratamentoSerializer()
    atendimento_origem = AtendimentoSerializer()
    atendimento_realizado = AtendimentoSerializer()
    paciente = PacienteSerializer()

    class Meta:
        model = AgendaAtendimento

class NotificacaoSerializer(serializers.HyperlinkedModelSerializer):
    paciente = PacienteSerializer()
    atendimento = AtendimentoSerializer()

    class Meta:
        model = Notificacao



class FuncaoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Funcao

class VoluntarioSerializer(serializers.HyperlinkedModelSerializer):
    paciente = PacienteSerializer()

    class Meta:
        model = Voluntario

class TrabalhoSerializer(serializers.HyperlinkedModelSerializer):
    funcao = FuncaoSerializer()
    voluntario = VoluntarioSerializer()

    class Meta:
        model = Trabalho

class FuncaoVoluntarioSerializer(serializers.HyperlinkedModelSerializer):
    funcao = FuncaoSerializer()
    voluntario = VoluntarioSerializer()

    class Meta:
        model = FuncaoVoluntario

class AgendaTrabalhoSerializer(serializers.HyperlinkedModelSerializer):
    voluntario = VoluntarioSerializer()

    class Meta:
        model = AgendaTrabalho
