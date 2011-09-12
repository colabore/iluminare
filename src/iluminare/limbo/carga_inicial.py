
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

dir_log = "/media/DATA/Iluminare/Arquivos locais/carga inicial/"
arquivo_log = open(dir_log+"carga.log", "w")

t0 = datetime.now()



dir_csvs = "/media/DATA/Iluminare/Arquivos locais/carga inicial/planilhas/"

"""
Este módulo implementa a carga inicial da base de dados do Iluminare.

Os PARAMETROS de entrada para a realizacão da carga são os arquivos no formato CSV, gerados a partir dos dados originais em XLS.
Cada arquivo CSV traz uma lista com os nomes dos pacientes e a presenca de cada um deles nos dias de tratamento. 
Temos um arquivo por sala de tratamento para cada 2 meses. Por exemplo, para a sala 5 em 2010, temos fev-mar, abr-mai, jun-jul, ago-set, out-nov e dez. Lembrar que não temos atividades em janeiro.
Para 2011, já temos fev-mar, abr-mai. 8 arquivos para cada sala. Como temos 5 salas de tratamento, teremos 40 arquivos como entrada.
O formato padrão para os arquivos é:
QL_<sala>_<ano>_<mes>.csv - onde mês representa, um bimestre ou dez.
Exemplo:
QL_sala5_2010_fev-mar.csv
QL_sala2_2010_dez.csv



AINDA PRECISAM SER TRATADOS OS SEGUINTES CASOS:
- Pessoas que por estarem nas listas de trabalhadores e pacientes estão com atendimentos repetidos (Ex: Helena 
"""




# retorna matriz com todas as linhas lidas no arquivo
def le_arquivo(nome_arquivo, primeira_linha_valida):
    file = open(nome_arquivo)
    linhas = file.readlines()
    linhas = linhas[(primeira_linha_valida-1):]
    matriz = []
    for linha in linhas:
        linha1 = linha.split(";")
        linha1 = [i.replace("\"","").replace("\n","") for i in linha1]
        if linha1[1] != '':
            matriz.append(linha1)
    return matriz
    
   
        
# Retorna o nome da pessoa com a primeira letra maiúscula
# Excecão para palavras com 1 letra, 'da' e 'de'.
# Evita que tenhamos João Da Silva ou João E Silva
def letra_maiuscula(nome):
    if len(nome) == 0:
        return ""
    if len(nome) == 1:
        return nome.lower()
    elif nome.lower() == 'da':
        return nome.lower()
    elif nome.lower() == 'de':
        return nome.lower()
    elif nome.lower() == 'do':
        return nome.lower()
    elif nome.lower() == 'dos':
        return nome.lower()
    elif len(nome) >= 2:
        nome = nome.capitalize()
        primeira_letra = nome[0]
        resto_nome = nome[1:].replace("Ã","ã").\
            replace("Á","á").replace("Ç","ç").\
            replace("É","é").replace("Ô","ô").\
            replace("Ó","ó").replace("Ê","ê").\
            replace("Ú","ú").replace("Í","í")
        return primeira_letra + resto_nome
    else:
        return nome

# recebe como parêmetro um nome completo uppercase.
# retorna o nome da pessoa somente com as primeiras letras maiúsculas
# Ex: JOÃO DA SILVA -> João da Silva
def primeira_letra_maiuscula(nome):
    lista = nome.split(' ')
    # para cada item na lista, põe a primeira letra maiúscula
    lista2 = [letra_maiuscula(c) for c in lista]
    nome = ' '.join(lista2)
    return nome
             

