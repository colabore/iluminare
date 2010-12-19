# Create your views here.
from django.shortcuts import render_to_response
from iluminare.entrada.models import Paciente

def index (request):
    lista = []
    pacientes = Paciente.objects.all()[:10]

    for paciente in pacientes:
        atendimentos = paciente.atendimento_set.all()
        at_anteriores = [a.hora_chegada.strftime("%d/%m") for a in atendimentos if a.atendido]
        
        tratamentos = paciente.tratamentoemandamento_set.all()
        salas = ["%s (%s)" % (t.tratamento.sala, t.tratamento.get_dia_display())  for t in tratamentos]

        dic = {
            'nome':paciente.nome,
            'atendimentos': ", ".join(at_anteriores),
            'salas': ",".join(salas)
        }

        lista.append(dic)
    
    return render_to_response ('listar-pessoas.html', {'pacientes':lista})

def listar_pessoas(request):
    return render_to_response ('listar-pessoas.html')    
