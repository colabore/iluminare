# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django import forms
from iluminare.voluntario.models import *
from django.forms.models import modelformset_factory, BaseModelFormSet

from django.utils.functional import curry, wraps

import datetime
from datetime import date

class voluntarioForm(forms.ModelForm):
	class Meta:
		model = Voluntario

def render(request):
	if request.method == "POST":
		form_voluntario = voluntarioForm(request.POST)
		form_voluntario.save()
		msg = "Novo voluntario cadastrado com sucesso"
	else:
		form_voluntario = voluntarioForm()
		msg = ""

	return render_to_response('add-voluntario.html',{'form_voluntario': form_voluntario, 'msg': msg})


def index(request):
	return render_to_response('index.html')

class FiltroPontoForm(forms.Form):

    def __init__(self, *args, **kwargs):
        	super(FiltroPontoForm, self).__init__(*args, **kwargs)

    data = forms.DateField(initial = datetime.date.today)

class FiltroPontoConsultaForm(forms.Form):

    def __init__(self, *args, **kwargs):
        	super(FiltroPontoConsultaForm, self).__init__(*args, **kwargs)

    data = forms.DateField(initial = datetime.date.today)


class PontoForm(forms.ModelForm):

    confirma = forms.BooleanField(required = False, label= 'Conf.')
    nome = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'30'}))
    tipo_vol = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'9'}))
    hora_inicio = forms.TimeField(label='Inicio',required=False, widget=forms.TextInput(attrs={'size':'6'}))
    hora_final = forms.TimeField(label='Final',required=False, widget=forms.TextInput(attrs={'size':'6'}))
    data_registro_ponto = None
    
    class Meta:
        model = Voluntario
        exclude = ['paciente', 'data_inicio', 'data_fim', 'ativo','observacao', 'tipo']

    def __init__(self, *args, **kwargs):
        super(PontoForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['confirma','nome', 'tipo_vol','hora_inicio', 'hora_final']
        voluntario = kwargs.pop('instance')
        
        # CORRIGIR
        # por enquanto está funcionando com data fixa.
        # preciso aprender a passar o parâmetro para o INIT().
        #data=data_registro_ponto
#        data = kwargs.pop('data')
        
        self.fields['nome'].initial = voluntario.paciente.nome
        tipo_str = ''
        if voluntario.tipo == 'T':
            tipo_str = 'Trabalhador'
        elif voluntario.tipo == 'C':
            tipo_str = 'Colaborador'
        
        self.fields['tipo_vol'].initial = tipo_str
        
        trabalho = Trabalho.objects.filter(voluntario = voluntario, data=self.data_registro_ponto)
        
        if len(trabalho) == 1:
            self.fields['confirma'].initial = True
            self.fields['hora_inicio'].initial = trabalho[0].hora_inicio
            self.fields['hora_final'].initial = trabalho[0].hora_final

    def save(self, commit=True):
        voluntario = super(PontoForm, self).save(commit=False)
        confirma_in = self.cleaned_data['confirma']
        hora_inicio_in = self.cleaned_data['hora_inicio']
        hora_final_in = self.cleaned_data['hora_final']
        
        # CORRIGIR        
        # por enquanto está funcionando com data fixa.
        # preciso aprender a passar o parâmetro para o save().
        #data=global_data_registro_ponto
        
        if confirma_in:
            trabalhos = Trabalho.objects.filter(voluntario = voluntario, data=self.data_registro_ponto)
            if len(trabalhos) == 0:
                funcao = Funcao.objects.get(descricao='Geral')
                trabalho = Trabalho(voluntario = voluntario, data=self.data_registro_ponto, funcao=funcao)
            elif len(trabalhos) == 1:
                trabalho = trabalhos[0]
                
            trabalho.hora_inicio = hora_inicio_in
            trabalho.hora_final = hora_final_in

            if trabalho.data == self.data_registro_ponto:
                trabalho.save()
        else:
            trabalhos = Trabalho.objects.filter(voluntario = voluntario, data=self.data_registro_ponto)
            if len(trabalhos) == 1:
                trabalhos[0].delete()

        
PontoFormSet = modelformset_factory(Voluntario, extra=0, form=PontoForm)

def registra_ponto(request):

    if request.method == "POST":
        filtro_form = FiltroPontoForm(request.POST)

        if filtro_form.is_valid():
            registro_ponto = filtro_form.cleaned_data['data']
            PontoForm.data_registro_ponto = registro_ponto
            
            voluntarios = None
            try:
                voluntarios = PontoFormSet(request.POST)
            except:
                voluntarios = PontoFormSet(queryset=Voluntario.objects.filter(ativo=True))
                
            if voluntarios.is_valid():
                voluntarios.save()
                #voluntarios = PontoFormSet(queryset=Voluntario.objects.filter(ativo=True))

    else:
        filtro_form = FiltroPontoForm()
        voluntarios = None
    
    return render_to_response('registra_ponto.html', {'filtro_form':filtro_form, 'voluntarios':voluntarios,\
        'mensagem': voluntarios and voluntarios.errors})
    

def consulta_ponto(request):

    form = FiltroPontoConsultaForm()
    mensagem_erro = ''
    retorno = [];

    if request.method == "POST":
        form = FiltroPontoConsultaForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data['data']
            
            voluntarios = Voluntario.objects.filter(ativo = True)
            
            for v in voluntarios:
                trabalho = Trabalho.objects.filter(voluntario = v, data=data)
                hc = '-'
                hs = '-'
                if len(trabalho) == 1:
                    
                    if trabalho[0].hora_inicio:
                        hc = trabalho[0].hora_inicio
                    if trabalho[0].hora_final:
                        hs = trabalho[0].hora_final
                    
                    retorno.append({'nome': v.paciente.nome, 'tipo': v.tipo, 'presente': 'P', \
                        'hora_chegada': hc, 'hora_saida': hs})
                else:
                    retorno.append({'nome': v.paciente.nome, 'tipo': v.tipo, 'presente': 'F', \
                        'hora_chegada': hc, 'hora_saida': hs})
            
        else:
            mensagem_erro = 'Formulário inválido'

    
    return render_to_response('consulta_ponto.html', {'form':form, 'retorno':retorno,'mensagem': mensagem_erro})
    