def atualiza_tratamento(paciente, instancia_tratamento_novo):
    """
    Verifica se o paciente tem um tratamento ativo. Se não, cria.
    Verifica se o o novo tratamento é diferente do anterior. Caso positivo,
        encerra o tratamento anterior e inicia o próximo.
    
    """     
    tps = TratamentoPaciente.objects.filter(paciente=paciente.id)
    if len(tps) == 0:
        novo_tp = TratamentoPaciente(paciente=paciente, tratamento=instancia_tratamento_novo.tratamento, data_inicio=instancia_tratamento_novo.data)
        novo_tp.save()
    else:
        # assumindo que o último tratamento paciente é o último da lista.
        tp_antigo = tps[len(tps)-1]
        if (instancia_tratamento_novo.tratamento.descricao_basica != tp_antigo.tratamento.descricao_basica):
            tp_antigo.data_fim = instancia_tratamento_novo.data
            tp_antigo.save()
            novo_tp = TratamentoPaciente(paciente=paciente, tratamento=instancia_tratamento_novo.tratamento, data_inicio=instancia_tratamento_novo.data)
            novo_tp.save()
            arquivo_log.write("** MUDANCA DE TRATAMENTO: paciente: "+str(paciente.id)+"Data: "+str(instancia_tratamento_novo.data)+ \
                "Trat antigo: "+tp_antigo.tratamento.descricao_basica+"Trat novo: "+instancia_tratamento_novo.tratamento.descricao_basica+'\n')



def inclui_tratamento(paciente, tratamento_str):
    """
    Para a carga da base, todos os pacientes só terão 1 tratamento carregado.
    A única exceção é com a manutenção. Neste caso, o paciente poderá ter 2 tratamentos ativos na base.
    Ex: [Sala 1, Manutenção] ou [Sala 2, Manutenção] ou [Manutenção]
    """

    tps = TratamentoPaciente.objects.filter(paciente=paciente.id)
    lista_tratamentos = [tp.tratamento for tp in tps]
    tratamento = Tratamento.objects.get(descricao_basica = tratamento_str)
    
    if len(tps) == 0:
        novo_tp = TratamentoPaciente(paciente=paciente, tratamento=tratamento, status='A')
        novo_tp.save()
    else:
        if tratamento_str == "Manutenção":
            if tratamento not in lista_tratamentos:
                novo_tp = TratamentoPaciente(paciente=paciente, tratamento=tratamento, status='A')
                novo_tp.save()
        else:
            for tp in tps:
                if tp.tratamento.descricao_basica[:4] == "Sala":
                    tp.tratamento = tratamento
                    tp.save()
                
        

