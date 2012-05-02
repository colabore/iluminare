# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django import forms
from iluminare.voluntario.models import *
from django.forms.models import modelformset_factory, BaseModelFormSet

from django.utils.functional import curry, wraps

import datetime
from datetime import date
import csv
from django.http import HttpResponse

from django.utils.encoding import smart_str


class VoluntarioForm(forms.ModelForm):
    class Meta:
        model = Voluntario
        exclude = ('paciente','data_inicio','data_fim',)

    def __init__(self, *args, **kwargs):
        super(VoluntarioForm, self).__init__(*args, **kwargs)

        voluntario = kwargs.pop('instance')

        self.fields['observacao'].widget.attrs['rows'] = 4

    def save(self):
        voluntario = forms.ModelForm.save(self)
        return voluntario

def render(request):
	if request.method == "POST":
		form_voluntario = VoluntarioForm(request.POST)
		form_voluntario.save()
		msg = "Novo voluntario cadastrado com sucesso"
	else:
		form_voluntario = VoluntarioForm()
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

class FiltroRelatiorioTrabalhosForm(forms.Form):

    DIA_SEMANA = (
        ('2', 'Segunda'),
        ('3', 'Terça'),
        ('5', 'Quinta'),
    )


    def __init__(self, *args, **kwargs):
        	super(FiltroRelatiorioTrabalhosForm, self).__init__(*args, **kwargs)

    data = datetime.date.today() - datetime.timedelta(30)
    data_inicial = forms.DateField(initial = data)
    data_final = forms.DateField(initial = datetime.date.today())
    dia_semana =  forms.ChoiceField(required=False, choices=DIA_SEMANA, initial='3')


FiltroRelatiorioTrabalhosForm

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


def atualizar(request, voluntario_id):
    voluntario = Voluntario.objects.get(pk=voluntario_id)
    nome_paciente = voluntario.paciente.nome
    
    if request.method == "POST":
        form_voluntario = VoluntarioForm(request.POST, instance=voluntario)
        if form_voluntario.is_valid():
            try:
                form_voluntario.save()
                msg = "Voluntário atualizado com sucesso."
            except v_exc:
                msg = "Erro na atualização do voluntário... " + v_exc
        else:
            msg = "Erro de validação dos dados."

    else:
        form_voluntario = VoluntarioForm(instance=voluntario)
        msg = ""

    return render_to_response('crud-voluntario.html', {'form_voluntario':form_voluntario, 'mensagem':msg, \
        'nome_paciente':nome_paciente})

def relatorio_trabalhos_geral(data_inicial_ordinal, data_final_ordinal, dia_semana_int):
    mensagem = ''
    lista_rotulos = []
    lista_dados = []
    lista_totais = []

    voluntarios = Voluntario.objects.filter(ativo = True)
    
    lista_geral = []
    lista_datas = []
    
    data_inicial = datetime.date.fromordinal(int(data_inicial_ordinal))
    data_final = datetime.date.fromordinal(int(data_final_ordinal))
    
    for v in voluntarios:
        if dia_semana_int != 9:
            trabalhos = Trabalho.objects.filter(voluntario = v, data__gte=data_inicial, \
                data__lte=data_final, data__week_day = dia_semana_int)
        else:
            trabalhos = Trabalho.objects.filter(voluntario = v, data__gte=data_inicial, \
                data__lte=data_final)

        lista_voluntario = []
        lista_voluntario.append(v)
        for trabalho in trabalhos:
            lista_voluntario.append(trabalho.data)
            if trabalho.data not in lista_datas:
                lista_datas.append(trabalho.data)
        
        lista_geral.append(lista_voluntario)
    
    lista_totais = [0]*(len(lista_datas)+1)
    #ordenando as datas e preparando rótulos
    lista_datas.sort()
    lista_rotulos.append("Voluntário")
    lista_rotulos.append("Tipo")
    for data in lista_datas:
        lista_rotulos.append(str(data))
    
    lista_rotulos.append("Total")
    
    for item in lista_geral:
        linha = []
        linha.append(smart_str(item[0].paciente.nome))
        linha.append(item[0].tipo)
        cont = 0
        i=0
        for data in lista_datas:
            if data in item:
                linha.append("P")
                cont +=1
                lista_totais[i] +=1
                lista_totais[-1] +=1
            else:
                linha.append("F")
            i+=1
        
        linha.append(str(cont))
        lista_dados.append(linha)
        
    lista_totais = ["Total","-"] + lista_totais
    lista_dados.append(lista_totais)

    return lista_rotulos, lista_dados, mensagem

   
def relatorio_trabalhos(request):
    """
        
    """
    form = FiltroRelatiorioTrabalhosForm()
    mensagem = ''
    lista_rotulos = []
    lista_dados = []
    lista_totais = []
    data_inicial_ordinal = ''
    data_final_ordinal = ''
    dia_semana_int = 9

    if request.method == "POST":
        form = FiltroRelatiorioTrabalhosForm(request.POST)

        if form.is_valid():
            data_inicial = form.cleaned_data['data_inicial']
            data_final = form.cleaned_data['data_final']
            dia_semana = form.cleaned_data['dia_semana']

            data_inicial_ordinal = data_inicial.toordinal()
            data_final_ordinal = data_final.toordinal()

            try:
                dia_semana_int = int(dia_semana)
            except:
                dia_semana_int = 9

            lista_rotulos, lista_dados, mensagem = relatorio_trabalhos_geral(data_inicial_ordinal, data_final_ordinal, dia_semana_int)

        else:
            mensagem = 'Formulário inválido'

    return render_to_response('relatorio-trabalhos.html', {'form':form, 'lista_rotulos':lista_rotulos,\
        'lista_dados':lista_dados,'mensagem': mensagem, 'data_inicial_ordinal':data_inicial_ordinal, \
        'data_final_ordinal':data_final_ordinal,'dia_semana_int':dia_semana_int})

def relatorio_trabalhos_csv(request, data_inicial_ordinal, data_final_ordinal, dia_semana_int):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=relatorio_trabalhos.csv'

    writer = csv.writer(response)
    lista_rotulos, lista_dados, mensagem = relatorio_trabalhos_geral(data_inicial_ordinal, data_final_ordinal, dia_semana_int)
    writer.writerow(lista_rotulos)
    for element in lista_dados:
        writer.writerow(element)

    return response
