
# coding: utf-8

from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from iluminare.atendimento.models import *
from iluminare.voluntario.models import *
from datetime import date
from datetime import datetime
from datetime import timedelta
import re
from django.utils.encoding import smart_str

class AtendimentoException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return self.message
            
def horario_autorizado(tratamento):
    
    if tratamento.horario_limite != None:
        if datetime.now().time() > tratamento.horario_limite:
            return False
        else:
            return True
    else:
        return True

def regras_gerais_atendidas(paciente, tratamento):
    
    ats = Atendimento.objects.filter(paciente = paciente, status='A').order_by('-instancia_tratamento__data')
    dic_retorno = {'sucesso':False, 'mensagem':None}

    # somente os tratamentos nas salas 1, 2, 3 e 4 são verificados, pois qualquer paciente pode fazer check-in na
    # quinta-feira na sala 5.
    if tratamento.descricao_basica in ['Sala 1', 'Sala 2', 'Sala 3', 'Sala 4']:
        if len(ats) == 0:
            dic_retorno['mensagem']='Paciente sem atendimentos registrados. Deve retornar para as segundas-feiras'
            return dic_retorno
        else:
            # último atendimento na casa há mais de 3 meses
            # é necessário ajustar esse regra para ficar mais genérica. No caso do início do ano, quando 
            # voltamos de 1 mês e meio de recesso, essa regra precisa ser ajustada.
            if ats[0].instancia_tratamento.data < datetime.today().date() - timedelta(days=90):
                dic_retorno['mensagem']='Último atendimento realizado há mais de 3 meses. Encaminhar paciente para a coordenação.'
                return dic_retorno
        
        


    # ainda não finalizou as manutenções
    # talvez ainda seja necessário ajustar essa lógica.
    if tratamento.descricao_basica[:4] == 'Sala':
        if ats:
            if ats[0].instancia_tratamento.tratamento.descricao_basica[:4] == "Manu" or \
                ats[0].instancia_tratamento.tratamento.descricao_basica[:4] == "Prim":
                data_limite = datetime.today().date() - timedelta(days=90)
                manuts = Atendimento.objects.filter(paciente = paciente, status='A', \
                    instancia_tratamento__tratamento__descricao_basica__startswith="Manu", \
                    instancia_tratamento__data__gte=data_limite)
                if len(manuts) < 4:
                   dic_retorno['mensagem']='Paciente ainda não finalizou as manutenções da segunda-feira.'
                   return dic_retorno
    
    # caso feliz :)
    dic_retorno['sucesso']=True
    return dic_retorno


def proxima_senha(tratamento):
    """
        Retorna um inteiro que representa a próxima senha a ser cadastrada.
        Para um mesmo dia, teremos uma contagem para cada tratamento em andamento..
        
    """
    senha = 0
    ult_at = Atendimento.objects.filter(instancia_tratamento__data = datetime.today().date(), \
        instancia_tratamento__tratamento = tratamento).order_by('-senha')
    if len(ult_at) == 0 or ult_at[0].senha == None:
        senha = 1
    else:
        senha = ult_at[0].senha + 1
    return senha

def checkin_paciente(paciente, tratamento, prioridade_bool, \
        observacao_prioridade_str, forcar_checkin):

    dic_retorno = {'sucesso':False,'mensagem':None, 'senha':0}
    
    if tratamento != None:
    
        hoje = date.today()
        its = InstanciaTratamento.objects.filter(tratamento = tratamento, data = hoje)
        
        if len(its) == 0:
            it =  InstanciaTratamento(tratamento=tratamento, data=hoje)
            it.save()
        elif len(its) == 1:
            it = its[0]
        else:
            dic_retorno['mensagem']="Inconsistência: Mais de um tratamento aberto para a mesma sala no mesmo dia. \
                (Mais de uma InstanciaTratamento para o mesmo tratamento-data)"
            return dic_retorno 
        
        ats = Atendimento.objects.filter(instancia_tratamento = it, paciente = paciente)
        
        if len(ats) == 0:
            dic_regras = regras_gerais_atendidas(paciente, tratamento)
            if dic_regras['sucesso'] or forcar_checkin:
                if horario_autorizado(tratamento) or forcar_checkin:
                    senha = proxima_senha(tratamento)

                    # Verifica se o paciente já é prioridade.
                    # se ele já for prioridade e tiver sido marcada prioridade no dia, 
                    # a prioridade no dia é ignorada.
                    if prioridade_bool:
                        dp = DetalhePrioridade.objects.filter(paciente = paciente)
                        if dp:
                            prioridade_bool = False

                    at = Atendimento(instancia_tratamento = it, paciente = paciente, prioridade = prioridade_bool, \
                        senha = senha, observacao_prioridade = observacao_prioridade_str, status = 'C')
                    at.hora_chegada=datetime.now()
                    at.save()
                    dic_retorno['mensagem'] = smart_str("CHECK-IN realizado com SUCESSO (%s)" \
                        % at.instancia_tratamento.tratamento.descricao_basica)
                    dic_retorno['sucesso'] = True
                    dic_retorno['senha'] = senha
                else:
                    dic_retorno['mensagem'] = smart_str("ATENÇÃO! CHECK-IN NÃO REALIZADO: Horário limite de \
                        entrada não atendido.")
            else:
                dic_retorno['mensagem'] = smart_str("ATENÇÃO! CHECK-IN NÃO REALIZADO: %s." % dic_regras['mensagem'])    
        else:
            dic_retorno['mensagem'] = smart_str("ATENÇÃO! Check-in do paciente JÁ REALIZADO para este tratamento.")
    else:
        dic_retorno['mensagem'] = smart_str("CHECK-IN não realizado.")

    return dic_retorno

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

