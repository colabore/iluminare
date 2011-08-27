
# coding: utf-8

from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from iluminare.atendimento.models import *
from datetime import date
from datetime import datetime
import re

class AtendimentoException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return repr(self.message)
        
    

def checkin_paciente(paciente, tratamento_paciente, senha_str, redirecionar, prioridade_bool, observacao_prioridade_str):

    if redirecionar == None and tratamento_paciente == None:
        raise AtendimentoException("Favor informar o tratamento.")

    if redirecionar != None:
        tratamento = redirecionar
    else:
        tratamento = tratamento_paciente.tratamento
    
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
    at.hora_chegada=datetime.now()
    at.save()


def atendimentos_paciente(paciente_id):

    ats = []
    try:
        ats = Atendimento.objects.raw("""select a.* from atendimento_atendimento a
            join tratamento_instanciatratamento it
	            on a.instancia_tratamento_id = it.id
            join tratamento_tratamento t
	            on it.tratamento_id = t.id
            where a.paciente_id = %d and a.status = 'A'
            order by data desc;""" % paciente_id)
    except:
        pass
        
    return ats

