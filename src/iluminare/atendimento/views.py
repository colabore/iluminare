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

import itertools

class CheckinPacienteForm(forms.ModelForm):
    redirecionar = forms.ModelChoiceField(queryset=Tratamento.objects.all(), required=False)
    tratamento   = forms.ModelChoiceField(queryset=Tratamento.objects.all(), required=False)

    def __init__(self, *args, **kargs):
        super(CheckinPacienteForm, self).__init__(*args, **kargs)
        self.fields.keyOrder = ['tratamento', 'redirecionar', 'prioridade', 'observacao_prioridade', 'senha']

    def update_tratamentos(self, paciente):
        tratamentos = [tp.tratamento for tp in paciente.tratamentopaciente_set.filter(status='A')]
        ids_tratamentos = [t.id for t in tratamentos]
        self.fields['tratamento'].queryset = Tratamento.objects.filter(id__in=ids_tratamentos)
        self.fields['observacao_prioridade'].help_tag = "Observação (prioridade)"
        self.fields['observacao_prioridade'].label = "Motivo prioridade"
        
    class Meta:
        model = Atendimento
        exclude = ['observacao', 'status', 'hora_atendimento', 'hora_chegada', 'instancia_tratamento', 'paciente']

def ajax_checkin_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    lista_atendimentos = logic_atendimento.atendimentos_paciente(paciente.id)
    
    if request.method == 'POST':
        checkin_paciente_form = CheckinPacienteForm(request.POST)
        if checkin_paciente_form.is_valid():
            tratamento              = checkin_paciente_form.cleaned_data['tratamento']
            senha                   = checkin_paciente_form.cleaned_data['senha']
            redirecionar            = checkin_paciente_form.cleaned_data['redirecionar']
            prioridade              = checkin_paciente_form.cleaned_data['prioridade']
            observacao_prioridade   = checkin_paciente_form.cleaned_data['observacao_prioridade']

            try:
                at = logic_atendimento.checkin_paciente(paciente, tratamento, senha, redirecionar, prioridade, observacao_prioridade)
                return HttpResponse("O check-in realizado com sucesso!<br/> Paciente: %s <br /> Tratamento: %s" % (paciente.nome, at.instancia_tratamento.tratamento.descricao_basica))
            except Exception, e:
                return HttpResponse("Erro: %s" % str(e))
        else:
            return HttpResponse("Erro %s" % str(checkin_paciente_form.errors))
    else:
        checkin_paciente_form = CheckinPacienteForm()
    
    checkin_paciente_form.update_tratamentos(paciente)

    return render_to_response('ajax-checkin-paciente.html', {'paciente':paciente, 'form':checkin_paciente_form, 'lista':lista_atendimentos, 'erros':str(checkin_paciente_form.errors)})

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
    tratamento      = forms.ModelChoiceField(queryset=Tratamento.objects.all(), help_text ="Tratamento")
    data            = forms.DateField(help_text="Data")

    def __init__(self, *args, **kwargs):
        super(FiltroAtendimentosForm, self).__init__(*args, **kwargs)
        self.fields['data'].initial = datetime.date.today()

