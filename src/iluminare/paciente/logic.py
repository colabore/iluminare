# coding: utf-8
from iluminare.paciente.models import *
from iluminare.tratamento.models import *
from iluminare.voluntario.models import *
import re, datetime

class PacienteException(Exception):
    def __init__(self, msg):
        self.message = msg
    
    def __str__(self):
        return repr(self.message)

def inserir_detalhe_prioridade(detalhe_prioridade):
    """
        recebe um objeto do tipo detalhe prioridade e salva na base
            - se é uma grávida ou lactante, é bom que possua o dado data_inicio
    """
    
    if detalhe_prioridade is None:
        raise PacienteException("Objeto detalhe_prioridade inconsistente.")

    if detalhe_prioridade.tipo == None:
        try:
            detalhe_prioridade.delete()
        except:
            pass
    else:
        if detalhe_prioridade.tipo in ['C','P','B'] :
            detalhe_prioridade.data_inicio = None
        detalhe_prioridade.save()

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

        voluntarios = Voluntario.objects.filter(paciente = paciente, ativo=True)
        voluntario = None
        if len(voluntarios) > 0:
            voluntario = voluntarios[0]
        
        dic = {'paciente': paciente,
               'tratamentos': tratamentos,
               'detalhe_prioridade': detalhe_prioridade,
               'voluntario': voluntario
                } 

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
        pacientes = Paciente.objects.filter(data_nascimento__startswith=data_nascimento).order_by('nome')
    else:
        pacientes = Paciente.objects.filter(nome__icontains=nome).order_by('nome')[:30]
    
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
	            where p.id = %d and ate.status = 'A'
	            order by it.data desc
	            limit 1;""" % paciente.id)[0]
        except:
            it = ''
        try:
            # para o caso de já ter algum checkin hoje...
            jtc = False
            it_jtc = InstanciaTratamento.objects.raw("""select it.* from paciente_paciente as p
	            join atendimento_atendimento as ate
		            on p.id = ate.paciente_id
	            join tratamento_instanciatratamento as it
		            on ate.instancia_tratamento_id = it.id
	            where p.id = %d
	            order by it.data desc
	            limit 1;""" % paciente.id)[0]
            if it_jtc.data == datetime.datetime.today().date():
                jtc = True
        except:
            it_jtc = ''
            
        voluntario = Voluntario.objects.filter(paciente = paciente, ativo=True)
        
        eh_vol = False
        if voluntario:
            eh_vol = True

        dic = {
			'tratamentos': tratamentos,
			'paciente':paciente,
            'atendimento': it,
            'salas': "TODO",
			'hoje': 'TODO',
			'jtc': jtc,
			'eh_vol': eh_vol
        }

        lista.append(dic)

    return lista
 
