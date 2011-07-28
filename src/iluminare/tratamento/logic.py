# coding: utf-8
from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from datetime import date
import re, datetime
from django.db.models import Q

class TratamentoException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return repr(self.message)


def encaminhar_paciente(paciente_id_par, lista_tratamentos_novos):
    """
    Recebe o id de um paciente e uma lista de tratamentos como parâmetro.
    Consulta na base quais são os tratamentos ativos do paciente. 
        - Importante notar que um tratamento está ativo se a data_fim está vazia.
    Caso a lista recebida como parâmetro e os valores ativos na tabela 
        tratamento_paciente foram iguais é sinal que não houve modificações.
    
    """

    try:
        paciente_id_par = int(paciente_id_par)
    except ValueError:
        raise TratamentoException("Erro: Não foi possível encaminhar o paciente. ID inválido: "+ str(paciente_id_par))
    
    # só executa algo se existir um paciente com o id passado    
    if Paciente.objects.filter(id=paciente_id_par).count() == 1:
        # retorna uma lista de TratamentoPaciente ativos
        tratamento_paciente = list(TratamentoPaciente.objects.filter(Q(paciente=paciente_id_par), Q(data_fim = None)))
        tratamentos_atuais = []

        for t in tratamento_paciente:
            tratamentos_atuais.append(t.tratamento)
            
            if t.tratamento not in lista_tratamentos_novos:
                # significa que o tratamento foi concluído, isto é, será removido da lista de tratamentos ativos.
                t.data_fim = date.today()
                t.save()

        for t in lista_tratamentos_novos:
            if t not in tratamentos_atuais:
                # significa que um novo tratamento foi iniciado.
                novoTP = TratamentoPaciente(tratamento_id=t.id, paciente_id=paciente_id_par, data_inicio=date.today(), data_fim=None)
                novoTP.save()            
    else:
        raise TratamentoException("Erro: Não foi possível encaminhar o paciente. Paciente inexistente. ID: "+ str(paciente_id_par))


