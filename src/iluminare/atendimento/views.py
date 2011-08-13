# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from iluminare.tratamento.models import Tratamento, InstanciaTratamento
from iluminare.atendimento.models import Atendimento
from iluminare.paciente.models import DetalhePrioridade, Paciente
from iluminare.voluntario.models import Voluntario
from django import forms
from django.forms.models import modelformset_factory, BaseModelFormSet
import datetime
from operator import itemgetter
from django.core.paginator import Paginator

class CheckinPacienteForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        exclude = ['observacao', 'status', 'hora_atendimento', 'hora_chegada', 'instancia_tratamento', 'paciente']

def ajax_checkin_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    if request.method == 'POST':
        pass
    else:
        checkin_paciente_form = CheckinPacienteForm()

    return render_to_response('ajax-checkin-paciente.html', {'paciente':paciente, 'form':checkin_paciente_form})

def get_info(paciente):
    info = ""
    
    try:
        prioridade = paciente.detalheprioridade_set.get()
    except DetalhePrioridade.DoesNotExist:
        prioridade = DetalhePrioridade(paciente=paciente)
        prioridade.save()
    except DetalhePrioridade.MultipleObjectsReturned:
        prioridade = paciente.detalheprioridade_set.all()[0]
    finally:
        info = prioridade.get_tipo_display()

    return info

class FiltroAtendimentosForm(forms.Form):
    tratamento      = forms.ModelChoiceField(queryset=Tratamento.objects.all())
    data            = forms.DateField()
    prioridades     = forms.BooleanField()
    nao_prioridades = forms.BooleanField()

class ConfirmacaoAtendimentoForm(forms.ModelForm):
    observacao = forms.CharField(required=False)
    nome = forms.CharField(required=False)
    info = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ConfirmacaoAtendimentoForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['nome', 'hora_chegada', 'info', 'hora_atendimento', 'status', 'observacao']
        atendimento = kwargs.pop('instance')
        self.fields['nome'].initial = atendimento.paciente.nome
        self.fields['info'].initial = get_info(atendimento.paciente)

    class Meta:
        model = Atendimento
        exclude = ['prioridade', 'instancia_tratamento', 'senha', 'observacao_prioridade', 'paciente']

ConfirmacaoAtendimentoFormSet = modelformset_factory(Atendimento, extra=0,
    form=ConfirmacaoAtendimentoForm)

def confirmacao(request):
    if request.method == "POST":
        filtro_form = FiltroAtendimentosForm(request.POST)
        atendimentos = ConfirmacaoAtendimentoFormSet(request.POST)
        if atendimentos.is_valid():
            atendimentos.save()
    else:
        filtro_form = FiltroAtendimentosForm()
        atendimentos = ConfirmacaoAtendimentoFormSet(queryset=Atendimento.objects.all())
    
    return render_to_response('confirmacao_atendimentos.html', {'filtro_form':filtro_form, 'atendimentos':atendimentos, 'mensagem':atendimentos.errors})
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
						retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': 						prioridade.get_tipo_display() + '/' + voluntario.get_tipo_display(), 'prioridade': True})
					except Voluntario.DoesNotExist:
						retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': 						prioridade.get_tipo_display(), 'prioridade': True})
							
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
	
		