def processa_arquivo(nome_arquivo, tratamento_str, lista_data_posicao, ficha):
    """
    ficha: indica a coluna no csv onde esta informação está armazenada. -1 indica que não trataremos esse caso.
    
    PACIENTES COM NOMES IGUAIS:
        MARIA DAS DORES SILVA (06/08/1964)
        MARIA DAS DORES DA SILVA (16/04/1966)
        MARIA JOSE DA SILVA (09-03-1963)
        MARIA JOSE DA SILVA (28-11-1964)
        Estou deixando os nomes dos pacientes com as datas de nascimento. Quando o sistema estiver em produção fazemos o ajuste, 
        migrando a data de nascimento para o campo correto.
        Ajuste os EXCEL para que as pacientes venham com o nome exatamente como apresentado acima.

    NÃO ESTAMOS TRATANDO AINDA A POSSIBILIDADE DE TERMOS O MESMO PACIENTE COM NOMES DIFERENTES NAS TABELAS.                
        
    """
    arquivo_log.write(nome_arquivo+'\n')
    arquivo_log.write(tratamento_str+'\n')
    print "Processando arquivo: "+nome_arquivo

    # cria instancias de tratamento para cada data 

    try:
        lista_instancias = []
        tratamento = Tratamento.objects.get(descricao_basica=tratamento_str)
        for i in lista_data_posicao:

            its = InstanciaTratamento.objects.filter(tratamento=tratamento, data=i[0])
            if len(its) == 0:
                it =  InstanciaTratamento(tratamento=tratamento, data=i[0])
                it.save()
            else:
                it = its[0]

            tupla = (i[0], i[1], it)
            lista_instancias.append(tupla)
    except MultipleObjectsReturned:
        print "Erro: mais de um tratamento com mesmo nome: " + tratamento_str        

    leitor = le_arquivo(nome_arquivo, 4)

    for linha in leitor:
        nome_cru = linha[1]
        nome_sem_ast = nome_cru.split("*")[0]
        nome = nome_sem_ast.strip(" ")
        nome = primeira_letra_maiuscula(nome)

        
        # como somente os arquivos mais novos, a partir de dezembro de 2010, trazem 
        # a informação referente à ficha, criamos a variável ficha, que recebe o valor -1 para
        # os casos em que não há essa informação na planilha. 
        # Quando a infomração estiver disponível, o parâmetro ficha informará a coluna em que se encontra (a partir de zero).
        tem_ficha = False
        if ficha != -1:
            tem_ficha_str = linha[ficha]
            if tem_ficha_str.lower() == 'sim':
                tem_ficha = True
        
        # Verificar se o cliente já está na base
        # por enquanto vamos simplificar, assumindo que todos os clientes têm nomes diferentes e que 
        # não há diferenças entre os nomes dos pacientes entre os arquivos.
        arquivo_log.write(nome+'\n')
        if nome != "":
            pacientes = Paciente.objects.filter(nome=nome)
            if len(pacientes) == 0:
                paciente = Paciente(nome=nome)
                arquivo_log.write("Adicionado"+"\n")
            
            if len(pacientes) == 1:
                paciente = pacientes[0]
            
            if len(pacientes) > 1:
                # DA FORMA COMO FOI ESCRITO NÃO HÁ NENHUM CASO.
                paciente = pacientes[0]
                arquivo_log.write('*** ERRO: MAIS DE UM PACIENTE COM MESMO NOME: '+str(paciente.id)+'\n')

            # INCLUSÃO DO PACIENTE
            paciente.tem_ficha = tem_ficha
            paciente.save()

            # INCLUSÃO DO TRATAMENTO
            inclui_tratamento(paciente, tratamento_str)

            # INCLUSÃO DOS ATENDIMENTOS
            for t in lista_instancias:
                if linha[t[1]] == 'P' or linha[t[1]] == 'p' or linha[t[1]] == 'p\n' or linha[t[1]] == 'P\n':
                    """
                    if paciente.tratamento != tratamento:
                        concluir o tratamento atual e abrir o novo tratamento.
                        
                    """
                    # não estou mais utilizando a atualiza_paciente. Simplificamos o processo.
                    # Cada paciente agora só terá registrado o último tratamento.
                    # atualiza_tratamento(paciente, t[2])                        
                    atendimento = Atendimento(paciente = paciente, instancia_tratamento = t[2], status='A')
                    atendimento.save()
                    arquivo_log.write(str(t[2].data)+'\n')
    
    arquivo_log.write('Encerrando arquivo: '+nome_arquivo+'\n')    


def string_to_date(data_str):
    """
        recebe uma string no formato "DD-MM-AA" ou "DD/MM/AA"
        retorna o objeto do tipo date correspondente.
    """
    lista = []
    if "/" in data_str:
        lista = data_str.split("/")
    elif "-" in data_str:    
        lista = data_str.split("-")
    dia = int(lista[0])
    mes = int(lista[1])
    ano = int(lista[2])+2000
    
    return date(ano, mes, dia)

def registra_atendimento(paciente, tratamento, data):
    """
        registra um novo atendimento para o paciente em uma data para um tratamento.
        caso não haja uma instancia_tratamento correspondente, cria-se.
    """
    
    its = InstanciaTratamento.objects.filter(tratamento=tratamento, data=data)
    
    if len(its) == 0:
        it = InstanciaTratamento(tratamento=tratamento, data=data)
        it.save()
    else:
        it = its[0]
    
    ats = Atendimento.objects.filter(paciente = paciente, instancia_tratamento=it)
    if len(ats) == 0:
        at = Atendimento(paciente = paciente, instancia_tratamento=it, status='A')
        at.save()


