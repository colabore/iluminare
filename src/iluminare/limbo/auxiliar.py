#-*- coding: utf-8 -*-

import csv
from datetime import *

from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from iluminare.atendimento.models import *
from django.core.exceptions import MultipleObjectsReturned

import re
from django.utils.encoding import smart_str, smart_unicode, smart_str

arquivo_log = open("aux.log", "w")

######### FUNCOES AUXILIARES

def lista_nomes_possivelmente_errados():
    lista_pacientes = Paciente.objects.filter()
    print len(lista_pacientes)

    for p in lista_pacientes:
        if len(p.nome) > 45 or len(p.nome) < 15:
            arquivo_log.write(smart_str(p.nome)+'\n')
            ats = Atendimento.objects.filter(paciente = p)
            for at in ats:
                arquivo_log.write(str(at.instancia_tratamento.data)+" "+at.instancia_tratamento.tratamento.descricao_basica+'\n')


def lista_nomes_possivelmente_iguais():
    lista_pacientes = Paciente.objects.filter()
    print len(lista_pacientes)

    for p in lista_pacientes:
        arquivo_log.write(smart_str(p.nome)+'\n')
        lista = compara_str_lista(p,lista_pacientes)
        for i in lista:
            arquivo_log.write("--- "+smart_str(i.nome)+'\n')
    

def compara_str_lista(paciente, lista):
    
    nova_lista = []
    for i in lista:
        if tamanho_parecido(paciente.nome, i.nome) and inicio_parecido(paciente.nome, i.nome) and final_parecido(paciente.nome, i.nome) and \
            paciente.nome != i.nome:
            nova_lista.append(i)
    return nova_lista
            
def tamanho_parecido(nome1, nome2):
    if len(nome1) == len(nome2) or len(nome1) == len(nome2)-1 or len(nome1) == len(nome2)-2 or len(nome1) == len(nome2)+1 or len(nome1) == len(nome2)+2:
        return True
    else:
        return False

def inicio_parecido(nome1, nome2):
    if nome1[:6] == nome2[:6]:
        return True
    else:
        return False

def final_parecido(nome1, nome2):
    if nome1[-6:] == nome2[-6:]:
        return True
    else:
        return False


# retorna true se há intersecao entre os atendimentos
def intersecao_atendimentos(nome1, nome2):
    if nome1 == nome2:
        return True
    
    paciente1 = Paciente.objects.get(nome = nome1)
    paciente2 = Paciente.objects.get(nome = nome2)

    atendimentos1 = Atendimento.objects.filter(paciente=paciente1)
    atendimentos2 = Atendimento.objects.filter(paciente=paciente2)
  
    for at1 in atendimentos1:
        for at2 in atendimentos2:
            data1 = at1.instancia_tratamento.data
            data2 = at2.instancia_tratamento.data
            if data1 == data2:
                return True

    return False
    

def consulta_scores():
    from django.db import connection
    cursor = connection.cursor()

    pacientes = Paciente.objects.all()
    lista_geral = []
    for paciente in pacientes:
        nome_principal = paciente.nome
        
        comando = "select nome, (match(nome) against(\"%s\" IN BOOLEAN MODE)) as score from  paciente_paciente order by score desc;" % nome_principal
        cursor.execute(comando)
        rows = cursor.fetchall()
        lista = []
        i=0
        j=0
        for row in rows:
            if i==3:
                break;
            nome_local = row[0]
            score = row[1]
            if score >= 3 and inicio_parecido(nome_principal, nome_local) and not intersecao_atendimentos(nome_principal, nome_local): 
                arquivo_log.write(""+smart_str(nome_local)+'\n')
                j+=1
            
            i+=1
        if j>0:
            arquivo_log.write("---- "+smart_str(nome_principal)+'\n')

## executa:

#lista_nomes_possivelmente_errados()
#lista_nomes_possivelmente_iguais()

consulta_scores()

#print str(intersecao_atendimentos("Wilson Soares de Souza Barros","Wilson Soares de Souza"))
#print str(intersecao_atendimentos("Guilherme Barros CorrÊa de Amorim","MarÍlia Barros CorrÊa de Amorim"))


arquivo_log.close()
