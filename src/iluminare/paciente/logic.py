# coding: utf-8
from iluminare.paciente.models import *
from iluminare.tratamento.models import *
import re, datetime

class PacienteException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return repr(self.message)

def validar_detalhe_prioridade(detalhe_prioridade):
    """
        recebe um objeto do tipo detalhe prioridade e faz as modificações nele
        para que ele seja salvo corretamente.
        validações
            - se uma grávida está com data de início da gestação
            - se é uma lactante, tem que possuir a data início de amamentação 
    """
    
    if detalhe_prioridade is None:
        raise PacienteException("Problema ao salvar o tipo de prioridade.")

    #if detalhe_prioridade.data_inicio_gravidez is None and detalhe_prioridade.gravida is True:
    #    raise PacienteException("A grávida precisa da data de inicio da gestacao.")

def consultar_paciente(codigo):
    try:
        codigo = int(codigo)
    except ValueError:
        raise PacienteException("Erro: código do paciente inválido: " + codigo)

    dic = {}
    
    try:
        paciente = Paciente.objects.get(id=codigo)
        
        # garante que só venham tratamentos_paciente com data_fim vazias. Isso significa que se tratam de tratamentos ativos para o paciente.
        tratamentos_paciente = TratamentoPaciente.objects.filter(paciente=codigo, data_fim = None)
        tratamentos = []
        for t in tratamentos_paciente:
            tratamentos.append(t.tratamento)

        try:
           detalhe_prioridade = DetalhePrioridade.objects.get(paciente=codigo)
        except DetalhePrioridade.DoesNotExist:
           detalhe_prioridade = None
        
        dic = {'paciente': paciente,
               'tratamentos': tratamentos,
               'detalhe_prioridade': detalhe_prioridade} 

    except Paciente.DoesNotExist:
        dic = {}
        
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
        tratamentos = paciente.tratamentopaciente_set.filter(status='A', paciente=paciente)
        try:
            it = InstanciaTratamento.objects.raw("""select it.* from paciente_paciente as p
	            join atendimento_atendimento as ate
		            on p.id = ate.paciente_id
	            join tratamento_instanciatratamento as it
		            on ate.instancia_tratamento_id = it.id
	            where p.id = %d
	            order by it.data desc
	            limit 1;""" % paciente.id)[0]
        except:
            it = ''
        dic = {
			'tratamentos': tratamentos,
			'paciente':paciente,
            'atendimento': it,
            'salas': "TODO",
			'hoje': 'TODO'
        }

        lista.append(dic)

    return lista
 
