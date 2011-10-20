
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
        
    

def ponto_voluntario(paciente, ponto_voluntario_char):
        
    voluntarios = Voluntario.objects.filter(paciente = paciente, ativo = True)
    voluntario = None
    if len(voluntarios) > 0:
        voluntario = voluntarios[0]
    else:
        return "ATENÇÃO! PONTO não efetuado: Paciente não é voluntário da casa."
    
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
            return "PONTO DE ENTRADA do voluntário efetuado com SUCESSO."
        else:
            return "ATENÇÃO! PONTO DE ENTRADA do voluntário JÁ REALIZADO."
    
    if ponto_voluntario_char == 'S':
        trabalhos = Trabalho.objects.filter(voluntario = voluntario, funcao=funcao, data = date.today())
        if len(trabalhos) == 0:
            return "ATENÇÃO! Ponto de saída não realizado: o ponto de saída só pode ser efetuado após o ponto de entrada."
        else:
            trabalho = trabalhos[0]
            if trabalho.hora_final == None:
                trabalho.hora_final = datetime.now()
                trabalho.save()
                return "PONTO DE SAÍDA do voluntário efetuado com sucesso."
            else:
                return "ATENÇÃO! PONTO DE SAÍDA do voluntário JÁ REALIZADO."
    
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

    # último atendimento na casa há mais de 3 meses
    if tratamento.descricao_basica in ['Sala 1', 'Sala 2', 'Sala 3', 'Sala 5']:
        if len(ats) == 0:
            return (False,'Paciente sem atendimentos registrados. Deve retornar para as segundas-feiras')
        else:
            if ats[0].instancia_tratamento.data < datetime.today().date() - timedelta(days=90):
                return (False,'Último atendimento realizado há mais de 3 meses. Deve retornar para as segundas-feiras')    

    # ainda não finalizou as manutenções
    # talvez ainda seja necessário ajustar essa lógica.
    if tratamento.descricao_basica[:4] == 'Sala':
        if len(ats) > 0:
            if ats[0].instancia_tratamento.tratamento.descricao_basica[:4] == "Manu" or \
                ats[0].instancia_tratamento.tratamento.descricao_basica[:4] == "Prim":
                data_limite = datetime.today().date() - timedelta(days=90)
                manuts = Atendimento.objects.filter(paciente = paciente, status='A', \
                    instancia_tratamento__tratamento__descricao_basica__startswith="Manu", \
                    instancia_tratamento__data__gte=data_limite)
                if len(manuts) < 4:
                   return (False,'Paciente ainda não finalizou as manutenções da segunda-feira.')
    
    # caso feliz
    return (True,'')

def checkin_paciente(paciente, tratamento, senha_str, redirecionar, prioridade_bool, \
        observacao_prioridade_str, ponto_voluntario_char, forcar_checkin):

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
            bool_msg = regras_gerais_atendidas(paciente, tratamento)
            if bool_msg[0] or forcar_checkin:
                if horario_autorizado(tratamento) or forcar_checkin:
                    at = Atendimento(instancia_tratamento = it, paciente = paciente, prioridade = prioridade_bool, senha = senha_str, \
                        observacao_prioridade = observacao_prioridade_str, status = 'C')
                    at.hora_chegada=datetime.now()
                    at.save()
                    mensagem_retorno = smart_str("CHECK-IN realizado com SUCESSO!<br/><br/> Paciente: %s <br /> \
                        Tratamento: %s <br/><br/>" % (paciente.nome, at.instancia_tratamento.tratamento.descricao_basica))
                else:
                    mensagem_retorno = smart_str("ATENÇÃO! CHECK-IN NÃO REALIZADO: Horário limite de entrada não atendido.<br/><br/>")
            else:
                mensagem_retorno = smart_str("ATENÇÃO! CHECK-IN NÃO REALIZADO: %s.<br/>" % bool_msg[1])    
        else:
            mensagem_retorno = smart_str("ATENÇÃO! Check-in do paciente JÁ REALIZADO para este tratamento.<br/><br/>")
            
    

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

