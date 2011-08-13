# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from iluminare.atendimento.models import *
from iluminare.tratamento.models import *
from iluminare.voluntario.models import *
from django import forms
import datetime
from operator import itemgetter
from django.core.paginator import Paginator


def index(request):
	return render_to_response('index.html')

#codigo aqui

class ImprimirListagemForm(forms.Form):

	def __init__(self, *args, **kwargs):
        	super(ImprimirListagemForm, self).__init__(*args, **kwargs)
        	self.fields['tratamento'].choices = [('', '----------')] + [(tratamento.id, tratamento.descricao_basica) for tratamento in Tratamento.objects.all()]

	tratamento = forms.ChoiceField(choices=())
	data = forms.DateField(initial = datetime.date.today)
	

def exibir_listagem(request, pagina = None):
	
	form_listagem = ImprimirListagemForm()
	mensagem_erro = ''
	retorno = [];
	
	if request.method == 'POST':
		form_listagem = ImprimirListagemForm(request.POST)

		if form_listagem.is_valid():
			data_in = form_listagem.cleaned_data['data']
			tratamento_in = form_listagem.cleaned_data['tratamento']
			
			tratamentos_marcados = InstanciaTratamento.objects.filter(tratamento__id  = tratamento_in, data = data_in)
			
			for tratamentos in tratamentos_marcados:
				atendimentos_previstos = Atendimento.objects.filter(instancia_tratamento__id = tratamentos.id)
				for atendimento in atendimentos_previstos:
					try:					
						prioridade = DetalhePrioridade.objects.get(paciente__id = atendimento.paciente.id)
						voluntario = Voluntario.objects.get(paciente__id = atendimento.paciente.id)	
						retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': 						prioridade.get_prioridade_display() + '/' + voluntario.get_tipo_display(), 'prioridade': True})
					except Voluntario.DoesNotExist:
						retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': 						prioridade.get_prioridade_display(), 'prioridade': True})
							
					except DetalhePrioridade.DoesNotExist:
						try:					
							voluntario = Voluntario.objects.get(paciente__id = atendimento.paciente.id)
							if atendimento.prioridade:
								retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': 								voluntario.get_tipo_display() + '/' + atendimento.observacao_prioridade, 'prioridade': True})

							else:
								retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': 								voluntario.get_tipo_display(), 'prioridade': False})
						except Voluntario.DoesNotExist:	
							if atendimento.prioridade:
								retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': 								atendimento.observacao_prioridade, 'prioridade': True})
							else:					
								retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info':'', 									'prioridade': False})
			retorno_com_hora = [];
			retorno_sem_hora = [];

			for elemento in retorno:
				if (elemento['hora'] == None):
					retorno_sem_hora.append(elemento)
				else:
					retorno_com_hora.append(elemento)
 
			retorno_com_hora = sorted(retorno_com_hora, key= itemgetter('hora'))
			retorno = retorno_com_hora + retorno_sem_hora			
			
			
			if not retorno:
				mensagem_erro = 'não há registros'
		else:
			mensagem_erro = 'formulário inválido';

	paginacao = Paginator(retorno,3) 
	if pagina == None:
		num_pagina = 1
	else:	
		num_pagina = int(pagina)
	pagina_atual = paginacao.page(num_pagina)		

	
	return render_to_response('listagem-diaria.html', {'form_listagem':form_listagem, 
							'mensagem': mensagem_erro,
							'pagina_atual':pagina_atual})

def exibir_atendimentos_paciente(request, paciente_id):
	
	lista_atendimentos = Atendimento.objects.filter(paciente__id = paciente_id)

	retorno   = [];
	
	for atendimento in lista_atendimentos:
		retorno.append({'data':	atendimento.instancia_tratamento.data, 'tratamento': atendimento.instancia_tratamento.tratamento.descricao_basica, 			'hora_chegada': atendimento.hora_chegada, 'observacao': atendimento.observacao, 'msg': ""})

	if not retorno:
		retorno.append({'data': None, 'tratamento': None, 'hora_chegada': None, 'observacao': None, 'msg': 'Não foi possível localizar usuário'})
	
	return render_to_response('lista-atendimentos.html',{'atendimentos': retorno})	
	
		
