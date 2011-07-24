# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from iluminare.paciente.models import *
from iluminare.atendimento.models import *
from iluminare.tratamento.models import *

import iluminare.paciente.logic as paciente_logic
import datetime

def ajaxlistarpessoas (request, nome):
    pacientes = None

    if request.method == 'GET' and nome != '':
        pacientes = paciente_logic.search(nome)
        
    if not pacientes:
        pacientes = Paciente.objects.all()[:10]

    lista = paciente_logic.format_table(pacientes)

    return render_to_response ('ajax-listar-pessoas.html', {'pacientes':lista})

def dialog_detalhe(request, paciente_id, tratamento_id):
    lista = TratamentoPaciente.objects.filter(tratamento__id=tratamento_id, paciente__id=paciente_id)
    
    if not lista:
        return HttpResponse ("O tratamento do paciente não está cadastrado")

    tratamento_em_andamento = lista[0]
    sala = tratamento_em_andamento.tratamento.sala
    nome = tratamento_em_andamento.paciente.nome

    tratamentos = Tratamento.objects.all()
    salas = []
    for tratamento in tratamentos:
        display = "%s (%s)" % (tratamento.sala, tratamento.get_dia_display()) 
        salas.append({'id':tratamento.id, 'display':display})
    
    dic = {
        'nome': nome,
        'sala': sala,
		'tratamentos': salas
    }

    return render_to_response ('ajax-dialog-detalhe-paciente.html', dic)

def index(request):
    return render_to_response ('index.html')


