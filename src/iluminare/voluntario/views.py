# -*- coding: utf-8 -*-
import datetime
import csv
from datetime import date

from django import forms
from django.shortcuts import render_to_response
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.utils.functional import curry, wraps
from django.http import HttpResponse
from django.utils.encoding import smart_str

from iluminare.voluntario.models import *
from iluminare.voluntario.models import Trabalho

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

class VoluntarioIncluirForm(forms.ModelForm):
    class Meta:
        model = Voluntario
        exclude = ('data_inicio','data_fim',)

    def __init__(self, *args, **kwargs):
        super(VoluntarioIncluirForm, self).__init__(*args, **kwargs)
        self.fields['observacao'].widget.attrs['rows'] = 4

    def save(self):
        voluntario = forms.ModelForm.save(self)
        return voluntario


def index(request):
	return render_to_response('index.html')

class FiltroPontoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        	super(FiltroPontoForm, self).__init__(*args, **kwargs)

    DIA_ESTUDO = (
        ('T', 'Terça'),
        ('X', 'Sexta'),
        ('O', 'Todos'),
    )

    data        = forms.DateField(initial = datetime.date.today)
    dia_estudo  = dia_estudo = forms.ChoiceField(required=False, choices=DIA_ESTUDO, initial='O')

class FiltroPontoConsultaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        	super(FiltroPontoConsultaForm, self).__init__(*args, **kwargs)

    data = forms.DateField(initial = datetime.date.today)

class FiltroRelatiorioTrabalhosForm(forms.Form):
    DIA_SEMANA = (
        ('2', 'Segunda'),
        ('3', 'Terça'),
        ('5', 'Quinta'),
        ('6', 'Sexta'),
    )

    def __init__(self, *args, **kwargs):
        	super(FiltroRelatiorioTrabalhosForm, self).__init__(*args, **kwargs)

    data = datetime.date.today() - datetime.timedelta(30)
    data_inicial = forms.DateField(initial = data)
    data_final = forms.DateField(initial = datetime.date.today())
    dia_semana =  forms.ChoiceField(required=False, choices=DIA_SEMANA, initial='3')

class FiltroConsultaVoluntariosForm(forms.Form):
    TIPO = (
        ('T', 'Trabalhador'),
        ('C', 'Colaborador'),
        ('A', 'Apoio'),
        ('O', 'Todos'),
    )

    ATIVO = (
        ('S', 'Sim'),
        ('N', 'Não'),
        ('T', 'Todos'),
    )

    DIA_ESTUDO = (
        ('T', 'Terça'),
        ('X', 'Sexta'),
        ('O', 'Todos'),
    )


    def __init__(self, *args, **kwargs):
        	super(FiltroConsultaVoluntariosForm, self).__init__(*args, **kwargs)

    tipo =  forms.ChoiceField(required=False, choices=TIPO, initial='O')
    ativo =  forms.ChoiceField(required=False, choices=ATIVO, initial='T')
    dia_estudo = forms.ChoiceField(required=False, choices=DIA_ESTUDO, initial='O')


FiltroRelatiorioTrabalhosForm
class FiltroRelatiorioTercasForm(forms.Form):

    TIPO = (
        ('T', 'Trabalhador'),
        ('C', 'Colaborador')
    )

    def __init__(self, *args, **kwargs):
        	super(FiltroRelatiorioTercasForm, self).__init__(*args, **kwargs)

    tipo_voluntario =  forms.ChoiceField(required=True, choices=TIPO)

