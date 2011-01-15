# -*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse
from iluminare.entrada.models import *

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
			'tratamento_id': tratamentos and tratamentos[0].tratamento.id or 0,
			'id':paciente.id,
            'nome':paciente.nome,
            'atendimentos': ", ".join(at_anteriores),
            'salas': ",".join(salas)
        }

        lista.append(dic)
    
    return render_to_response ('ajax-listar-pessoas.html', {'pacientes':lista})

def dialog_detalhe(request, paciente_id, tratamento_id):
    lista = TratamentoEmAndamento.objects.filter(tratamento__id=tratamento_id, paciente__id=paciente_id)
    
    if not lista:
        return HttpResponse ("O tratamento do paciente não está cadastrado")

    tratamento_em_andamento = lista[0]
    sala = tratamento_em_andamento.tratamento.sala
    nome = tratamento_em_andamento.paciente.nome
	
    dic = {
        'nome': nome,
        'sala': sala
    }

    return render_to_response ('ajax-dialog-detalhe-paciente.html', dic)

def index(request):
    return render_to_response ('index.html')    
