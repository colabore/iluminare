
#-*- coding: utf-8 -*-


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

"""


import MySQLdb

# PARÂMETROS
arquivo_sala1 = "Pacientes_QL_25_11_2010_sala1.csv"
arquivo_sala2 = "Pacientes_QL_25_11_2010_sala2.csv"
arquivo_sala3 = "Pacientes_QL_25_11_2010_sala3.csv"
arquivo_sala4 = "Pacientes_QL_25_11_2010_sala4.csv"
arquivo_sala5 = "Pacientes_QL_25_11_2010_sala5.csv"


# retorna matriz com todas as linhas lidas no arquivo
def le_arquivo(nome_arquivo):
    file = open(nome_arquivo)
    linhas = file.readlines()
    matriz = []
    for linha in linhas:
        linha = linha.decode("cp1252") 
        linha1 = linha.split(";",13)[1:13]
        if linha1[0] == '':
            break
        matriz.append (linha.split(";",13)[1:13])
        #print (linha.split(";",13)[0:13])
    matriz = matriz[3:]
    return matriz


# retorna a lista somente com os nomes dos pacientes
def lista_nomes(nome_arquivo):
    matriz = le_arquivo(nome_arquivo)
    lista = []
    for linha in matriz:
        nome_maiusculo = primeira_letra_maiuscula(linha[0])
        lista.append(nome_maiusculo)
        #print linha[1] 
    return lista

# Retorna o nome da pessoa com a primeira letra maiúscula
# Excecão para palavras com 1 letra, 'da' e 'de'.
# Evita que tenhamos João Da Silva ou João E Silva
def letra_maiuscula(nome):
    if len(nome) == 1:
        return nome.lower()
    elif nome.lower() == 'da':
        return nome.lower()
    elif nome.lower() == 'de':
        return nome.lower()
    else:
        return nome.capitalize()

# recebe como parêmetro um nome completo uppercase.
# retorna o nome da pessoa somente com as primeiras letras maiúsculas
# Ex: JOÃO DA SILVA -> João da Silva
def primeira_letra_maiuscula(nome):
    list = nome.split(' ')
    # para cada item na lista, põe a primeira letra maiúscula
    list2 = [letra_maiuscula(c) for c in list]
    nome2 = ' '.join(list2)
    return nome2


# método que recebe como parâmetro a lista dos nomes dos pacientes e a sala
# e insere os dados no banco de dados
def insere_no_banco(lista, sala):
    # Open database connection
    db = MySQLdb.connect(host=".", port=3306, user="root", passwd="root", db="test")
    #db = MySQLdb.connect('localhost','root','root','test',3306 )
    
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    
    for nome in lista:
        # foram usadas aspas duplas no comando insert devido a erro com nomes como 
        # Joana D'arc
        sql = "INSERT INTO paciente(nome, sala) \
               VALUES (\"%s\", \"%s\")" % (nome, sala)
        print sql
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
        except:
            # Rollback in case there is any error
            print "erro"
            raw_input("Erro! Tecle ENTER para continuar...")
            db.rollback()
    db.close()
    return


# método que deve ser chamado para executar a carga de todos os pacientes
# de todas as salas
def executa():
    nomes = lista_nomes(arquivo_sala1)
    insere_no_banco(nomes, "1")
    nomes = lista_nomes(arquivo_sala2)
    insere_no_banco(nomes, "2")
    nomes = lista_nomes(arquivo_sala3)
    insere_no_banco(nomes, "3")
    nomes = lista_nomes(arquivo_sala4)
    insere_no_banco(nomes, "4")
    nomes = lista_nomes(arquivo_sala5)
    insere_no_banco(nomes, "5")
    
    
    


def main():
    nomes = lista_nomes(arquivo_sala1)
    
    i = 1
    for x in nomes:
        print str(i) + '-' + x
        i = i+1


#main()
executa()

#nome = "JOAO DA SILVA"

#print primeira_letra_maiuscula(nome)

#print lista_nomes(matriz)



#print matriz