class PontoForm(forms.ModelForm):
    STATUS_TRABALHO = Trabalho.STATUS

    #confirma = forms.BooleanField(required = False, label= 'Conf.')
    # pf (Presença ou Falta)
    pf = forms.ChoiceField(required=False, choices=STATUS_TRABALHO, initial='NI', label='P / F')
    nome = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'30'}))
    tipo_vol = forms.CharField(required=False, label='Tipo', widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'9'}))
    hora_inicio = forms.TimeField(label='Inicio',required=False, widget=forms.TextInput(attrs={'size':'6'}))
    hora_final = forms.TimeField(label='Final',required=False, widget=forms.TextInput(attrs={'size':'6'}))
    info_voluntario = forms.CharField(required=False, label='Info', widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'18'}))
    data_registro_ponto = None
    dia_estudo = None

    class Meta:
        model = Voluntario
        exclude = ['paciente', 'data_inicio', 'data_fim', 'ativo','observacao', 'tipo', 'dia_estudo']

    def __init__(self, *args, **kwargs):
        super(PontoForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['nome', 'tipo_vol', 'info_voluntario','pf','hora_inicio', 'hora_final']
        voluntario = kwargs.pop('instance')

        self.fields['nome'].initial = voluntario.paciente.nome
        tipo_str = ''
        if voluntario.tipo == 'T':
            tipo_str = 'Trabalhador'
        elif voluntario.tipo == 'C':
            tipo_str = 'Colaborador'
        elif voluntario.tipo == 'A':
            tipo_str = 'Apoio'

        self.fields['tipo_vol'].initial = tipo_str
        self.fields['info_voluntario'].initial = voluntario.observacao

        trabalho = Trabalho.objects.filter(voluntario = voluntario, data=self.data_registro_ponto)

        if len(trabalho) == 1:
            if trabalho[0].status:
                self.fields['pf'].initial = trabalho[0].status
            else:
                self.fields['pf'].initial = 'PR'
            self.fields['hora_inicio'].initial = trabalho[0].hora_inicio
            self.fields['hora_final'].initial = trabalho[0].hora_final
        else:
            self.fields['pf'].initial = 'NI'

    def save(self, commit=True):
        voluntario = super(PontoForm, self).save(commit=False)
        #confirma_in = self.cleaned_data['confirma']
        pf_in = self.cleaned_data['pf']
        hora_inicio_in = self.cleaned_data['hora_inicio']
        hora_final_in = self.cleaned_data['hora_final']

        trabalhos = Trabalho.objects.filter(voluntario = voluntario, data=self.data_registro_ponto)
        if len(trabalhos) == 0:
            funcao = Funcao.objects.get(descricao='Geral')
            trabalho = Trabalho(voluntario = voluntario, data=self.data_registro_ponto, funcao=funcao)
        elif len(trabalhos) == 1:
            trabalho = trabalhos[0]

        trabalho.hora_inicio = hora_inicio_in
        trabalho.hora_final = hora_final_in
        trabalho.status = pf_in
        if trabalho.data == self.data_registro_ponto:
            trabalho.save()


PontoFormSet = modelformset_factory(Voluntario, extra=0, form=PontoForm)
def registra_ponto(request):
    debug = ''
    mensagem_sucesso = ''
    mensagem_erro = ''
    mensagem = ''
    if request.method == 'POST':
        filtro_form = FiltroPontoForm(request.POST)
        if filtro_form.is_valid():
            if 'pesquisar' in request.POST:
                PontoForm.data_registro_ponto = filtro_form.cleaned_data['data']
                PontoForm.dia_estudo = filtro_form.cleaned_data['dia_estudo']
                if PontoForm.dia_estudo == 'T' or PontoForm.dia_estudo == 'X':
                    voluntarios = PontoFormSet(queryset=Voluntario.objects.filter(ativo=True, dia_estudo=PontoForm.dia_estudo))
                else:
                    voluntarios = PontoFormSet(queryset=Voluntario.objects.filter(ativo=True))

        if 'salvar' in request.POST:
            try:
                voluntarios = PontoFormSet(request.POST)
            except:
                voluntarios = None

            if voluntarios.is_valid():
                voluntarios.save()
                mensagem_sucesso = "Dados atualizados com sucesso."
                mesagem = ''
                #voluntarios = PontoFormSet(queryset=Voluntario.objects.filter(ativo=True))
            else:
                mensagem_erro = "Dados não atualizados. Verificar campos com erro."
                mensagem = voluntarios.errors

    else:
        filtro_form = FiltroPontoForm()
        voluntarios = None

    return render_to_response('registra_ponto.html', {'filtro_form':filtro_form, 'voluntarios':voluntarios,\
        'mensagem': mensagem, 'debug': debug, 'titulo': 'REGISTRAR PONTOS',
        'mensagem_sucesso':mensagem_sucesso, 'mensagem_erro':mensagem_erro})


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


    return render_to_response('consulta_ponto.html', {'form':form, 'retorno':retorno,'mensagem': mensagem_erro,
                                'titulo':'CONSULTAR PONTOS'})


def atualizar(request, voluntario_id):
    voluntario = Voluntario.objects.get(pk=voluntario_id)
    nome_paciente = voluntario.paciente.nome
    mensagem_sucesso = ''
    mensagem_erro = ''
    mensagem = ''
    if request.method == "POST":
        form_voluntario = VoluntarioForm(request.POST, instance=voluntario)
        if form_voluntario.is_valid():
            try:
                form_voluntario.save()
                mensagem_sucesso = "Voluntário atualizado com sucesso."
            except v_exc:
                mensagem_erro = "Erro na atualização do voluntário... " + v_exc
        else:
            mensagem_erro = "Voluntário não atualizado. Erro de validação dos dados."

    else:
        form_voluntario = VoluntarioForm(instance=voluntario)
        mensagem = ''

    return render_to_response('crud-voluntario.html', {'form_voluntario':form_voluntario, 'mensagem':mensagem,
        'nome_paciente':nome_paciente, 'titulo': 'ATUALIZAR VOLUNTÁRIO', 'mensagem_sucesso': mensagem_sucesso,
        'mensagem_erro':mensagem_erro})

def incluir_voluntario(request):
    mensagem_sucesso = ''
    mensagem_erro = ''
    mensagem = ''
    if request.method == "POST":
        form_voluntario = VoluntarioIncluirForm(request.POST)
        if form_voluntario.is_valid():
            try:
                paciente = form_voluntario.cleaned_data['paciente']
                voluntarios = Voluntario.objects.filter(paciente = paciente)
                if not voluntarios:
                    form_voluntario.save()
                    mensagem_sucesso = "Voluntário incluído com sucesso."
                else:
                    mensagem_erro = "Este paciente já é um voluntário. Verificar se está inativo."
            except v_exc:
                mensagem_erro = "Erro na atualização do voluntário... " + v_exc
        else:
            mensagem_erro = "Erro de validação dos dados. Verificar se todos os campos foram preenchidos corretamente."

    else:
        form_voluntario = VoluntarioIncluirForm()
        mensagem = ""

    return render_to_response('incluir-voluntario.html', {'form_voluntario':form_voluntario, 'mensagem':mensagem,
                                'titulo': 'INCLUIR VOLUNTÁRIO', 'mensagem_sucesso': mensagem_sucesso,
                                'mensagem_erro':mensagem_erro})


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

        dict_voluntario = {}
        dict_voluntario['voluntario'] = v
        for trabalho in trabalhos:
            dict_voluntario[trabalho.data] = trabalho
            if trabalho.data not in lista_datas:
                lista_datas.append(trabalho.data)

        lista_geral.append(dict_voluntario)

    # inicializando a lista de totais inferior.
    lista_totais = [0]*(len(lista_datas)+1)

    #ordenando as datas e preparando rótulos
    lista_datas.sort()

    # preparando a lista de rótulos
    lista_rotulos.append("Voluntário")
    lista_rotulos.append("Tipo")
    for data in lista_datas:
        lista_rotulos.append(str(data))
    lista_rotulos.append("Total")

    for item in lista_geral:
        linha = []
        linha.append(smart_str(item['voluntario'].paciente.nome))
        linha.append(item['voluntario'].tipo)
        cont = 0
        i=0
        for data in lista_datas:
            if data in item.keys():
                linha.append(item[data].status)
                if item[data].status == 'PR':
                    cont +=1
                    lista_totais[i] +=1
                    lista_totais[-1] +=1
            else:
                linha.append("FA")
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
        'data_final_ordinal':data_final_ordinal,'dia_semana_int':dia_semana_int, 'titulo': 'RELATÓRIO DE TRABALHOS'})

