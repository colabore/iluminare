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

from django.db.models import Q
import  traceback

dir_log = "/media/DATA/Iluminare/relatorios/"


def gera_csv(lista_rotulos, lista, nome_arquivo_csv):
    
    spamWriter = csv.writer(open(dir_log+nome_arquivo_csv, 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    try:
        spamWriter.writerow(lista_rotulos)
    except:
        print lista_rotulos
        traceback.print_exc()
        
    
    for item in lista:
        try:
            spamWriter.writerow(item)
        except:
            print item
            traceback.print_exc()

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
    
    tratamentos = Tratamento.objects.all()
    lista_salas = [tratamento.descricao_basica.encode('utf-8') for tratamento in tratamentos]
    lista_rotulos = ["Data"] + ["Ano-mes".encode('utf-8')] + lista_salas
    lista_rotulos = lista_rotulos + ["Todos"]
    
    # listar datas
    # no caso, serão as quintas feiras de 01/01/2011 até agora.
    lista_datas = []
    data_inicial = datetime(ano, 1,1).date()
    data_final = datetime.today().date()
    
    a = data_inicial
    while a <= data_final:
        if a.weekday()==3 or a.weekday()==0:
            lista_datas.append(a)
        a = a + timedelta(1)
    
    lista_dados = []
    for d in lista_datas:
        lista_linha = []
        lista_linha.append(str(d))
        lista_linha.append(str(d.year)+'-'+str(d.month))
        total = 0
        for s in lista_salas:
            # consulta
            ats = Atendimento.objects.filter(instancia_tratamento__data = d, \
                instancia_tratamento__tratamento__descricao_basica = s, status = 'A')
            lista_linha.append(len(ats))
            total += len(ats)

        lista_linha.append(total)
        lista_dados.append(lista_linha)
    
    gera_csv(lista_rotulos, lista_dados, "relatorio_2011.csv")


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
    


def relatorio_atendimentos_basico():
    ats = Atendimento.objects.filter(Q(instancia_tratamento__data__year=2011) | Q(instancia_tratamento__data__year=2012))
#    ats = Atendimento.objects.all()
    # 17 campos
    lista_rotulos = ["Id Atendimento", #1
                    "Nome Paciente", #2
                    "Sexo", #3
                    "Tratamento", #4
                    "Tratamento 2", # 5
                    "Tratamento dia", #6
                    "Data", #7
                    "Hora chegada",#8
                    "Status atendimento", #9
                    "Voluntario", #10
                    "Prioridade", #11
                    "Tipo Prioridade", #12
                    "Prioridade no dia", #13
                    "Observacao", #14
                    "Observacao Prioridade", #15
                    "Mes", #16
                    "Ano", #17
                    "Dia semana", #18
                    "Mais de um tratamento", #19
                    "Último atendimento", #20
                    "Ativo", #21 indica se o paciente está 'ativo'. inativo indica que está há mais de 3 meses sem se tratar.
                    "Primeiro atendimento - Trat atual", #22
                    "Id Paciente"] #23
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

        tps = TratamentoPaciente.objects.filter(paciente = at.paciente, status='A')
        if len(tps) == 1:
            lista.append(smart_str(tps[0].tratamento.descricao_basica)) #4
            lista.append("") #5
        elif len(tps) >= 2:
            lista.append(smart_str(tps[0].tratamento.descricao_basica))
            lista.append(smart_str(tps[1].tratamento.descricao_basica))
        else: 
            lista.append("")
            lista.append("")
            
        if (at.instancia_tratamento.tratamento.id == 4 and at.instancia_tratamento.data < datetime(2012,1,1).date()) or \
            (at.instancia_tratamento.tratamento.id == 5 and at.instancia_tratamento.data >= datetime(2012,1,1).date()):
            lista.append(smart_str("Sala 5 (4 até 2011)")) #6
        elif (at.instancia_tratamento.tratamento.id == 5 and at.instancia_tratamento.data < datetime(2012,1,1).date()) or \
            (at.instancia_tratamento.tratamento.id == 4 and at.instancia_tratamento.data >= datetime(2012,1,1).date()):
            lista.append(smart_str("Sala 4 (5 até 2011)"))
        else:
            lista.append(smart_str(at.instancia_tratamento.tratamento.descricao_basica)) 

        lista.append(at.instancia_tratamento.data) #7
        lista.append(at.hora_chegada) #8
        lista.append(at.status) #9
        vols = Voluntario.objects.filter(paciente = at.paciente, ativo = True)
        if vols:
            lista.append(vols[0].tipo) #10
        else:
            lista.append("")
        dtps = DetalhePrioridade.objects.filter(paciente = at.paciente)
        if len(dtps) > 0:
            lista.append("P") #11
            lista.append(dtps[0].tipo) # 12
        else:
            lista.append("N")
            lista.append("")
        if at.prioridade:
            lista.append("P") #13
        else:
            lista.append("N")
        lista.append(smart_str(at.observacao)) #14
        lista.append(smart_str(at.observacao_prioridade)) #15
        lista.append(at.instancia_tratamento.data.month) #16
        lista.append(at.instancia_tratamento.data.year) #17

        dia_semana_str = retorna_dia_semana(at.instancia_tratamento.data)
        lista.append(smart_str(dia_semana_str)) #18
        
        if len(tps) > 1:
            lista.append('S') #19
        else:
            lista.append('N')
        
        it = []
        try:
            it = InstanciaTratamento.objects.raw("""select it.* from paciente_paciente as p
	            join atendimento_atendimento as ate
		            on p.id = ate.paciente_id
	            join tratamento_instanciatratamento as it
		            on ate.instancia_tratamento_id = it.id
	            where p.id = %d and ate.status = 'A'
	            order by it.data desc
	            limit 1;""" % at.paciente.id)[0]
        except:
            it = []

        if it:
            lista.append(it.data) #20
            if it.data >= datetime(2011,12,1).date():
                lista.append('A') #21 Ativo
            else:
                lista.append('I') #21 Inativo
        else:
            lista.append("") #20
            lista.append('I') #21

        try:
            if tps:
                it = InstanciaTratamento.objects.raw("""select it.* from paciente_paciente as p
	                join atendimento_atendimento as ate
		                on p.id = ate.paciente_id
	                join tratamento_instanciatratamento as it
		                on ate.instancia_tratamento_id = it.id
                    join tratamento_tratamento as t
                        on t.id = it.tratamento_id
	                where p.id = %d and ate.status = 'A' and t.id = %d
	                order by it.data asc
	                limit 1;""" % (at.paciente.id,tps[0].tratamento.id))[0]
                if it:
                    lista.append(it.data) #22
                else:
                    lista.append("") #22
            else:
                lista.append("") #22
        except Exception as e:
            lista.append("") #22
            
        lista.append(at.paciente.id) #23
        
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

def retorna_trabalhos_trabalhadores_novo(data_inicial, data_final):
    """
        Retorna a listagens de objetos do tipo de trabalho para todos os trabalhadores
        a partir da data_inicial
        data_inicial é um objeto do tipo datetime.date
        data_final é um objeto do tipo datetime.date

        EXECUTAR.
        
        from datetime import *
        from iluminare.limbo import consultas_gerais
        d1 = datetime(2012, 01, 01)
        d2 = datetime.today()
        consultas_gerais.retorna_trabalhos_trabalhadores_novo(d1, d2)

        
    """
    import datetime
    spamWriter = csv.writer(open(dir_log+"trabalhos3.csv", 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamWriter.writerow(["Nome", #1
                        "Tipo", #2
                        "Tratamento(s)", #3
                        "Data", #4
                        "Dia semana", #5
                        "Hora Inicio", #6
                        "Hora Final", #7
                        "Horas de trabalho"]) #8


    vols = Voluntario.objects.filter(ativo=True)
    
    # criando lista básica de datas
    lista_datas = []
    d = data_inicial
    while d <= data_final:
        lista_datas.append(d)
        d = d + datetime.timedelta(days=1)
    
    for vol in vols:
        for data in lista_datas:
            lista = []
            
            lista.append(smart_str(vol.paciente.nome)) #1
            lista.append(smart_str(vol.tipo)) #2
            tps = TratamentoPaciente.objects.filter(paciente = vol.paciente, status = 'A')
            lista_tratamentos = ''
            for tp in tps:
                lista_tratamentos = tp.tratamento.descricao_basica + ', ' + lista_tratamentos
            lista.append(lista_tratamentos) #3
            lista.append(data) #4
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
            lista.append(smart_str(dia_semana_str)) #5
            
            trabalhos_dia = Trabalho.objects.filter(data = data)
            # garante que somente dias em que há pelo menos um registro de trabalho sejam apresentados
            if trabalhos_dia:
                trabalho = Trabalho.objects.filter(voluntario = vol, data = data)
                if len(trabalho) == 1:
                    trabalho = trabalho[0]
                    
                    if trabalho.hora_inicio:
                        lista.append(trabalho.hora_inicio) #6
                    else:
                        lista.append("X") #6
                        
                    if trabalho.hora_final:
                        lista.append(trabalho.hora_final) #7
                    else:
                        lista.append("X") #7
                        
                    if trabalho.hora_inicio and trabalho.hora_final:
                        diferenca =  datetime.datetime.combine(date.today(), trabalho.hora_final) - \
                            datetime.datetime.combine(date.today(), trabalho.hora_inicio)
                        horas_trabalho = diferenca.__str__()
                        lista.append(horas_trabalho) #8
                    else:
                        lista.append("X") #8
                else:
                    lista.append("X") #6
                    lista.append("X") #7
                    lista.append("X") #8
            else:
                lista.append("X") #6
                lista.append("X") #7
                lista.append("X") #8
                

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
                at = Atendimento.objects.filter(paciente=p, instancia_tratamento__tratamento__id=5).\
                    order_by("-instancia_tratamento__data")
                if len(at) > 0:
                    ult_atendimento = at[0]
                    data_limite = datetime(2013,01,01).date()
                    if ult_atendimento.instancia_tratamento.data > data_limite:
                        lista.append(p)
                        break

    spamWriter = csv.writer(open(dir_log+"fluido12.csv", 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamWriter.writerow(["Id", "Nome", "Ultimo atendimento", "Data encaminhamento", "Quantidade atendimentos"])
    
    print lista
    for paciente in lista:
        l = []
        tp = TratamentoPaciente.objects.filter(paciente = paciente, status='A', tratamento__id=5)
        print tp
        if len(tp) == 1:
            l.append(paciente.id)
            l.append(smart_str(paciente.nome))
            data_enc = tp[0].data_inicio
            at = Atendimento.objects.filter(paciente=paciente, instancia_tratamento__tratamento__id=5, \
                instancia_tratamento__data__gte=data_enc).order_by("-instancia_tratamento__data")
            if len(at) > 0:
                l.append(at[0].instancia_tratamento.data)
            else:
                l.append('F')
            l.append(data_enc)
            l.append(len(at))
            spamWriter.writerow(l)
        else:
            print "Else"


def retorna_lista_pacientes():
    """
        Retorna listagem de pacientes.
        Notar que a fluido era sala 4 até 2011. Em 2012 passou a ser a sala 5.
    """
    pacientes = Paciente.objects.all()

    spamWriter = csv.writer(open(dir_log+"lista_tratamentos.csv", 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamWriter.writerow(["Id", "Nome", "Data", "Tratamento 1", "Tratamento 2", "Mais de um Tratamento", "Atendimento"])
    
    for paciente in pacientes:
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

def redireciona_pacientes():
    nome_arquivo = '/media/DATA/Iluminare/Arquivos locais/reavaliacoes/reav_sala4_abril_2012.csv'
    file = open(nome_arquivo)
    linhas = file.readlines()
    matriz = []
    for linha in linhas:
        linha1 = linha.split(";")
        linha1 = [i.replace("\"","").replace("\n","") for i in linha1]
        matriz.append(linha1)

    for elemento in matriz:
        pacientes = Paciente.objects.filter(nome = elemento[0])
        if len(pacientes) == 0:
            raw_input('erro: '+ elemento[0])
        else:
            paciente = pacientes[0]
            tps = TratamentoPaciente.objects.filter(paciente = paciente, status = 'A')
            for tp in tps:
                tp.status = 'C'
                tp.data_fim = datetime(2012,4,12).date()
                tp.save()
                print tp
            descricao_sala = 'Sala '+elemento[1]
            print descricao_sala
            novo_trat = Tratamento.objects.get(descricao_basica = descricao_sala)
            novo_tp = TratamentoPaciente(paciente = paciente, tratamento = novo_trat, data_inicio = datetime(2012,4,12).date(), status='A')
            novo_tp.save()
            print novo_tp
            if paciente.observacao:
                paciente.observacao = paciente.observacao + ' - Reavaliado(a) dia 12/04 por Nafmenathe para ' + novo_trat.descricao_basica
            else:
                paciente.observacao = 'Reavaliado(a) dia 12/04 por Nafmenathe para ' + novo_trat.descricao_basica
            print paciente.observacao
            paciente.save()
            
        
        
