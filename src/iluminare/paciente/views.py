# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from iluminare.paciente.models import *
from iluminare.atendimento.models import *
import datetime, re

def ajaxlistarpessoas (request, nome):
    lista = []
    print nome
    if request.method == 'GET' and nome != '':
        data = re.findall('([0-9]{2})([0-9]{2})([0-9]{4})', nome)
        if data:
            data_nascimento = data[0]
            data_nascimento = "%s-%s-%s" % (data_nascimento[2], data_nascimento[1], data_nascimento[0])
            pacientes = Paciente.objects.filter(data_nascimento__startswith=data_nascimento)
        else:
            pacientes = Paciente.objects.filter(nome__istartswith=nome)
        
    else:
        pacientes = Paciente.objects.all()[:10]

    for paciente in pacientes:
        atendimentos = paciente.atendimento_set.all()
        at_anteriores = [a.hora_chegada.strftime("%d/%m") for a in atendimentos if a.atendido]
       
        hoje = False
        for atendimento in atendimentos:
            chegada = atendimento.hora_chegada
            chegada = (chegada.year, chegada.month, chegada.day)
            agora = datetime.datetime.now()
            agora = (agora.year, agora.month, agora.day)
            if chegada == agora:
                hoje = True

        tratamentos = paciente.tratamentoemandamento_set.all()
        salas = ["%s (%s)" % (t.tratamento.sala, t.tratamento.get_dia_display())  for t in tratamentos]

        dic = {
			'tratamento_id': tratamentos and tratamentos[0].tratamento.id or 0,
			'id':paciente.id,
            'nome':paciente.nome,
			'data_nascimento':paciente.data_nascimento.strftime("%d/%m/%Y"),
            'atendimentos': ", ".join(at_anteriores),
            'salas': ",".join(salas),
			'hoje': hoje and '\o/' or ':('
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


