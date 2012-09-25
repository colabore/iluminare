# -*- coding: utf-8 -*-
from pylab import *
import numpy
import matplotlib.pyplot as plt
from iluminare.paciente.models import *
from iluminare.atendimento.models import *
from django.utils.encoding import smart_str, smart_unicode
import datetime

def autolabel(rects, ax):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                ha='center', va='bottom')


def plotar_histograma_escolaridade():
    x = arange(len(Paciente.ESCOLARIDADE))
    quant = [0]*len(Paciente.ESCOLARIDADE)
    descricoes = []
    for esc in Paciente.ESCOLARIDADE:
        descricoes.append(smart_unicode(esc[1]))

    pacientes = Paciente.objects.filter(escolaridade__isnull=False)
    for p in pacientes:
        cod_esc = int(p.escolaridade)
        quant[cod_esc-1] = quant[cod_esc-1]+1

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title(smart_unicode('Histograma de Escolaridade'))
    ax.set_ylabel('# pacientes')
    ax.set_xlabel('Escolaridade')
    #ax.bar(x, quant, align='center')
    s = ax.bar(x, quant)
    xticks( x + 0.5, tuple(descricoes))
    labels = ax.get_xticklabels()
    setp(labels, rotation=-30)
    fig.autofmt_xdate()

    autolabel(s, ax)
    plt.show()

def lista_meses(ano_inicial=2011):
    lista = []
    ano = 2011
    mes = 1
    while True:
        lista.append(str(mes)+'-'+str(ano))
        if mes==12:
            mes = 1
            ano+=1
        else:
            mes+=1
        if datetime.date.today().year <= ano and datetime.date.today().month < mes:
            break
    return lista

def plotar_historico_atendimentos(ano_inicial=2011):
    meses = lista_meses(ano_inicial)
    x = arange(len(meses))
    numero_atendimentos = [0]*len(meses)
    cont = 0
    for m in meses:
        mes = m.split('-')[0]
        ano = m.split('-')[1]
        ats = Atendimento.objects.filter(status='A', instancia_tratamento__data__month=mes, instancia_tratamento__data__year=ano)
        numero_atendimentos[cont]=len(ats)
        cont+=1
    
    fig = figure()
    ax = fig.add_subplot(111)
    ax.set_title(smart_unicode('Número de atendimentos por mês'))
    ax.set_ylabel('# pacientes')
    ax.set_xlabel(smart_unicode('Mês'))
    
#    ax.xaxis.set_major_formatter(formatter)
    s = ax.bar(x, numero_atendimentos)
    xticks(x + 0.5, tuple(meses))
    labels = ax.get_xticklabels()
    setp(labels, rotation=-30)
    
    #ax.plot(numpy.arange(len(meses)), numero_atendimentos, 'o-')
    fig.autofmt_xdate()
    autolabel(s, ax)
    show()


plotar_histograma_escolaridade()
plotar_historico_atendimentos()

