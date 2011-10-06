
# coding: utf-8

from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from iluminare.atendimento.models import *
from iluminare.voluntario.models import *
from datetime import date
from datetime import datetime
import re
from django.utils.encoding import smart_str

class AtendimentoException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return self.message
        
    

def ponto_voluntario(paciente, ponto_voluntario_char):
        
    voluntarios = Voluntario.objects.filter(paciente = paciente, ativo = True)
    voluntario = None
    if len(voluntarios) > 0:
        voluntario = voluntarios[0]
    else:
        return "Ponto não efetuado: Paciente não é voluntário da casa."
    
    funcoes = Funcao.objects.filter(descricao__startswith = "Geral")
    if len(funcoes) == 0:
        funcao = Funcao(descricao = "Geral")
        funcao.save()
    else:
        funcao = funcoes[0]
    
    if ponto_voluntario_char == 'E':
        trabalhos = Trabalho.objects.filter(voluntario = voluntario, funcao=funcao, data = date.today())
        if len(trabalhos) == 0:
            trabalho = Trabalho(voluntario = voluntario, funcao=funcao, data = date.today(), hora_inicio = datetime.now())
            trabalho.save()
            return "Ponto de entrada do voluntário efetuado com sucesso."
        else:
            return "Ponto de entrada do voluntário já realizado."
    
    if ponto_voluntario_char == 'S':
        trabalhos = Trabalho.objects.filter(voluntario = voluntario, funcao=funcao, data = date.today())
        if len(trabalhos) == 0:
            return "Ponto de saída não realizado: o ponto de saída só pode ser efetuado depois do ponto de entrada."
        else:
            trabalho = trabalhos[0]
            trabalho.hora_final = datetime.now()
            trabalho.save()
            return "Ponto de saída do voluntário efetuado com sucesso."
    
    

def checkin_paciente(paciente, tratamento, senha_str, redirecionar, prioridade_bool, observacao_prioridade_str, ponto_voluntario_char):

    if redirecionar == None and tratamento == None and ponto_voluntario_char == 'N':
        return "Favor informar o tratamento ou confirmar o ponto do voluntário"

    if ponto_voluntario_char == 'S' and (redirecionar != None or tratamento != None):
        return "Operação não realizada: Para efetuar o ponto de saída do voluntário é necessário que \
            todos os outros campos estejam vazios"

    mensagem_retorno = ""
    
    if redirecionar != None or tratamento != None:

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
            return "Inconsistência: Mais de um tratamento aberto para a mesma sala no mesmo dia. \
                (Mais de uma InstanciaTratamento para o mesmo tratamento-data)"
        
        ats = Atendimento.objects.filter(instancia_tratamento = it, paciente = paciente)
        
        if len(ats) == 0:
            at = Atendimento(instancia_tratamento = it, paciente = paciente, prioridade = prioridade_bool, senha = senha_str, \
                observacao_prioridade = observacao_prioridade_str, status = 'C')
            at.hora_chegada=datetime.now()
            at.save()
            mensagem_retorno = smart_str("O check-in realizado com sucesso!<br/> Paciente: %s <br /> Tratamento: %s <br/>" % (paciente.nome, \
                at.instancia_tratamento.tratamento.descricao_basica))
        else:
            mensagem_retorno = "Check-in do paciente já realizado para este tratamento.<br/>"
    

    if ponto_voluntario_char != 'N':
        mensagem_retorno = mensagem_retorno + ponto_voluntario(paciente, ponto_voluntario_char)
        
    return mensagem_retorno




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

