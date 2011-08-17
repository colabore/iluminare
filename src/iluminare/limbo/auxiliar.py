#-*- coding: utf-8 -*-

import csv
from datetime import *

from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from iluminare.atendimento.models import *
from django.core.exceptions import MultipleObjectsReturned

import re
from django.utils.encoding import smart_str, smart_unicode, smart_str

dir_log = "/media/DATA/Iluminare/Arquivos locais/carga inicial/"
arquivo_log = open(dir_log+"aux.log", "w")


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
    
    print "Consultado Scores..."
    t0 = datetime.now()
    arquivo_consolida = open(dir_log+"consolida_pacientes.csv", "w")

    from django.db import connection
    cursor = connection.cursor()

    pacientes = Paciente.objects.all()
    lista_geral = []
    for paciente in pacientes:
        nome_principal = paciente.nome
        
        # esse teste garante que os nomes já inseridos na lista não entrem outra vez.
        if nome_principal not in lista_geral:
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
                    lista_geral.append(nome_local)
                    arquivo_consolida.write(""+smart_str(nome_local)+" ; ")
                    j+=1
                
                i+=1
            if j>0:
                lista_geral.append(nome_local)
                arquivo_consolida.write(""+smart_str(nome_principal)+'\n')
    
    arquivo_consolida.close()
    t1 = datetime.now()
    delta = t1-t0
    print "Duração: "+str(delta)

def consolida_tratamentos_paciente(paciente_consolidado, paciente):
    tps_pc = TratamentoPaciente.objects.filter(paciente = paciente_consolidado)
    arquivo_log.write("TPs Paciente consolidado: "+smart_str(""+str(tps_pc)+"\n"))
    tps_p = TratamentoPaciente.objects.filter(paciente = paciente)
    arquivo_log.write("TPs Paciente a consolidar: "+smart_str(""+str(tps_p)+"\n"))
        
    # assumo que se o id é maior, o registro do paciente é posterior ao do paciente consolidado.
    # isso implica que devo considerar que o tratamento mais recente é o do paciente e não do paciente consolidado.
    if paciente.id > paciente_consolidado.id:
        lista_tratamentos_pc = [tp.tratamento for tp in tps_pc]
        lista_tratamentos_p = [tp.tratamento for tp in tps_p]
        
        """
            TPC = [M, 1]
            TP = [M, 2]
        """
        for t in lista_tratamentos_p:
            if t not in lista_tratamentos_pc:
                tp = TratamentoPaciente(paciente = paciente_consolidado, tratamento = t)
                tp.save()
        """
            TPC = [M, 1, 2]

        """            
        for t in lista_tratamentos_pc:
            if t not in lista_tratamentos_p and t.descricao_basica[:4] != "Manu":
                tp = TratamentoPaciente.objects.get(paciente = paciente_consolidado, tratamento = t)
                tp.delete()


        """
            TPC = [M, 2]
        
        """
        tps_pc = TratamentoPaciente.objects.filter(paciente = paciente_consolidado)
        arquivo_log.write("TPs Paciente consolidado: "+smart_str(""+str(tps_pc)+"\n"))

def consolida_atendimentos(paciente_consolidado, paciente):
    ats_pc = Atendimento.objects.filter(paciente = paciente_consolidado)
    ats_p = Atendimento.objects.filter(paciente = paciente)
    
    for at in ats_p:
        at.paciente = paciente_consolidado
        at.save()
        arquivo_log.write(smart_str("Incluindo atendimento: "+str(at.instancia_tratamento.data)+" - " +at.instancia_tratamento.tratamento.descricao_basica+"\n"))
        



def consolidar_paciente(lista_nomes_paciente):
    """
        Recebe uma lista de pacientes que deve ser consolidados em um só.
        Ex: Maria José B. da Silva; Maria José Bastos da Silva
            São a mesma pessoa com registros diferentes na base
        
        - Consolidar os atendimentos
        - Consolidar os tratamentos
        - Consolidar o registro dos pacientes
        
    """
    
    # assumo que só há um paciente com o mesmo nome.
    paciente_consolidado = Paciente.objects.filter(nome = lista_nomes_paciente[0])[0]
    arquivo_log.write(smart_str(lista_nomes_paciente[0])+"\n")
    
    if lista_nomes_paciente > 1:
        for nome_paciente in lista_nomes_paciente[1:]:
            paciente = Paciente.objects.filter(nome = nome_paciente)[0]
            arquivo_log.write(smart_str(paciente.nome)+"\n")
            consolida_tratamentos_paciente(paciente_consolidado, paciente)
            consolida_atendimentos(paciente_consolidado, paciente)
        
        
def consolidar_pacientes():
    print "Consolidando pacientes...."
    arquivo_consolida = open(dir_log+"consolida_pacientes.csv")
    linhas = file.readlines(arquivo_consolida)
    for linha in linhas:
        linha = linha.split(";")
        nomes = [i.replace("\"","").replace("\n","").strip(" ") for i in linha]
        consolidar_paciente(nomes)
        arquivo_log.write("---------"+"\n")
    arquivo_consolida.close()

## executa:

#lista_nomes_possivelmente_errados()
#lista_nomes_possivelmente_iguais()

#consulta_scores()
consolidar_pacientes()

#print str(intersecao_atendimentos("Wilson Soares de Souza Barros","Wilson Soares de Souza"))
#print str(intersecao_atendimentos("Guilherme Barros CorrÊa de Amorim","MarÍlia Barros CorrÊa de Amorim"))


arquivo_log.close()