def processa_manutencao(nome_arquivo):

    arquivo_log.write("--- Manutencoes: "+nome_arquivo+'\n')
    print "--- Manutencoes: "+nome_arquivo
    
    leitor = le_arquivo(nome_arquivo, 4)

    c_n = 1 # coluna nome
    c_t = 2 # coluna tratamento
    c_1 = 3 # coluna 1a vez
    c_f = 4 # coluna frequencia
    c_o = 5 # coluna obs (c/ficha ou s/ficha)
    
            
    for linha in leitor:
    
        ## NOME CORRETO
        nome_cru = linha[c_n]
        nome_sem_ast = nome_cru.split("*")[0]
        nome = nome_sem_ast.strip(" ")
        nome = primeira_letra_maiuscula(nome)
        
        arquivo_log.write(nome+"\n")
        
        ## PACIENTE
        tem_ficha = False
        if linha[c_o].lower == 'cf':
            tem_ficha = True
            
        pacientes = Paciente.objects.filter(nome = nome) # pode retornar mais de um paciente.
        if len(pacientes) == 0:
            paciente = Paciente(nome = nome)
            arquivo_log.write("Adicionado"+"\n")
        elif len(pacientes) == 1:
            paciente = pacientes[0]
        else:
            arquivo_log.write("*** ERRO: MAIS DE UM TRABALHADOR(PACIENTE) COM MESMO NOME:"+nome+'\n')
        
        paciente.tem_ficha = tem_ficha
        paciente.save()


        ## TRATAMENTO + TRATAMENTO_PACIENTE
        if linha[c_t].strip(" ") in [str(i+1) for i in range(5)]:
            tratamento_str = "Sala "+linha[c_t].strip(" ")
            tratamento = Tratamento.objects.get(descricao_basica = tratamento_str)
            inclui_tratamento(paciente, tratamento_str)

        elif linha[c_t].strip(" ").lower()[:4] == "manu":
            tratamento_str = "Manutenção"
            tratamento = Tratamento.objects.get(descricao_basica = tratamento_str)
            inclui_tratamento(paciente, tratamento_str)
            
        
        ## 1a VEZ
        # assumindo que as datas vêm no formado: DD-MM-AA ou DD/MM/AA
        data_str = linha[c_1].strip(" ")
        tratamentopvez = Tratamento.objects.get(descricao_basica="Primeira vez")
        if data_str != "":
            data = string_to_date(data_str)
            registra_atendimento(paciente, tratamentopvez, data)

        ## ATENDIMENTOS MANUTENÇÃO
        ## COLUNA 6 PRA FRENTE.
        for data_str in linha[6:]:
            manutencao = Tratamento.objects.get(descricao_basica="Manutenção")
            if data_str != "":
                data = string_to_date(data_str)
                registra_atendimento(paciente, manutencao, data)
                   
        

