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

class PontoForm(forms.ModelForm):

    confirma = forms.BooleanField(required = False, label= 'Conf.')
    nome = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'30'}))
    tipo_vol = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'9'}))
    hora_inicio = forms.TimeField(label='Inicio',required=False, widget=forms.TextInput(attrs={'size':'6'}))
    hora_final = forms.TimeField(label='Final',required=False, widget=forms.TextInput(attrs={'size':'6'}))

    
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
        data=date(2011,10,27)
#        data = kwargs.pop('data')
        
        self.fields['nome'].initial = voluntario.paciente.nome
        tipo_str = ''
        if voluntario.tipo == 'T':
            tipo_str = 'Trabalhador'
        elif voluntario.tipo == 'C':
            tipo_str = 'Colaborador'
        
        self.fields['tipo_vol'].initial = tipo_str
        
        trabalho = Trabalho.objects.filter(voluntario = voluntario, data=data)
        
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
        data=date(2011,10,27)
        
        if confirma_in:
            trabalhos = Trabalho.objects.filter(voluntario = voluntario, data=data)
            if len(trabalhos) == 0:
                funcao = Funcao.objects.get(descricao='Geral')
                trabalho = Trabalho(voluntario = voluntario, data=data, funcao=funcao)
            elif len(trabalhos) == 1:
                trabalho = trabalhos[0]
                
            trabalho.hora_inicio = hora_inicio_in
            trabalho.hora_final = hora_final_in
            trabalho.save()
        else:
            trabalhos = Trabalho.objects.filter(voluntario = voluntario, data=data)
            if len(trabalhos) == 1:
                trabalhos[0].delete()

        
PontoFormSet = modelformset_factory(Voluntario, extra=0, form=PontoForm)

def registra_ponto(request):

    if request.method == "POST":
        filtro_form = FiltroPontoForm(request.POST)
        voluntarios = PontoFormSet(request.POST)

        if filtro_form.is_valid() and voluntarios.is_valid:
            data	   = filtro_form.cleaned_data['data']
            voluntarios.save()
            voluntarios = PontoFormSet(queryset=Voluntario.objects.filter(ativo=True))

    else:
        filtro_form = FiltroPontoForm()
        voluntarios = PontoFormSet(queryset=Voluntario.objects.filter(ativo=True))
    
    return render_to_response('registra_ponto.html', {'filtro_form':filtro_form, 'voluntarios':voluntarios,\
        'mensagem':voluntarios.errors})
    


