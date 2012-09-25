
from iluminare.atendimento.models import *
import datetime

def conta_duplicados_data(data):
    ats = Atendimento.objects.filter(instancia_tratamento__data = data)
    lista = []
    lista_dupli = []
    for at in ats:
        if at.paciente in lista:
            lista_dupli.append(at)
        lista.append(at.paciente)
    return len(lista_dupli)


def conta_duplicados():
    data_var = datetime.date(2012,1,1)
    hoje = datetime.date.today()
    dic = {}
    while data_var < hoje:
        if data_var.weekday() == 3:
            cont = conta_duplicados_data(data_var)
            dic[data_var] = cont
        data_var = datetime.date.fromordinal(data_var.toordinal()+1)
    return dic

dic = conta_duplicados()
print dic
