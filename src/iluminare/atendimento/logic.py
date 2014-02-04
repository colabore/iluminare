
# coding: utf-8

from    iluminare.paciente.models       import *
from    iluminare.tratamento.models     import *
from    iluminare.atendimento.models    import *
from    iluminare.voluntario.models     import *
from    datetime                        import date, datetime, timedelta
from    django.utils.encoding           import smart_str
from    iluminare.util.logic            import get_data_limite

import  re

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
    if tratamento.id in [1,2,3,4,12]:
        if len(ats) == 0:
            dic_retorno['mensagem']='Paciente sem atendimentos registrados. Deve retornar para as segundas-feiras'
            return dic_retorno
        else:
            # último atendimento na casa há mais de 3 meses
            if ats[0].instancia_tratamento.data < get_data_limite():
                dic_retorno['mensagem']='Último atendimento realizado há mais de 3 meses. Encaminhar paciente para a coordenação.'
                return dic_retorno

    # somente pacientes com agendamento na desobsessão podem fazer checkin.
    if tratamento.id == 8:
        agenda = AgendaAtendimento.objects.filter(paciente = paciente, agenda_tratamento__tratamento = tratamento, \
            status='A')
        if not agenda:
            dic_retorno['mensagem']='Paciente não agendado para a Desobsessão. Favor encaminhá-lo para a coordenação.'
            return dic_retorno

    # regra básica:
    # se o paciente está fazendo um checkin para algum tratamento,
    # será necessário verificar se ele já cumpriu as 4 manutenções.
    # para tal, simplesmente verificamos se o último atendimento foi manutenção ou primeira vez e se
    # nos últimos 180 dias houve 4 manutenções.
    if tratamento.id in [1,2,3,4,5,12]:
        if ats:
            if ats[0].instancia_tratamento.tratamento.descricao_basica[:4] == "Manu" or \
                ats[0].instancia_tratamento.tratamento.descricao_basica[:4] == "Prim":
                data_limite = datetime.today().date() - timedelta(days=180)
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
        tratamento_smart = smart_str(tratamento.descricao_basica)
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
                        % tratamento_smart)
                    dic_retorno['sucesso'] = True
                    dic_retorno['senha'] = senha
                else:
                    
                    dic_retorno['mensagem'] = smart_str("ATENÇÃO! CHECK-IN NÃO REALIZADO (%s): Horário limite de \
                        entrada não atendido." % tratamento_smart)
            else:
                dic_retorno['mensagem'] = smart_str("ATENÇÃO! CHECK-IN NÃO REALIZADO (%s): %s." % 
                    (tratamento_smart, dic_regras['mensagem']))
        else:
            dic_retorno['mensagem'] = smart_str("ATENÇÃO! Check-in do paciente JÁ REALIZADO (%s)." % tratamento_smart)
    else:
        dic_retorno['mensagem'] = smart_str("CHECK-IN não realizado. Tratamento não informado.")

    return dic_retorno

