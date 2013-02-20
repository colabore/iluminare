# -*- coding: utf-8 -*-

"""

    ARQUIVO COM SCRIPTS UTILIZADOS ISOLADAMENTE EM ALGUNS MOMENTOS
    E QUE PODEM VIR A SER IMPORTANTES POSTERIORMENTE.
    
"""

from iluminare.atendimento.models import *
from iluminare.paciente.models import *
from iluminare.tratamento.models import *
import datetime


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

