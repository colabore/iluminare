# -*- coding: utf-8 -*-

"""

    ARQUIVO COM SCRIPTS UTILIZADOS ISOLADAMENTE EM ALGUNS MOMENTOS
    E QUE PODEM VIR A SER IMPORTANTES POSTERIORMENTE.
    
"""

from iluminare.atendimento.models import *
from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from iluminare.limbo.consultas_gerais import gera_csv
import datetime
from django.utils.encoding import smart_str, smart_unicode


def condicao_paciente_ativo(paciente):
    data_limite = datetime.date.today() - datetime.timedelta(days=180)
    atendimentos = Atendimento.objects.filter(paciente = paciente).order_by('-instancia_tratamento__data')[:1]
    if atendimentos and atendimentos[0].instancia_tratamento.data > data_limite:
        return True
    else:
        return False

def get_pacientes_ativos():
    pacientes = Paciente.objects.all()
    pacientes2 = []
    for p in pacientes:
        if condicao_paciente_ativo(p):
            pacientes2.append(p)
    return pacientes2

def atualiza_notificacoes():
    """
        Script para atualizar as notificações dos pacientes em função das observações registradas.
        Os pacientes inativos terão suas notificações criadas inativas.
        Os pacientes ativos terão suas notificações criadas ativas.
        Precisaremos avaliar qual será a nova função para o campo observacao do paciente.
        Talvez se torne descenecessário.
    """
    pacientes = Paciente.objects.all()
    for p in pacientes:
        if condicao_paciente_ativo(p):
            if p.observacao: 
                notificacao = Notificacao(paciente = p, ativo=True, fixo=True, tela_checkin=True, descricao=p.observacao, \
                    data_criacao=datetime.date.today())
                notificacao.save()
                p.observacao = ''
                p.save()
                print p.nome + ' - ' + 'ativo' + ' - ' + p.observacao
        else:
            if p.observacao: 
                notificacao = Notificacao(paciente = p, ativo=False, fixo=True, tela_checkin=True, descricao=p.observacao, \
                    data_criacao=datetime.date.today())
                notificacao.save()
                p.observacao = ''
                p.save()
                print p.nome + ' - ' + 'inativo' + ' - '

def migra_observacoes_desob():
    """
        Todas as observações que tiverem desob depois do dia 19/11 eu já posso criar os agendamentos para a próxima desob.
    """
    data_base = datetime.datetime(2012, 11, 20).date()
    ats = Atendimento.objects.filter(observacao__icontains='desob', instancia_tratamento__data__gte=data_base)
    desob = Tratamento.objects.get(descricao_basica__startswith='Desob')
    agenda_tratamentos = AgendaTratamento.objects.filter(data=None, tratamento=desob)
    if not agenda_tratamentos:
        agenda_tratamento = AgendaTratamento(tratamento = desob, data=None)
        agenda_tratamento.save()
    else:
        agenda_tratamento = agenda_tratamentos[0]

    for at in ats:
        agenda_atendimento = AgendaAtendimento(paciente = at.paciente, \
            agenda_tratamento = agenda_tratamento, atendimento_origem = at, status = 'A')
        agenda_atendimento.save()
        print at.paciente.nome + ' - ' + str(at.instancia_tratamento.data)

def exibe_notificacoes():
    lista_rotulos = ['id', 'data',smart_str('Notificação'),'Paciente']
    lista_retorno = []
    ns = Notificacao.objects.filter(ativo=True)
    for n in ns:
        lista = [str(n.id), str(n.data_criacao), smart_str(n.descricao), smart_str(n.paciente.nome)]
        lista_retorno.append(lista)
    gera_csv(lista_rotulos, lista_retorno, 'obs.csv')


def ajusta_notificacoes():
    ns = Notificacao.objects.filter(ativo=True)
    for n in ns:
        if ('desob' in n.descricao.lower()) or ('nafme' in n.descricao.lower()):
            n.ativo = False
            n.save()

def ajusta_notificacoes2():
    ns = Notificacao.objects.filter(ativo=True)
    for n in ns:
        if (n.data_criacao == datetime.date(2013,02,20)) and (n.id not in [244, 285, 307,320, 355,389,408,424,526,536,541,542,\
           663,664,693,774,775,776,795,844,865,881,886,893,903,935,954,970,1024,1042,1048,1080,1084,1096,1105,1109,1110,1167,\
           1180,1186,1273,1317,1325,1358,1381,1397]):
            n.ativo = False
            n.save()
