# coding: utf-8
from iluminare.paciente.models import *
import re, datetime

def search(nome):
    """
        retorno: DataSet (i.e.: Paciente.objects.all()
    """

    data = re.findall('([0-9]{2})([0-9]{2})([0-9]{4})', nome)
    if data:
        data_nascimento = data[0]
        data_nascimento = "%s-%s-%s" % (data_nascimento[2], data_nascimento[1], data_nascimento[0])
        pacientes = Paciente.objects.filter(data_nascimento__startswith=data_nascimento)
    else:
        pacientes = Paciente.objects.filter(nome__istartswith=nome)
    
    return pacientes


def format_table(pacientes):
    """
        retorno: {
            'tratamento_id': int,
            'id': int,
            'nome': str,
            'data_nascimento': str}
    """

    lista = []
    for paciente in pacientes:

        dic = {
			'tratamento_id': 0,
			'id':paciente.id,
            'nome':paciente.nome,
			'data_nascimento':paciente.data_nascimento and paciente.data_nascimento.strftime("%d/%m/%Y") or '',
            'atendimentos': "TODO",
            'salas': "TODO",
			'hoje': 'TODO'
        }

        lista.append(dic)

    return lista
 