def processa_arquivo_tratamento_voluntarios(nome_arquivo, lista_data_posicao, primeira_linha):
    """
    Para cada linha
        - Inserir o paciente (trabalhador).
        - Informar o tratamento do trabalhador (vamos, inicialmente, ignorar as mudanças que podem ter havido
            incluindo somente o tratamento indicado na coluna C).
        Para cada coluna:
            - Carregar a instancia_tratamento (dia, tratamento) ou criá-la
            - Criar registro na tabela atendimento para cada presença do paciente(trabalhador)
    
   
    """
    arquivo_log.write("--- Tratamentos Trabalhadores e Colabores: "+nome_arquivo+'\n')
    print "--- Tratamentos Trabalhadores e Colabores: "+nome_arquivo
    
    leitor = le_arquivo(nome_arquivo, primeira_linha)
    c_n = 1 # coluna nome
    c_t = 2 # coluna tratamento

    
        
            
    for linha in leitor:
        nome_cru = linha[c_n]
        nome_sem_ast = nome_cru.split("*")[0]
        nome = nome_sem_ast.strip(" ")
        nome = primeira_letra_maiuscula(nome)
        
        arquivo_log.write(nome+"\n")
        
        pacientes = Paciente.objects.filter(nome = nome) # pode retornar mais de um paciente.
        if len(pacientes) == 0:
            paciente = Paciente(nome = nome)
            paciente.save()
            arquivo_log.write("Adicionado"+"\n")
        elif len(pacientes) == 1:
            paciente = pacientes[0]
        else:
            arquivo_log.write("*** ERRO: MAIS DE UM TRABALHADOR(PACIENTE) COM MESMO NOME:"+nome+'\n')

        voluntarios = Voluntario.objects.filter(paciente  = paciente)
        if len(voluntarios) == 0:
            voluntario = Voluntario(paciente = paciente)
            voluntario.save()
            arquivo_log.write("Adicionado Voluntário: "+"\n")

        if linha[c_t] != "": 
            tratamento_str = "Sala "+linha[c_t]
            

            # pode levantar exceção.. Não está sendo tratada.
            tratamento = Tratamento.objects.get(descricao_basica = tratamento_str)
            
            tps = TratamentoPaciente.objects.filter(paciente=paciente)
            if len(tps)==0:
                tp = TratamentoPaciente(paciente=paciente, tratamento=tratamento, status='A')
                tp.save()
            elif len(tps)==1:
                tp = tps[0]
                tp.tratamento = tratamento
                tp.save()
            else:
                arquivo_log.write("*** ERRO: MAIS DE UM TRATAMENTO EM PARALELO:"+nome+" Tratamento: "+tratamento.descricao_basica+'\n')
            
            
        
        # estamos ignorando as datas de início e fim dos tratamentos dos voluntários.. 
        # Preciso incluir esse aspecto ainda.. 
        #novo_tp = TratamentoPaciente(paciente=paciente, tratamento=tratamento)
        #novo_tp.save()
        
        for item in lista_data_posicao:
            
            data = item[0]
            pos = item[1]
            if linha[pos] in [str(i+1) for i in range(5)] or len(linha[pos]) > 1:
                lista = linha[pos].split(',')
                if len(lista) > 1: 
                    arquivo_log.write("*** MAIS DE UM ATENDIMENTO NO MESMO DIA: "+tratamento.descricao_basica+" "+str(data)+"\n")
                for i in lista:
                    tratamento = Tratamento.objects.get(descricao_basica='Sala '+i)
                    its = InstanciaTratamento.objects.filter(tratamento=tratamento, data=data)
                    if len(its) == 0:
                        it =  InstanciaTratamento(tratamento=tratamento, data=data)
                        it.save()
                    elif len(its)==1:
                        it = its[0]
                    else:
                        arquivo_log.write("*** ERRO: MAIS DE UMA INSTANCIA_TRATAMENTO: "+tratamento.descricao_basica+" "+str(data)+"\n")
                    atendimento = Atendimento(paciente = paciente, instancia_tratamento = it, status='A')
                    atendimento.save()
                    arquivo_log.write(str(data)+'\n')

def cria_salas_tratamentos():

    tratamentos = [
        "Sala 1",
        "Sala 2",
        "Sala 3",
        "Sala 4",
        "Sala 5",
        "Primeira vez",
        "Manutenção",
        "Desobsessão",
        "Atendimento Fraterno",
        "Acolhimento Espiritual"]
    for t in tratamentos:
        try:
            tratamento = Tratamento.objects.get(descricao_basica=t)
        except Tratamento.DoesNotExist:
            tratamento = Tratamento(descricao_basica=t)
            tratamento.save()

def processa_manutencoes():
    
    lista_arquivos = [
        "Manut-1avez-2010-12.csv",
        "Manut-1avez-2011-02.csv",
        "Manut-1avez-2011-03.csv",
        "Manut-1avez-2011-04.csv",
        "Manut-1avez-2011-05.csv",
        "Manut-1avez-2011-06.csv",
        "Manut-1avez-2011-07.csv",
        "Manut-1avez-2011-08.csv",
        "Manut-1avez-2011-09.csv"        
        ]

    for arq in lista_arquivos:
        nome_arquivo = dir_csvs + arq
        processa_manutencao(nome_arquivo)

