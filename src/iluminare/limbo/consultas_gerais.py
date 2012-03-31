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

# funcao desenvolvida para carga de dados..
# no dia 15-12-2011 iniciamos os trabalhos sem os dados do dia 12.
def carrega_ats_15122011():
    spamReader = csv.reader(open(dir_log+'ats_15122011.csv', 'rb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    it_s1 = InstanciaTratamento(tratamento = Tratamento.objects.get(descricao_basica='Sala 1'), data='2011-12-15')
    it_s1.save()
    it_s2 = InstanciaTratamento(tratamento = Tratamento.objects.get(descricao_basica='Sala 2'), data='2011-12-15')
    it_s2.save()
    it_s3 = InstanciaTratamento(tratamento = Tratamento.objects.get(descricao_basica='Sala 3'), data='2011-12-15')
    it_s3.save()
    it_s4 = InstanciaTratamento(tratamento = Tratamento.objects.get(descricao_basica='Sala 4'), data='2011-12-15')
    it_s4.save()
    it_s5 = InstanciaTratamento(tratamento = Tratamento.objects.get(descricao_basica='Sala 5'), data='2011-12-15')
    it_s5.save()
    
    for row in spamReader:
        print row[1]
        pac = Paciente.objects.filter(nome=row[1])
        if len(pac) == 0:
            pac = Paciente(nome = row[1])
            pac.save()
            print 'NOVO PACIENTE: ' + row[1]
        elif len(pac) == 1:
            pac = pac[0]
        else:
            print 'MAIS DE UM NOME.. ' + row[1]
            pac = Paciente.objects.get(id=row[0])
            
        sala_str = row[2]
        it = None
        if sala_str == 'Sala 1':
            it = it_s1
        elif sala_str == 'Sala 2':
            it = it_s2
        elif sala_str == 'Sala 3':
            it = it_s3
        elif sala_str == 'Sala 4':
            it = it_s4
        elif sala_str == 'Sala 5':
            it = it_s5
        at = Atendimento(paciente = pac, instancia_tratamento = it, hora_chegada = row[3], status = row[4], \
            observacao_prioridade = row[5], observacao = row[6])
        at.save()
            
            

    spamReader = csv.reader(open(dir_log+'ts_15122011.csv', 'rb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in spamReader:
        print row[0]
        vol = Voluntario.objects.get(id=row[0])
        f = Funcao.objects.get(descricao='Geral')
        if len(row[2]) > 0:
            trabalho = Trabalho(funcao = f, voluntario = vol, data = '2011-12-15', hora_inicio = row[1], hora_final = row[2])
        else:
            trabalho = Trabalho(funcao = f, voluntario = vol, data = '2011-12-15', hora_inicio = row[1])
        trabalho.save()
    

# funcao desenvolvida para carga de dados..
# no dia 15-12-2011 iniciamos os trabalhos sem os dados do dia 12.
def atendimentos_15122011():
    ats = Atendimento.objects.filter(instancia_tratamento__data='2011-12-15')
    # 7 campos
    lista_rotulos = ["Id Paciente", #1
                    "Nome Paciente", #2
                    "Tratamento", #3
                    "Hora chegada",#4
                    "Status", #5
                    "Observacao Prioridade", #6
                    "Observacao"] #7
    
    lista_retorno = []
    for at in ats:
        lista = []
        lista.append(at.paciente.id) #1
        print at.paciente.id
        
        lista.append(smart_str(at.paciente.nome)) #2
        
        lista.append(smart_str(at.instancia_tratamento.tratamento.descricao_basica)) #3

        lista.append(at.hora_chegada) #4
        lista.append(at.status) #5
        lista.append(smart_str(at.observacao_prioridade)) #6
        lista.append(smart_str(at.observacao)) #7
        
        lista_retorno.append(lista)
        
    gera_csv(lista_rotulos, lista_retorno, "ats_15122011.csv")

    
    ts = Trabalho.objects.filter(data = '2011-12-15')
    lista_rotulos = ["Id Voluntario", #1
                    "Hora Inicio", #2
                    "Hora final"] #3

    lista_retorno = []
    for t in ts:
        lista = []
        lista.append(t.voluntario.id) #1
        print t.voluntario.id
        
        lista.append(t.hora_inicio) #2
        lista.append(t.hora_final) #3
        
        lista_retorno.append(lista)
        
    gera_csv(lista_rotulos, lista_retorno, "ts_15122011.csv")

def relatorio_trabalhos():
    ts = Trabalho.objects.filter()
    
    lista_rotulos = ["Id Trabalho", #1
                    "Nome voluntário", #2
                    "Data", #3
                    "Dia semana", #4
                    "Mes", #5
                    "Ano", #6
                    "Hora inicio", #7
                    "Hora final", #8
                    "Ativo", #9
                    "Tipo voluntário" #10
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

        lista.append(t.voluntario.tipo) #10
        
        lista_retorno.append(lista)
        
    gera_csv(lista_rotulos, lista_retorno, "relatorio_trabalhos.csv")


def relatorio_atendimentos_por_sala(ano=2011):
    """
        Gera um arquivo CSV com a quantidade atendimentos por sala para cada data.
        Parametros: 
        - ano: a partir de..
    """
    
    lista_salas = ["Sala 1", "Sala 2", "Sala 3", "Sala 4", "Sala 5"]
    lista_rotulos = ["Data"] + lista_salas
    lista_rotulos = lista_rotulos + ["Todos"]
    
    # listar datas
    # no caso, serão as quintas feiras de 01/01/2011 até agora.
    lista_datas = []
    data_inicial = datetime(ano, 1,1).date()
    data_final = datetime.today().date()
    
    a = data_inicial
    while a <= data_final:
        if a.weekday()==3:
            lista_datas.append(a)
        a = a + timedelta(1)
    
    lista_dados = []
    for d in lista_datas:
        lista_linha = []
        lista_linha.append(str(d))
        total = 0
        for s in lista_salas:
            # consulta
            ats = Atendimento.objects.filter(instancia_tratamento__data = d, \
                instancia_tratamento__tratamento__descricao_basica = s, status = 'A')
            lista_linha.append(len(ats))
            total += len(ats)

        lista_linha.append(total)
        lista_dados.append(lista_linha)
    
    gera_csv(lista_rotulos, lista_dados, "relatorio.csv")


def histograma_horarios():
    """
        Plota um histograma com os horários de chegada dos pacientes
    """
    import numpy as np
    import matplotlib.pyplot as plt

    data = datetime(2011, 12,8)
    ats = Atendimento.objects.filter(instancia_tratamento__data = data)
    horas = [a.hora_chegada.hour*60 + a.hora_chegada.minute for a in ats]
    plt.hist(horas, 25)
    plt.show()
    


def relatorio_atendimentos_basico(ano=2012):
    ats = Atendimento.objects.filter(instancia_tratamento__data__year=ano)
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
        #print at.id
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


def retorna_trabalhos_trabalhadores(data_inicial):
    """
        Retorna a listagens de objetos do tipo de trabalho para todos os trabalhadores
        a partir da data_inicial
        data_inicial é um objeto do tipo datetime.date
    """
    
    ts = Trabalho.objects.raw("""
        select tr.id, p.nome, tr.data, tr.hora_inicio, tr.hora_final from voluntario_trabalho tr
            join voluntario_voluntario v on v.id = tr.voluntario_id
            join paciente_paciente p on p.id = v.paciente_id;    
        """)
    
    spamWriter = csv.writer(open(dir_log+"trabalhos2.csv", 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamWriter.writerow(["Id", #1
                        "Nome", #2
                        "Tipo", #3
                        "Tratamento(s)", #4
                        "Data", #5
                        "Dia semana", #6
                        "Hora Inicio", #7
                        "Hora Final"]) #8

    for t in ts:
        if t.data >= data_inicial:
            lista = []
            lista.append(t.id) #1
            lista.append(smart_str(t.voluntario.paciente.nome)) #2
            lista.append(smart_str(t.voluntario.tipo)) #3
            tps = TratamentoPaciente.objects.filter(paciente = t.voluntario.paciente, status = 'A')
            lista_tratamentos = ''
            for tp in tps:
                lista_tratamentos = tp.tratamento.descricao_basica + ', ' + lista_tratamentos
            lista.append(lista_tratamentos) #4
            lista.append(t.data) #5
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
            lista.append(smart_str(dia_semana_str)) #6
            lista.append(t.hora_inicio) #7
            lista.append(t.hora_final) #8
            spamWriter.writerow(lista)
        

def retorna_criancas():
    """
        Salva arquivo com listagem de crianças com nome, tratamento atual e data de último atendimento.
    """
    dpc = DetalhePrioridade.objects.filter(tipo='C')
    lista = []
    f = open(dir_log+'criancas.csv', 'w')
    for c in d:
        print c.paciente.nome
        l1 = []
        l1.append(c.paciente.nome)
        l_tp_ativos = []
        for tp in c.paciente.tratamentopaciente_set.values():
            if tp['status'] == 'A':
                l_tp_ativos.append(tp)
        if len(l_tp_ativos) > 0:
            l1.append(Tratamento.objects.get(id=l_tp_ativos[0]['tratamento_id']).descricao_basica)
        else:
            l1.append('')
        try:
            it = InstanciaTratamento.objects.raw("""select it.* from paciente_paciente as p
                join atendimento_atendimento as ate
                    on p.id = ate.paciente_id
                join tratamento_instanciatratamento as it
                    on ate.instancia_tratamento_id = it.id
                where p.id = %d and ate.status = 'A'
                order by it.data desc
                limit 1;""" % c.paciente.id)[0]
            l1.append(str(it.data))
        except:
            l1.append('')
        lista.append(l1)
        f.write(smart_str(l1[0]) + ';' + smart_str(l1[1]) + ';' + l1[2] + '\n')
        
    f.close()


def _retorna_tratamento_ativo(paciente):
    """
        Retorna um tratamento ativo do paciente.
        Por enquanto, ignoramos o fato de que um paciente pode ter mais de um tratamento ativo.
    """
    tps = paciente.tratamentopaciente_set.values()
    for tp in tps:
        if tp['status'] == 'A':
            trat = Tratamento.objects.get(tp['tratamento_id'])
            return trat

    # se chegar aqui é porque não há tratamentos ativos. Logo, retorna None.
    return None


def retorna_lista_pacientes_fluido():
    """
        retorna listagem de pacientes da fluido que estão com mais de 12 tratamentos.
        Falta ajsutar...
        Notar que a fluido era sala 4 até 2011. Em 2012 passou a ser a sala 5.
    """
    pacientes = Paciente.objects.all()

    # primeiramente eu identifico todos os pacientes que estão ativos na sala 5 (fluido).
    lista = []
    for p in pacientes:
        tps = p.tratamentopaciente_set.values()
        var = 0
        for tp in tps:
            if tp['status'] == 'A' and tp['tratamento_id'] == 5:
                lista.append(p)
                break

    spamWriter = csv.writer(open(dir_log+"fluido12.csv", 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamWriter.writerow(["Id", "Nome", "Data", "Tratamento"])
    
    for paciente in lista:
        ats = Atendimento.objects.filter(paciente = paciente)
        #trat = _retorna_tratamento_ativo(paciente)
        for at in ats:
            l = []
            if (at.instancia_tratamento.tratamento.id == 4 and at.instancia_tratamento.data < datetime(2012,1,1).date()) or \
                (at.instancia_tratamento.tratamento.id == 5 and at.instancia_tratamento.data >= datetime(2012,1,1).date()):
                l.append(at.id)
                l.append(smart_str(paciente.nome))
                l.append(at.instancia_tratamento.data)
                l.append("Fluido")
                spamWriter.writerow(l)
            
