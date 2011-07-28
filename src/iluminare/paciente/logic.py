# coding: utf-8
from iluminare.paciente.models import *
from iluminare.tratamento.models import *
import re, datetime

class PacienteException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return repr(self.message)


def consultar_paciente(codigo):
    
    
    try:
        codigo = int(codigo)
    except ValueError:
        raise PacienteException("Erro: código do paciente inválido: " + codigo)

    dic = {}
    
    try:
        paciente = Paciente.objects.get(id=codigo)
        # ainda falta filtrar os tratamentos já encerrados
        tratamentos_paciente = TratamentoPaciente.objects.filter(paciente=codigo)
        tratamentos = []
        for t in tratamentos_paciente:
            tratamentos.append(t.tratamento)
        
        if DetalhePrioridade.objects.filter(paciente=codigo).count() == 1:
            detalhe_prioridade = DetalhePrioridade.objects.get(paciente=codigo)
        else:
            detalhe_prioridade = None
        
        
        dic = {  'paciente': paciente,
                 'tratamentos': tratamentos,
                 'detalhe_prioridade': detalhe_prioridade
                 
              } 

    except Paciente.DoesNotExist:
        dic = {}
    except:
        raise PacienteException("Erro na função consultar paciente")
        
    return dic

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
 