def processa_atendimentos_voluntarios():
    
    ######### ANO 2010
    nome_arquivo = dir_csvs + "Trabalhadores-2010-Tratamentos.csv"
    lista_datas = [
        date(2010,2,4),
        date(2010,2,11),
        date(2010,2,18),
        date(2010,2,25),
        date(2010,3,4),
        date(2010,3,11),
        date(2010,3,18),
        date(2010,3,25),
        date(2010,4,1),
        date(2010,4,8),
        date(2010,4,15),
        date(2010,4,22),
        date(2010,4,29),
        date(2010,5,6),
        date(2010,5,13),
        date(2010,5,20),
        date(2010,5,27),
        date(2010,6,3),
        date(2010,6,10),
        date(2010,6,17),
        date(2010,6,24),
        date(2010,7,1),
        date(2010,7,8),
        date(2010,7,15),
        date(2010,7,22),
        date(2010,7,29),
        date(2010,8,5),
        date(2010,8,12),
        date(2010,8,19),
        date(2010,8,26),
        date(2010,9,2),
        date(2010,9,9),
        date(2010,9,16),
        date(2010,9,23),
        date(2010,9,30),
        date(2010,10,7),
        date(2010,10,14),
        date(2010,10,21),
        date(2010,10,28),
        date(2010,11,4),
        date(2010,11,8),
        date(2010,11,18),
        date(2010,11,25),
        date(2010,12,2),
        date(2010,12,9),
        date(2010,12,16)]
    
    lista_data_posicao = []
    i=3
    for data in lista_datas:
        lista_data_posicao.append((data, i))
        i+=1   
    processa_arquivo_tratamento_voluntarios(nome_arquivo, lista_data_posicao, 7)


    ######## FEV 2011
    nome_arquivo = dir_csvs + "TratamentosTrabalhadores-2011-02.csv"
    lista_data_posicao = [
        (date(2011,2,3),3),
        (date(2011,2,10),4),
        (date(2011,2,17),5),
        (date(2011,2,24),6)]
    processa_arquivo_tratamento_voluntarios(nome_arquivo, lista_data_posicao, 7)
    
    ######## MAR 2011
    nome_arquivo = dir_csvs + "TratamentosTrabalhadores-2011-03.csv"
    lista_data_posicao = [
        (date(2011,3,3),3),
        (date(2011,3,10),4),
        (date(2011,3,17),5),
        (date(2011,3,24),6),
        (date(2011,3,31),7)]
    processa_arquivo_tratamento_voluntarios(nome_arquivo, lista_data_posicao, 7)

    ######## ABR 2011
    nome_arquivo = dir_csvs + "TratamentosTrabalhadores-2011-04.csv"
    lista_data_posicao = [
        (date(2011,4,7),3),
        (date(2011,4,14),4),
        (date(2011,4,21),5),
        (date(2011,4,28),6)]
    processa_arquivo_tratamento_voluntarios(nome_arquivo, lista_data_posicao, 7)

    ######## MAI 2011
    nome_arquivo = dir_csvs + "TratamentosTrabalhadores-2011-05.csv"
    lista_data_posicao = [
        (date(2011,5,5),3),
        (date(2011,5,12),4),
        (date(2011,5,19),5),
        (date(2011,5,26),6)]
    processa_arquivo_tratamento_voluntarios(nome_arquivo, lista_data_posicao, 7)
    
    ######## JUN 2011
    nome_arquivo = dir_csvs + "TratamentosTrabalhadores-2011-06.csv"
    lista_data_posicao = [
        (date(2011,6,2),3),
        (date(2011,6,9),4),
        (date(2011,6,16),5),
        (date(2011,6,23),6),
        (date(2011,6,30),7)]
    processa_arquivo_tratamento_voluntarios(nome_arquivo, lista_data_posicao, 7)

    ######## JUL 2011
    nome_arquivo = dir_csvs + "TratamentosTrabalhadores-2011-07.csv"
    lista_data_posicao = [
        (date(2011,7,7),3),
        (date(2011,7,14),4),
        (date(2011,7,21),5),
        (date(2011,7,28),6)]
    processa_arquivo_tratamento_voluntarios(nome_arquivo, lista_data_posicao, 7)

    ######## AGO 2011
    nome_arquivo = dir_csvs + "TratamentosTrabalhadores-2011-08.csv"
    lista_data_posicao = [
        (date(2011,8,4),3),
        (date(2011,8,11),4),
        (date(2011,8,18),5),
        (date(2011,8,25),6)]
        
    processa_arquivo_tratamento_voluntarios(nome_arquivo, lista_data_posicao, 7)

    ######## SET 2011
    nome_arquivo = dir_csvs + "TratamentosTrabalhadores-2011-09.csv"
    lista_data_posicao = [
        (date(2011,9,1),3),
        (date(2011,9,8),4),
        (date(2011,9,15),5),
        (date(2011,9,22),6),
        (date(2011,9,29),7)]
        
    processa_arquivo_tratamento_voluntarios(nome_arquivo, lista_data_posicao, 7)


    
