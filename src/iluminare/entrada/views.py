# Create your views here.
from django.shortcuts import render_to_response
from iluminare.entrada.models import Paciente

def ajaxlistarpessoas (request, nome):
    lista = []
    print nome
    if request.method == 'GET' and nome != '':
        pacientes = Paciente.objects.filter(nome__istartswith=nome)
    else:
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
    
    return render_to_response ('ajax-listar-pessoas.html', {'pacientes':lista})

def index(request):
    return render_to_response ('index.html')    