def relatorio_trabalhos_csv(request, data_inicial_ordinal, data_final_ordinal, dia_semana_int):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=relatorio_trabalhos.csv'

    writer = csv.writer(response)
    lista_rotulos, lista_dados, mensagem = relatorio_trabalhos_geral(data_inicial_ordinal, data_final_ordinal, dia_semana_int)
    writer.writerow(lista_rotulos)
    for element in lista_dados:
        writer.writerow(element)

    return response

def relatorio_voluntarios_geral(tipo, ativo, dia_estudo):
    mensagem = ''
    voluntarios = Voluntario.objects.all()
    if tipo != 'O':
        voluntarios = voluntarios.filter(tipo = tipo)
    if ativo != 'T':
        ativo_param = True
        if ativo == 'N':
            ativo_param = False
        voluntarios = voluntarios.filter(ativo = ativo_param)
    if dia_estudo != 'O':
        voluntarios = voluntarios.filter(dia_estudo = dia_estudo)
    return voluntarios, mensagem


def relatorio_voluntarios(request):
    form = FiltroConsultaVoluntariosForm()
    mensagem = ''
    voluntarios = []

    if request.method == "POST":
        form = FiltroConsultaVoluntariosForm(request.POST)

        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            ativo = form.cleaned_data['ativo']
            dia_estudo = form.cleaned_data['dia_estudo']
            voluntarios, mensagem = relatorio_voluntarios_geral(tipo, ativo, dia_estudo)
            if len(voluntarios) == 0:
                mensagem = 'Nenhum registro'
        else:
            mensagem = 'Formulário inválido'

    return render_to_response('relatorio-voluntarios.html', {'form':form, 'mensagem': mensagem, \
        'voluntarios':voluntarios, 'titulo': 'LISTAR VOLUNTÁRIOS'})

