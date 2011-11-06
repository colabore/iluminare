#-*- coding: utf-8 -*-

import csv
from datetime import *

from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from iluminare.atendimento.models import *
from iluminare.voluntario.models import *
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
    if nome1[:3] == nome2[:3]:
        return True
    else:
        return False

def final_parecido(nome1, nome2):
    if nome1[-6:] == nome2[-6:]:
        return True
    else:
        return False


# retorna true se há intersecao entre os atendimentos
def intersecao_atendimentos(id_nome1, id_nome2):
    if id_nome1 == id_nome2:
        return True
    
    paciente1 = Paciente.objects.get(id = id_nome1)
    paciente2 = Paciente.objects.get(id = id_nome2)

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
            comando = "select nome, id, (match(nome) against(\"%s\" IN BOOLEAN MODE)) as score from  paciente_paciente order by score desc;" % nome_principal
            cursor.execute(comando)
            rows = cursor.fetchall()
            lista = []
            i=0
            j=0
            for row in rows:
                if i==3:
                    break;
                nome_local = row[0]
                id_paciente = row[1]
                score = row[2]
                if score >= 3 and nome_principal != nome_local and inicio_parecido(nome_principal, nome_local) and not intersecao_atendimentos(paciente.id, id_paciente): 
                    lista_geral.append(nome_local)
                    arquivo_consolida.write(""+smart_str(nome_local)+"-"+str(id_paciente)+" ; ")
                    j+=1
                
                i+=1
            if j>0:
                lista_geral.append(nome_local)
                arquivo_consolida.write(""+smart_str(nome_principal)+'-'+str(paciente.id)+'\n')
    
    arquivo_consolida.close()
    t1 = datetime.now()
    delta = t1-t0
    print "Duração: "+str(delta)

# JUNTA AS INSTANCIAS TRATAMENTO_PACIENTE EM UM ÚNICO PACIENTE.
def consolida_tratamentos_paciente(id_paciente_consolidado, id_paciente):
    paciente_consolidado = Paciente.objects.get(id = id_paciente_consolidado)
    arquivo_log.write("Paciente consolidado: "+smart_str(""+paciente_consolidado.nome+"\n"))
    
    tps_p = TratamentoPaciente.objects.filter(paciente__id = id_paciente)

    for tp in tps_p:
        tp.delete()
        arquivo_log.write(smart_str("Deletando TP: "+str(tp)+"\n"))
        print smart_str("Deletando TP: "+str(tp)+"\n")
        
# JUNTA AS INSTANCIAS DOS ATENDIMENTOS EM UM ÚNICO PACIENTE.
def consolida_atendimentos(id_paciente_consolidado, id_paciente):
    ats_pc = Atendimento.objects.filter(paciente__id = id_paciente_consolidado)
    ats_p = Atendimento.objects.filter(paciente__id = id_paciente)
    
    for at in ats_p:
        at.paciente = Paciente.objects.get(id = id_paciente_consolidado)
        at.save()
        arquivo_log.write(smart_str("Incluindo atendimento: "+str(at.instancia_tratamento.data)+" - " +at.instancia_tratamento.tratamento.descricao_basica+"\n"))
        print smart_str("Incluindo atendimento: "+str(at.instancia_tratamento.data)+" - " +at.instancia_tratamento.tratamento.descricao_basica+"\n")
        
# RECEBE UMA LISTA DE IDS DE PACIENTES.
# CONSIDERA QUE O PRIMEIRO É O PACIENTE A SER CONSOLIDADO.
# JUNTA OS TRATAMENTOS_PACIENTE E OS ATENDIMENTOS E
# APAGA O PACIENTE.
def consolidar_paciente(lista_ids_pacientes):
    """
        O PRIMEIRO PACIENTE DA LISTA SERÁ O CONSOLIDADO. TODOS OS OUTROS SERÃO EXCLUÍDOS.        
    """
    
    paciente_consolidado = Paciente.objects.get(id = lista_ids_pacientes[0])
    arquivo_log.write(smart_str(paciente_consolidado.nome)+"\n")
    print smart_str(paciente_consolidado.nome)+"\n"
    
    if lista_ids_pacientes > 1:
        for id_paciente in lista_ids_pacientes[1:]:
            paciente = Paciente.objects.get(id = id_paciente)
            arquivo_log.write(smart_str(paciente.nome)+"\n")
            consolida_atendimentos(paciente_consolidado.id, id_paciente)
            #consolida_tratamentos_paciente(paciente_consolidado.id, id_paciente)
            
            vs = Voluntario.objects.filter(paciente = paciente)
            if len(vs) == 1:
                vol = vs[0]
                vol.paciente = paciente_consolidado
                vol.save()
                msg = "Voluntário consolidado: "+smart_str(paciente.nome)+"\n"
                arquivo_log.write(msg)
                print msg
                
            paciente.delete()
            msg = "Paciente excluído: "+ smart_str(paciente.nome)+"\n"
            arquivo_log.write(msg)
            print msg
        
def consolidar_pacientes():
    print "Consolidando pacientes...."
    arquivo_consolida = open(dir_log+"consolida_pacientes_ids_2.csv")
    linhas = file.readlines(arquivo_consolida)
    for linha in linhas:
        linha = linha.split(";")
        ids = [int(i) for i in linha]
        consolidar_paciente(ids)
        arquivo_log.write("---------"+"\n")
    arquivo_consolida.close()

def unifica_tratamentos():
    print "Unificando tratamentos...."
    arquivo_consolida = open(dir_log+"consolida_pacientes_ids_2.csv")
    linhas = file.readlines(arquivo_consolida)
    for linha in linhas:
        linha = linha.split(";")
        id_paciente = int(linha[0])
        paciente = Paciente.objects.get(id = id_paciente)
        tps = TratamentoPaciente.objects.filter(paciente__id = id_paciente)
        print smart_str(paciente.nome) + "  -  " + str(len(tps))
        
        if len(tps) == 2 and tps[0].tratamento ==  tps[1].tratamento:
            tps[1].delete()
        elif len(tps) == 3 and tps[0].tratamento ==  tps[1].tratamento and tps[1].tratamento ==  tps[2].tratamento:
            tps[1].delete()
            tps[2].delete()
        else:
            pass


## executa:

#lista_nomes_possivelmente_errados()
#lista_nomes_possivelmente_iguais()

#consulta_scores()
consolidar_pacientes()
#unifica_tratamentos()

#print str(intersecao_atendimentos("Wilson Soares de Souza Barros","Wilson Soares de Souza"))
#print str(intersecao_atendimentos("Guilherme Barros CorrÊa de Amorim","MarÍlia Barros CorrÊa de Amorim"))


arquivo_log.close()