def retornaInfo(atendimento):

    info_str = ''
    
    try:
        tratamento = Tratamento.objects.get(id = atendimento.instancia_tratamento.tratamento.id)
        
        if tratamento.descricao_basica[:4] == "Manu" or tratamento.descricao_basica[:4] == "Prim":
            cont = len(Atendimento.objects.filter(paciente__id = atendimento.paciente.id, 
                instancia_tratamento__tratamento__id = tratamento.id, status='A'))  
           
            info_str = info_str + '[' + str(cont) + ']'
        if tratamento.descricao_basica[:4] == "Manu":
            tps = TratamentoPaciente.objects.filter(paciente = atendimento.paciente, status='A')
            tratamentos = ''
            for tp in tps:
                tratamentos = tratamentos + tp.tratamento.descricao_basica + ', '
            
            # retira o ', ' do final
            tratamentos = tratamentos[:-2]
            
            if tratamentos != "":
                info_str = info_str + '[' + tratamentos + ']'
            
            # inclui o [1a vez] se o paciente também está realizando um atendimento de 1a vez no mesmo dia.
            primeira_vez = Atendimento.objects.filter(paciente__id = atendimento.paciente.id, 
                instancia_tratamento__tratamento__descricao_basica__startswith = "Prime", instancia_tratamento__data = datetime.datetime.today())
            if len(primeira_vez) == 1:
                info_str = info_str + '[1a vez]'
            
    except Tratamento.DoesNotExist:
        pass

    manutencao = Atendimento.objects.filter(paciente__id = atendimento.paciente.id, 
        instancia_tratamento__tratamento__descricao_basica__startswith = "Manu", status='A')
    atendimentos = Atendimento.objects.filter(paciente__id = atendimento.paciente.id, 
        instancia_tratamento__tratamento = tratamento, status='A')

    if tratamento.descricao_basica in ["Sala 1", "Sala 2", "Sala 3", "Sala 4", "Sala 5"] and len(manutencao) == 4 and \
        len(atendimentos) == 0:
        info_str = info_str + '[1o tratamento]'

    try:
        voluntario = Voluntario.objects.filter(paciente__id = atendimento.paciente.id, ativo = True)
        if len(voluntario) > 0:
            info_str = info_str + '[' + voluntario[0].get_tipo_display() + ']'
    except Voluntario.DoesNotExist:
        pass
    
    try:
        prioridade =  DetalhePrioridade.objects.filter(paciente__id = atendimento.paciente.id)
        if len(prioridade) > 0:
            info_str = info_str + '[' + prioridade[0].get_tipo_display() + ']'
    except DetalhePrioridade.DoesNotExist:
        pass
    
    if atendimento.observacao_prioridade:   
        info_str = info_str + '[' + atendimento.observacao_prioridade + ']' 

    return info_str
    
    