def processa_atendimentos_quinta():
    """
        PROCESSA OS TRATAMENTOS DOS PACIENTES DAS QUINTAS-FEIRAS.
    """

#### FEVEREIRO E MARÇO 2010

    nome_arquivo_pre = dir_csvs + '2010-02-03-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2010,2,4), 2),
        (date(2010,2,11), 3),
        (date(2010,2,18), 4),
        (date(2010,2,25), 5),
        (date(2010,3,4), 8),
        (date(2010,3,11), 9),
        (date(2010,3,18), 10),
        (date(2010,3,25), 11)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)
    
    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)
    
#### ABRIL E MAIO 2010
    
    nome_arquivo_pre = dir_csvs + '2010-04-05-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2010,4,1), 2),
        (date(2010,4,8), 3),
        (date(2010,4,15), 4),
        (date(2010,4,22), 5),
        (date(2010,4,29), 6),
        (date(2010,5,6), 8),
        (date(2010,5,13), 9),
        (date(2010,5,20), 10),
        (date(2010,5,27), 11)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)


#### JUNHO E JULHO 2010

    nome_arquivo_pre = dir_csvs + '2010-06-07-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2010,6,3), 2),
        (date(2010,6,10), 3),
        (date(2010,6,17), 4),
        (date(2010,6,24), 5),
        (date(2010,7,1), 7),
        (date(2010,7,8), 8),
        (date(2010,7,15), 9),
        (date(2010,7,22), 10),
        (date(2010,7,29), 11)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)


#### AGOSTO E SETEMBRO 2010

    nome_arquivo_pre = dir_csvs + '2010-08-09-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2010,8,5), 2),
        (date(2010,8,12), 3),
        (date(2010,8,19), 4),
        (date(2010,8,26), 5),
        (date(2010,9,2), 7),
        (date(2010,9,9), 8),
        (date(2010,9,16), 9),
        (date(2010,9,23), 10),
        (date(2010,9,30), 11)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

#### OUTUBRO E NOVEMBRO 2010

    nome_arquivo_pre = dir_csvs + '2010-10-11-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2010,10,7), 2),
        (date(2010,10,14), 3),
        (date(2010,10,21), 4),
        (date(2010,10,28), 5),
        (date(2010,11,4), 7),
        (date(2010,11,8), 8),
        (date(2010,11,18), 9),
        (date(2010,11,25), 10)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, -1)


