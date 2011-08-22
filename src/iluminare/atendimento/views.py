# -*- coding: utf-8 -*-
from iluminare.tratamento.models import Tratamento, InstanciaTratamento, TratamentoPaciente
from iluminare.atendimento.models import Atendimento
from iluminare.voluntario.models import Voluntario

from iluminare.paciente.models import DetalhePrioridade, Paciente
import iluminare.atendimento.logic as logic_atendimento

from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.core.paginator import Paginator
from django.http import HttpResponse

import datetime
from operator import itemgetter

class CheckinPacienteForm(forms.ModelForm):
    redirecionar = forms.ModelChoiceField(queryset=Tratamento.objects.all(), required=False)
    tratamento   = forms.ModelChoiceField(queryset=TratamentoPaciente.objects.all(), required=False)

    def __init__(self, *args, **kargs):
        super(CheckinPacienteForm, self).__init__(*args, **kargs)
        self.fields.keyOrder = ['tratamento', 'senha', 'redirecionar', 'prioridade', 'observacao_prioridade']

    def update_tratamentos(self, paciente):
        tratamentos = paciente.tratamentopaciente_set.all()
        self.fields['tratamento'].queryset = tratamentos
        self.fields['observacao_prioridade'].help_tag = "Observação (prioridade)"

    class Meta:
        model = Atendimento
        exclude = ['observacao', 'status', 'hora_atendimento', 'hora_chegada', 'instancia_tratamento', 'paciente']

def ajax_checkin_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    if request.method == 'POST':
        checkin_paciente_form = CheckinPacienteForm(request.POST)
        if checkin_paciente_form.is_valid():
            tratamento              = checkin_paciente_form.cleaned_data['tratamento']
            senha                   = checkin_paciente_form.cleaned_data['senha']
            redirecionar            = checkin_paciente_form.cleaned_data['redirecionar']
            prioridade              = checkin_paciente_form.cleaned_data['prioridade']
            observacao_prioridade   = checkin_paciente_form.cleaned_data['observacao_prioridade']

            try:
                logic_atendimento.checkin_paciente(paciente, tratamento, senha, redirecionar, prioridade, observacao_prioridade)
                return HttpResponse("O checking de %s foi realizado com sucesso" % paciente.nome)
            except Exception, e:
                return HttpResponse("Erro: %s" % e)
        else:
            return HttpResponse("errro %s" % str(checkin_paciente_form.errors))
    else:
        checkin_paciente_form = CheckinPacienteForm()
    
    checkin_paciente_form.update_tratamentos(paciente)

    return render_to_response('ajax-checkin-paciente.html', {'paciente':paciente, 'form':checkin_paciente_form, 'erros':str(checkin_paciente_form.errors)})

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
	
        if filtro_form.is_valid() and atendimentos.is_valid():
            tratamento = filtro_form.cleaned_data['tratamento']
            data	   = filtro_form.cleaned_data['data']
            atendimentos = ConfirmacaoAtendimentoFormSet(queryset=Atendimento.objects.filter(instancia_tratamento__data=data,instancia_tratamento__tratamento=tratamento,status='C'))
		
    else:
        filtro_form = FiltroAtendimentosForm()
        atendimentos = ConfirmacaoAtendimentoFormSet(queryset=Atendimento.objects.none())
    
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
	
class RelatorioAtendimentoData(forms.Form):

	def __init__(self, *args, **kwargs):
		super(RelatorioAtendimentoData,self).__init__(*args, **kwargs)
		self.fields['tratamento'].choices = [('', '----------')] + [(tratamento.id, tratamento.descricao_basica) for tratamento in 			  			Tratamento.objects.all	()]

	STATUS = (
		('C','CHECK-IN'), 
		('I','IMPRESSO'), 
		('X','CHAMADO'), 
		('A','ATENDIDO'), 
		('N','NAO-ATENDIDO'))
	
	status = forms.ChoiceField(choices= STATUS)

	data = forms.DateField(initial = datetime.date.today)
	tratamento = forms.ChoiceField(choices=())
	

def exibir_relatorio_atendimento(rquest):

	form_relatorio = RelatorioAtendimentoData()
	mensagem_erro = ''	
	
	if request.method == "POST":
		
		if form_listagem.is_valid():
			data_in = form_listagem.cleaned_data['data']
			tratamento_in = form_listagem.cleaned_data['tratamento']
		else:
			mensagem_erro = 'formulário inválido'	
		

	return render_to_response('relatorio-atendimento.html', {'form_relatorio':form_relatorio})

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

	paginacao = Paginator(retorno,45) 
	if pagina == None:
		num_pagina = 1
	else:	
		num_pagina = int(pagina)
	pagina_atual = paginacao.page(num_pagina)		

	
	return render_to_response('listagem-diaria.html', {'form_listagem':form_listagem, 
							'mensagem': mensagem_erro,
							'pagina_atual':pagina_atual})

def exibir_atendimentos_paciente(request, paciente_id, pagina = None):
	lista_atendimentos = Atendimento.objects.filter(paciente__id = paciente_id)

	mensagem_erro = ''
	retorno   = [];
	
	for atendimento in lista_atendimentos:
		retorno.append({'data':	atendimento.instancia_tratamento.data, 'tratamento': atendimento.instancia_tratamento.tratamento.descricao_basica, 			'hora_chegada': atendimento.hora_chegada, 'observacao': atendimento.observacao})
		
		
	if not retorno:
		mensagem_erro = 'Não foi possível localizar usuário'
		
	paginacao = Paginator(retorno,45)
	if pagina == None:
		num_pagina = 1
	else:	
		num_pagina = int(pagina)
	pagina_atual = paginacao.page(num_pagina)	
	
	return render_to_response('lista-atendimentos.html',{'mensagem': mensagem_erro, 'pagina_atual': pagina_atual, 'paciente_id': paciente_id})	
	
		