class ConfirmacaoAtendimentoForm(forms.ModelForm):
    observacao = forms.CharField(required=False)
    nome = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly'}))
    info = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly'}))
    hora_chegada = forms.TimeField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly'}))   
    confirma = forms.BooleanField(required = False, label= 'Conf.')   

    def __init__(self, *args, **kwargs):
        
               
        super(ConfirmacaoAtendimentoForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['confirma','nome', 'hora_chegada', 'info', 'observacao']
        atendimento = kwargs.pop('instance')
        
        self.fields['nome'].initial = atendimento.paciente.nome
        self.fields['info'].initial = retornaInfo(atendimento)
        
        if atendimento.status == 'A':
            status = True
        else:
            status = False
        self.fields['confirma'].initial = status

    def save(self, commit=True):
        atendimento = super(ConfirmacaoAtendimentoForm, self).save(commit=False)
#        atendimento = forms.ModelForm.save(self, commit=True)
        prioridade_in = self.cleaned_data['confirma']
        if prioridade_in:
            atendimento.status = 'A'
        else:
            atendimento.status = 'C'
        if commit:
            atendimento.save()

    class Meta:
        model = Atendimento
        exclude = ['prioridade', 'instancia_tratamento', 'senha', 'observacao_prioridade', 'paciente', 'hora_atendimento', 'status']
          

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
            atendimentos = ConfirmacaoAtendimentoFormSet(queryset=Atendimento.objects.filter(instancia_tratamento__data=data,instancia_tratamento__tratamento=tratamento))

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
	prioridade = forms.BooleanField(required = False)

class ListagemGeralForm(forms.Form):

	def __init__(self, *args, **kwargs):
        	super(ListagemGeralForm, self).__init__(*args, **kwargs)

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
    tratamento = ''

    if request.method == 'POST':
        form_listagem = ImprimirListagemForm(request.POST)

        if form_listagem.is_valid():
            data_in = form_listagem.cleaned_data['data']
            tratamento_in = form_listagem.cleaned_data['tratamento']
            prioridade_in = form_listagem.cleaned_data['prioridade']

            tratamentos_marcados = InstanciaTratamento.objects.filter(tratamento__id  = tratamento_in, data = data_in)
            tratamento = Tratamento.objects.get(id=tratamento_in)
            for tratamentos in tratamentos_marcados:
                if not prioridade_in:
                    atendimentos_previstos = Atendimento.objects.filter(instancia_tratamento__id = tratamentos.id)
                else:
                    #atendimentos_previstos = Atendimento.objects.filter(instancia_tratamento__id = tratamentos.id)
                    atendimentos_previstos1 = Atendimento.objects.raw(""" select ate.* from atendimento_atendimento ate
	                                                                            join paciente_paciente pac
		                                                                            on pac.id = ate.paciente_id
	                                                                            join paciente_detalheprioridade dp
		                                                                            on pac.id = dp.paciente_id
	                                                                            where ate.instancia_tratamento_id = %d""" % tratamentos.id)
                    atendimentos_previstos2 = Atendimento.objects.raw(""" select ate.* from atendimento_atendimento ate
	                                                                        where ate.prioridade = True and ate.instancia_tratamento_id = %d
                                                                            order by hora_chegada;""" % tratamentos.id)

                    atendimentos_previstos = []
                    for at in atendimentos_previstos1:
                        atendimentos_previstos.append(at)
                    for at in atendimentos_previstos2:
                        atendimentos_previstos.append(at)

                for atendimento in atendimentos_previstos:
                    info_str = retornaInfo(atendimento)
                    retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': info_str, 'prioridade': False})
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
                mensagem_erro = 'Não há registros'
        else:
            mensagem_erro = 'Formulário inválido';

    i = itertools.count(1)
    for at in retorno:
        at["id"]=next(i)

    paginacao = Paginator(retorno,25) 
    if pagina == None:
        num_pagina = 1
    else:
        num_pagina = int(pagina)
    pagina_atual = paginacao.page(num_pagina)

	
    return render_to_response('listagem-diaria.html', {'form_listagem':form_listagem, 
                            'mensagem': mensagem_erro,
                            'pagina_atual':pagina_atual,
                            'tratamento':tratamento})

def exibir_listagem_geral(request):

    form_listagem = ListagemGeralForm()
    mensagem_erro = ''
    retorno = [];
    tratamento = ''

    if request.method == 'POST':
        form_listagem = ListagemGeralForm(request.POST)

        if form_listagem.is_valid():
            data_in = form_listagem.cleaned_data['data']

            tratamentos_marcados = InstanciaTratamento.objects.filter(data = data_in)
            atendimentos_previstos = Atendimento.objects.filter(instancia_tratamento__data = data_in).order_by('-hora_chegada')
            
            i = len(atendimentos_previstos)
            for atendimento in atendimentos_previstos:
                info_str = retornaInfo(atendimento)
                retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': info_str, 'prioridade': False, \
                    'sala': atendimento.instancia_tratamento.tratamento.descricao_basica, 'cont':i})
                i=i-1
                

            if not retorno:
                mensagem_erro = 'Não há registros'
        else:
            mensagem_erro = 'Formulário inválido';

    return render_to_response('listagem-diaria-geral.html', {'form_listagem':form_listagem, 
                            'mensagem': mensagem_erro,
                            'retorno':retorno,
                            'tratamento':tratamento})

def exibir_atendimentos_paciente(request, paciente_id, pagina = None):
	lista_atendimentos = Atendimento.objects.filter(paciente__id = paciente_id).order_by('-instancia_tratamento__data')

	mensagem_erro = ''
	retorno   = [];
	paciente = Paciente.objects.get(id=paciente_id)
	
	
	for atendimento in lista_atendimentos:
		retorno.append({'data':	atendimento.instancia_tratamento.data, 'tratamento': atendimento.instancia_tratamento.tratamento.descricao_basica, 			'hora_chegada': atendimento.hora_chegada, 'observacao': atendimento.observacao, 'status':atendimento.status})
		
		
	if not retorno:
		mensagem_erro = 'Não foi possível localizar usuário'
		
	paginacao = Paginator(retorno,45)
	if pagina == None:
		num_pagina = 1
	else:	
		num_pagina = int(pagina)
	pagina_atual = paginacao.page(num_pagina)	
	
	return render_to_response('lista-atendimentos.html',{'mensagem': mensagem_erro, 'pagina_atual': pagina_atual, 'paciente_id': paciente_id, \
	    'nome_paciente': paciente.nome })	
	
		