def relatorio_voluntarios_csv(request, tipo, ativo, dia_estudo):
    """
        Falta corrigir..
    """
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=relatorio_voluntarios.csv'

    writer = csv.writer(response)
    lista_rotulos, lista_dados, mensagem = relatorio_voluntario_geral(tipo, ativo, dia_estudo)
    writer.writerow(lista_rotulos)
    for element in lista_dados:
        writer.writerow(element)

    return response


def relatorio_tercas_geral(tipo):
    """
    O único parâmetro é o perfil do voluntário.
    Nesse caso, só teremos Trabalhadores ou Colaboradores.

    O objetivo é gerar um relatório de presenças nas terças para o mês atual,
    o mês anterior e o mês retrasado.

    """
    mensagem = ''
    lista_rotulos = []
    lista_dados = []
    lista_totais = []

    voluntarios = Voluntario.objects.filter(ativo = True, tipo = tipo)

    lista_geral = []
    lista_datas = []

    ### identificando os meses #####
    hoje = datetime.datetime.today()
    mes_atual = hoje.month
    ano_atual = hoje.year

    mes_ant = mes_atual-1
    ano_ant = ano_atual
    if mes_ant == 0:
        mes_ant = 12
        ano_ant = ano_atual -1

    mes_ret = mes_atual-2
    ano_ret = ano_atual

    if mes_ret == 0:
        mes_ret = 12
        ano_ret = ano_atual -1
    elif mes_ret == -1:
        mes_ret = 11
        ano_ret = ano_atual -1

    ################################

    data_inicial = datetime.datetime(ano_ret, mes_ret, 1)
    data_final = hoje
    for v in voluntarios:
        trabalhos = Trabalho.objects.filter(voluntario = v, data__gte=data_inicial, \
            data__lte=data_final, data__week_day = 3)
        dic_voluntario = {}
        dic_voluntario['voluntario'] = v
        for trabalho in trabalhos:
            dic_voluntario[trabalho.data] = trabalho
            if trabalho.data not in lista_datas:
                lista_datas.append(trabalho.data)

        lista_geral.append(dic_voluntario)

    # Cria uma lista com zeros. Exemplo: [0,0,0,0]
    lista_totais = [0]*(len(lista_datas)+1)

    ### ordenando as datas e preparando rótulos ######
    lista_datas.sort()
    lista_rotulos.append("Voluntário")
    data1 = None
    mes1 = None
    if lista_datas:
        data1 = lista_datas[0]
        mes1 = data1.month

    for data in lista_datas:
        if data.month != mes1:
            lista_rotulos.append("Relatório do mês "+str(mes1)+" [P, FA, F]")
            mes1 = data.month
        lista_rotulos.append(str(data))

    if lista_datas:
        mes = lista_datas[-1].month
        lista_rotulos.append("Relatório do mês "+str(mes)+"[P, FA, F]")

    lista_rotulos.append("Relatório")

    ##################################################

    for dic_vol in lista_geral:
        linha = []
        linha.append(smart_str(dic_vol['voluntario'].paciente.nome))
        cont_presencas = 0
        cont_faltas_abonadas = 0
        cont_faltas = 0

        data1 = None
        mes1 = None
        if lista_datas:
            data1 = lista_datas[0]
            mes1 = data1.month

        for data in lista_datas:
            if data.month != mes1:
                linha.append("["+str(cont_presencas)+", "+str(cont_faltas_abonadas)+", "+str(cont_faltas)+"]")
                mes1 = data.month
                cont_presencas = 0
                cont_faltas_abonadas = 0
                cont_faltas = 0

            if data in dic_vol.keys():
                trabalho = dic_vol[data]
                if trabalho.status == None or trabalho.status == 'PR':
                    linha.append("P")
                    cont_presencas +=1
                elif trabalho.status == 'FS' or trabalho.status == 'FV' or trabalho.status == 'FL':
                    linha.append("J")
                    cont_faltas_abonadas +=1
                else:
                    linha.append("F")
                    cont_faltas +=1
            else:
                linha.append("F")
                cont_faltas += 1

        linha.append("["+str(cont_presencas)+", "+str(cont_faltas_abonadas)+", "+str(cont_faltas)+"]")
        linha.append("Relatório..")

        lista_dados.append(linha)

    return lista_rotulos, lista_dados, mensagem

def relatorio_tercas(request):
    form = FiltroRelatiorioTercasForm()
    mensagem = ''
    lista_rotulos = []
    lista_dados = []
#    lista_totais = []
    tipo_voluntario = ''

    if request.method == "POST":
        form = FiltroRelatiorioTercasForm(request.POST)

        if form.is_valid():
            tipo_voluntario = form.cleaned_data['tipo_voluntario']

            lista_rotulos, lista_dados, mensagem = relatorio_tercas_geral(tipo_voluntario)

        else:
            mensagem = 'Formulário inválido'

    return render_to_response('relatorio-tercas.html', {'form':form, 'lista_rotulos':lista_rotulos,\
        'lista_dados':lista_dados,'mensagem': mensagem, 'tipo_voluntario':tipo_voluntario})

def relatorio_tercas_csv(request, tipo_voluntario):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=relatorio_tercas.csv'

    writer = csv.writer(response)
    lista_rotulos, lista_dados, mensagem = relatorio_tercas_geral(tipo_voluntario)
    writer.writerow(lista_rotulos)
    for element in lista_dados:
        writer.writerow(element)

    return response