#### DEZEMBRO 2010

    nome_arquivo_pre = dir_csvs + '2010-12-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2010,12,2), 4),
        (date(2010,12,9), 5),
        (date(2010,12,16), 6)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    lista_data_posicao4 = [
        (date(2010,12,2), 5),
        (date(2010,12,9), 6),
        (date(2010,12,16), 7)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao4, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

#### FEVEREIRO 2011

    nome_arquivo_pre = dir_csvs + '2011-02-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2011,2,3), 4),
        (date(2011,2,10), 5),
        (date(2011,2,17), 6),
        (date(2011,2,24), 7)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    lista_data_posicao4 = [
        (date(2011,2,3), 5),
        (date(2011,2,10), 6),
        (date(2011,2,17), 7),
        (date(2011,2,24), 8)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao4, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

#### MARÇO 2011

    nome_arquivo_pre = dir_csvs + '2011-03-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2011,3,3), 4),
        (date(2011,3,10), 5),
        (date(2011,3,17), 6),
        (date(2011,3,24), 7),
        (date(2011,3,31), 8)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    lista_data_posicao4 = [
        (date(2011,3,3), 5),
        (date(2011,3,10), 6),
        (date(2011,3,17), 7),
        (date(2011,3,24), 8),
        (date(2011,3,31), 9)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao4, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

#### ABRIL 2011

    nome_arquivo_pre = dir_csvs + '2011-04-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2011,4,7), 4),
        (date(2011,4,14), 5),
        (date(2011,4,21), 6),
        (date(2011,4,28), 7)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    lista_data_posicao4 = [
        (date(2011,4,7), 5),
        (date(2011,4,14), 6),
        (date(2011,4,21), 7),
        (date(2011,4,28), 8)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao4, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

#### MAIO 2011

    nome_arquivo_pre = dir_csvs + '2011-05-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2011,5,5), 4),
        (date(2011,5,12), 5),
        (date(2011,5,19), 6),
        (date(2011,5,26), 7)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    lista_data_posicao4 = [
        (date(2011,5,5), 5),
        (date(2011,5,12), 6),
        (date(2011,5,19), 7),
        (date(2011,5,26), 8)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao4, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

#### JUNHO 2011

    nome_arquivo_pre = dir_csvs + '2011-06-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2011,6,2), 4),
        (date(2011,6,9), 5),
        (date(2011,6,16), 6),
        (date(2011,6,30), 7)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    lista_data_posicao4 = [
        (date(2011,6,2), 5),
        (date(2011,6,9), 6),
        (date(2011,6,16), 7),
        (date(2011,6,30), 8)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao4, 3)
    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

#### JULHO 2011

    nome_arquivo_pre = dir_csvs + '2011-07-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2011,7,7), 4),
        (date(2011,7,14), 5),
        (date(2011,7,21), 6),
        (date(2011,7,28), 7)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    lista_data_posicao4 = [
        (date(2011,7,7), 5),
        (date(2011,7,14), 6),
        (date(2011,7,21), 7),
        (date(2011,7,28), 8)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao4, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)


#### AGOSTO 2011

    nome_arquivo_pre = dir_csvs + '2011-08-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2011,8,4), 4),
        (date(2011,8,11), 5),
        (date(2011,8,18), 6),
        (date(2011,8,25), 7)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    lista_data_posicao4 = [
        (date(2011,8,4), 5),
        (date(2011,8,11), 6),
        (date(2011,8,18), 7),
        (date(2011,8,25), 8)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao4, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)
        

#### SETEMBRO 2011

    nome_arquivo_pre = dir_csvs + '2011-09-'
    nome_arquivo = nome_arquivo_pre + 'Sala1.csv'
    tratamento = "Sala 1"
    lista_data_posicao = [
        (date(2011,9,1), 4),
        (date(2011,9,8), 5),
        (date(2011,9,15), 6),
        (date(2011,9,22), 7),
        (date(2011,9,29), 8)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala2.csv'
    tratamento = "Sala 2"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala3.csv'
    tratamento = "Sala 3"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala4.csv'
    tratamento = "Sala 4"
    lista_data_posicao4 = [
        (date(2011,9,1), 5),
        (date(2011,9,8), 6),
        (date(2011,9,15), 7),
        (date(2011,9,22), 8),
        (date(2011,9,29), 9)]
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao4, 3)

    nome_arquivo = nome_arquivo_pre + 'Sala5.csv'
    tratamento = "Sala 5"
    processa_arquivo(nome_arquivo, tratamento, lista_data_posicao, 3)
    


def processa():
    # IMPORTANTE: RODAR ESSE MÉTODO É NECESSÁRIO CRIAR A BASE iluminare (utf-8 default)
    
    cria_salas_tratamentos()
    processa_manutencoes()
    processa_atendimentos_voluntarios()
    processa_atendimentos_quinta()

    delta_t = datetime.now() - t0 
    print delta_t
    
    arquivo_log.close()



### EXECUTA:
# processa()
#processa_arquivo("", "", "")
