#-*- coding: utf-8 -*-

import csv
from datetime import *

from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from iluminare.atendimento.models import *
from iluminare.voluntario.models import *
from django.core.exceptions import MultipleObjectsReturned

import re
from django.utils.encoding import smart_str, smart_unicode

dir_log = "/media/DATA/Iluminare/relatorios/"


def gera_csv(lista_rotulos, lista, nome_arquivo_csv):
    
    spamWriter = csv.writer(open(dir_log+nome_arquivo_csv, 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamWriter.writerow(lista_rotulos)
    
    for item in lista:
        spamWriter.writerow(item)

def retorna_dia_semana(data):

    dia_semana_int = data.weekday()
    dia_semana_str = ""
    if dia_semana_int == 0:
        dia_semana_str = "Segunda"
    elif dia_semana_int == 1:
        dia_semana_str = "Terça"
    elif dia_semana_int == 2:
        dia_semana_str = "Quarta"
    elif dia_semana_int == 3:
        dia_semana_str = "Quinta"
    elif dia_semana_int == 4:
        dia_semana_str = "Sexta"
    elif dia_semana_int == 5:
        dia_semana_str = "Sábado"
    elif dia_semana_int == 6:
        dia_semana_str = "Domingo"

    return dia_semana_str



def relatorio_trabalhos():
    ts = Trabalho.objects.all()
    
    lista_rotulos = ["Id Trabalho", #1
                    "Voluntário", #2
                    "Data", #3
                    "Dia semana", #4
                    "Mes", #5
                    "Ano", #6
                    "Hora inicio", #7
                    "Hora final", #8
                    "Ativo" #9
                    ]

    lista_retorno = []
    for t in ts:
        lista = []
        lista.append(t.id) #1
        print t.id
        lista.append(smart_str(t.voluntario.paciente.nome)) #2
        lista.append(t.data) #3
        dia_semana_str = retorna_dia_semana(t.data)
        lista.append(smart_str(dia_semana_str)) #4
        lista.append(t.data.month) #5
        lista.append(t.data.year) #6
        lista.append(t.hora_inicio) #7
        lista.append(t.hora_final) #8
        
        ativo = t.voluntario.ativo
        if ativo:
            lista.append("S") #9
        else:
            lista.append("N") #9
        
        lista_retorno.append(lista)
        
    gera_csv(lista_rotulos, lista_retorno, "relatorio_trabalhos.csv")


def relatorio_atendimentos_basico():
    ats = Atendimento.objects.all()
    # 17 campos
    lista_rotulos = ["Id Atendimento", #1
                    "Nome Paciente", #2
                    "Sexo", #3
                    "Tratamento", #4
                    "Tratamento dia", #5
                    "Data", #6
                    "Hora chegada",#7
                    "Status atendimento", #8
                    "Voluntario", #9
                    "Prioridade", #10
                    "Tipo Prioridade", #11
                    "Prioridade no dia", #12
                    "Observacao", #13
                    "Observacao Prioridade", #14
                    "Mes", #15
                    "Ano", #16
                    "Dia semana"] #17
    
    lista_retorno = []
    for at in ats:
        lista = []
        lista.append(at.id) #1
        print at.id
        lista.append(smart_str(at.paciente.nome)) #2
        if at.paciente.sexo: 
            lista.append(at.paciente.sexo) #3
        else:
            lista.append("")
        tps = TratamentoPaciente.objects.filter(paciente = at.paciente) 
        if tps: 
            lista.append(smart_str(tps[0].tratamento.descricao_basica)) #4
        else:
            lista.append("")
        lista.append(smart_str(at.instancia_tratamento.tratamento.descricao_basica)) #5
        lista.append(at.instancia_tratamento.data) #6
        lista.append(at.hora_chegada) #7
        lista.append(at.status) #8
        vols = Voluntario.objects.filter(paciente = at.paciente, ativo = True)
        if vols:
            lista.append(vols[0].tipo) #9
        else:
            lista.append("")
        dtps = DetalhePrioridade.objects.filter(paciente = at.paciente)
        if len(dtps) > 0:
            lista.append("P") #10
            lista.append(dtps[0].tipo) # 11
        else:
            lista.append("N")
            lista.append("")
        if at.prioridade:
            lista.append("P") #12
        else:
            lista.append("N")
        lista.append(smart_str(at.observacao)) #13
        lista.append(smart_str(at.observacao_prioridade)) #14
        lista.append(at.instancia_tratamento.data.month) #15
        lista.append(at.instancia_tratamento.data.year) #16

        dia_semana_str = retorna_dia_semana(at.instancia_tratamento.data)
        lista.append(smart_str(dia_semana_str)) #17
        
        lista_retorno.append(lista)
        
    gera_csv(lista_rotulos, lista_retorno, "relatorio_geral_atendimentos.csv")
        

def retorna_tratamentos_trabalhadores():
    ats = Atendimento.objects.raw("""
        select at.id, p.nome, it.data, t.descricao_basica from atendimento_atendimento at
            join paciente_paciente p
	            on p.id = at.paciente_id
            join voluntario_voluntario v
	            on v.paciente_id = p.id
            join tratamento_instanciatratamento it 
	            on at.instancia_tratamento_id = it.id
            join tratamento_tratamento t
	            on t.id = it.tratamento_id
            where v.ativo = True and (it.data = '2011-09-01' or it.data = '2011-09-08' or it.data = '2011-09-15' or it.data = '2011-09-22' or 
	            it.data = '2011-09-29' or it.data = '2011-10-06' or it.data = '2011-10-13' or it.data = '2011-10-20' or 
	            it.data = '2011-10-27')
            order by p.nome, it.data;    
    """)
    
    lista_rotulos = ["Nome", "Data", "Tratamento"]
    
    # lista de listas 
    lista_retorno = []
    
    for at in ats:
        lista = []
        lista.append(smart_str(at.paciente.nome))
        lista.append(at.instancia_tratamento.data)
        lista.append(at.instancia_tratamento.tratamento.descricao_basica)
        lista_retorno.append(lista)
    
    gera_csv(lista_rotulos, lista_retorno, "consulta_tratamentos_trabalhadores.csv")


def retorna_trabalhos_trabalhadores():
    ts = Trabalho.objects.raw("""
        select tr.id, p.nome, tr.data, tr.hora_inicio, tr.hora_final from voluntario_trabalho tr
            join voluntario_voluntario v on v.id = tr.voluntario_id
            join paciente_paciente p on p.id = v.paciente_id;    
    """)
    
    spamWriter = csv.writer(open(dir_log+"consulta2.csv", 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamWriter.writerow(["Id", "Nome", "Data", "Dia semana" , "Hora Inicio", "Hora Final"])
    
    for t in ts:
        lista = []
        lista.append(t.id)
        lista.append(smart_str(t.voluntario.paciente.nome))
        lista.append(t.data)
        dia_semana_int = t.data.weekday()
        dia_semana_str = ""
        if dia_semana_int == 0:
            dia_semana_str = "Segunda"
        elif dia_semana_int == 1:
            dia_semana_str = "Terça"
        elif dia_semana_int == 2:
            dia_semana_str = "Quarta"
        elif dia_semana_int == 3:
            dia_semana_str = "Quinta"
        elif dia_semana_int == 4:
            dia_semana_str = "Sexta"
        elif dia_semana_int == 5:
            dia_semana_str = "Sábado"
        elif dia_semana_int == 6:
            dia_semana_str = "Domingo"
        lista.append(smart_str(dia_semana_str))
        lista.append(t.hora_inicio)
        lista.append(t.hora_final)
        spamWriter.writerow(lista)

