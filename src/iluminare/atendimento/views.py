# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from iluminare.atendimento.models import *

def index(request):
	return render_to_response('index.html')

#codigo aqui

def exibirAtendimentosPaciente(request, paciente_id):
	
	lista_atendimentos = Atendimento.objects.filter(paciente__id = paciente_id)

	retorno   = [];
	
	for atendimento in lista_atendimentos:
		retorno.append({'data':	atendimento.instancia_tratamento.data, 'tratamento': atendimento.instancia_tratamento.tratamento.descricao_basica, 			'hora_chegada': atendimento.hora_chegada, 'observacao': atendimento.observacao, 'msg': ""})

	if not retorno:
		retorno.append({'data': None, 'tratamento': None, 'hora_chegada': None, 'observacao': None, 'msg': 'Não foi possível localizar usuário'})
	
	return render_to_response('lista-atendimentos.html',{'atendimentos': retorno})	
	
		
