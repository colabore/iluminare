
# coding: utf-8

from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from iluminare.atendimento.models import *
from datetime import date
import re, datetime

class AtendimentoException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return repr(self.message)
        
    

def checkin_paciente(paciente, tratamento, senha_str, redirecionar, prioridade_bool, observacao_prioridade_str):
    if redirecionar != None:
        tratamento = redirecionar
    
    hoje = date.today()
    its = InstanciaTratamento.objects.filter(tratamento = tratamento, data = hoje)
    
    if len(its) == 0:
        it =  InstanciaTratamento(tratamento=tratamento, data=hoje)
        it.save()
    elif len(its) == 1:
        it = its[0]
    else:
        raise AtendimentoException("Inconsistência: Mais de um tratamento aberto para a mesma sala no mesmo dia. \
            (Mais de uma InstanciaTratamento para o mesmo tratamento-data)")
    
    at = Atendimento(instancia_tratamento = it, paciente = paciente, prioridade = prioridade_bool, senha = senha_str, \
        observacao_prioridade = observacao_prioridade_str, status = 'C')
    at.save()

