# coding: utf-8

import re
from datetime import date
from datetime import datetime
from datetime import timedelta

from django.utils.encoding import smart_str

from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from iluminare.atendimento.models import *
from iluminare.voluntario.models import *

class VoluntarioException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message

def ponto_voluntario(paciente, ponto_voluntario_char):
    dic_retorno = {'sucesso':False, 'mensagem':''}
    voluntarios = Voluntario.objects.filter(paciente = paciente, ativo = True)
    voluntario = None
    if len(voluntarios) > 0:
        voluntario = voluntarios[0]
    else:
        dic_retorno['mensagem']="ATENÇÃO! PONTO não efetuado: Paciente não é voluntário da casa."
        return dic_retorno

    funcoes = Funcao.objects.filter(descricao__startswith = "Geral")
    if len(funcoes) == 0:
        funcao = Funcao(descricao = "Geral")
        funcao.save()
    else:
        funcao = funcoes[0]

    if ponto_voluntario_char == 'E':
        trabalhos = Trabalho.objects.filter(voluntario = voluntario, funcao=funcao, data = date.today())
        if len(trabalhos) == 0:
            trabalho = Trabalho(voluntario = voluntario, funcao=funcao, data = date.today(), \
                hora_inicio = datetime.now(), status='PR')
            trabalho.save()
            dic_retorno['mensagem'] = "PONTO DE ENTRADA do voluntário efetuado com SUCESSO."
            dic_retorno['sucesso'] = True
            return dic_retorno
        else:
            dic_retorno['mensagem'] = "ATENÇÃO! PONTO DE ENTRADA do voluntário JÁ REALIZADO."
            return dic_retorno

    if ponto_voluntario_char == 'S':
        trabalhos = Trabalho.objects.filter(voluntario = voluntario, funcao=funcao, data = date.today())
        if len(trabalhos) == 0:
            dic_retorno['mensagem'] = "ATENÇÃO! Ponto de saída não realizado: o ponto de saída só pode \
                ser efetuado após o ponto de entrada."
            return dic_retorno
        else:
            trabalho = trabalhos[0]
            if trabalho.hora_final == None:
                trabalho.hora_final = datetime.now()
                trabalho.save()
                dic_retorno['mensagem'] = "PONTO DE SAÍDA do voluntário efetuado com sucesso."
                dic_retorno['sucesso'] = True
                return dic_retorno
            else:
                dic_retorno['mensagem'] = "ATENÇÃO! PONTO DE SAÍDA do voluntário JÁ REALIZADO."
                return dic_retorno
