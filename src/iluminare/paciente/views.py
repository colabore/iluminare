# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
#from django.forms import ModelForm, CharField, Select, DateField
from django import forms
from iluminare.paciente.models import *
from iluminare.atendimento.models import *
from iluminare.tratamento.models import *
from iluminare.voluntario.models import *


from django.db.models import Q

import iluminare.paciente.logic as paciente_logic
import iluminare.tratamento.logic as tratamento_logic
import iluminare.atendimento.logic as logic_atendimento
import iluminare.atendimento.views as view_atendimento

import datetime

from django.utils.encoding import smart_str


PRIORIDADE_CHOICES = (
    ('G', 'Grávida'),
    ('L', 'Lactante'),
    ('B', 'Baixa Imunidade'),
    ('C', 'Criança até 12 anos'))

class DetalhePrioridadeForm(forms.ModelForm):
    """ formulário para atualizar os detalhes caso o paciente seja prioritário. """
    paciente = None
    class Meta:
        model = DetalhePrioridade
        exclude = ('paciente', )

    def __init__(self, *args, **kwargs):
        super(DetalhePrioridadeForm, self).__init__(*args, **kwargs)
        self.fields['tipo'].label = 'Prioridade'
        self.fields['data_inicio'].label = 'Data Início (Grav / Lac)'


    def save(self):
        detalhe_prioridade = forms.ModelForm.save(self, commit=False)
        detalhe_prioridade.paciente = self.paciente
        # verifica se o objeto detalhe_prioridade está consistente
        paciente_logic.inserir_detalhe_prioridade(detalhe_prioridade)
        self.save_m2m()

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        exclude = ('saude', )

    def __init__(self, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)
        self.fields['acompanhante'].label = 'Acompanha'
        self.fields['observacao'].label = 'Observação (Tela Check-in)'
        self.fields['pais'].label = 'País'

    def save(self):
        paciente = forms.ModelForm.save(self)
        return paciente

def get_lista_tratamentos(tps):
    # Retorna a lista de tratamentos a partir da lista de TratamentoPaciente
    
    lista = []
    for tp in tps:
        lista.append(tp.tratamento)
    return lista

            
def get_lista_tratamentos_atuais(paciente):
    # Retorna a lista de tratamentos no formato TRATAMENTO_CHOICES
    # Exemplo: ['1','4']

    TRATAMENTOS_CHOICES = (
        (1, u'Sala 1'),
        (2, u'Sala 2'),
        (3, u'Sala 3'),
        (4, u'Sala 4'),
        (5, u'Sala 5'),
        (6, u'Manutenção'),
        (7, u'Sala 9')
    )

    lista = []    
    tps = list(TratamentoPaciente.objects.filter(Q(paciente=paciente.id), Q(status = 'A')))
    ts = get_lista_tratamentos(tps)    

    for t in TRATAMENTOS_CHOICES:
        tratamento = Tratamento.objects.get(descricao_basica = t[1])
        if tratamento in ts:
            lista.append(t[0])
    return lista


class TratamentoPacienteForm(forms.Form):
    # IMPORTANTE OBSERVAR QUE OS TRATAMENTOS DEVEM TER OS MESMOS NOMES QUE OS TRATAMENTOS QUE ESTÃO NA BASE
    # PODE SER MELHORADO.
    TRATAMENTOS_CHOICES = (
        (1, u'Sala 1'),
        (2, u'Sala 2'),
        (3, u'Sala 3'),
        (4, u'Sala 4'),
        (5, u'Sala 5'),
        (6, u'Manutenção'),
        (7, u'Sala 9')
    )
    tratamentos = forms.MultipleChoiceField(choices=TRATAMENTOS_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)

    def update(self, paciente):
        lista_tratamentos_atuais = get_lista_tratamentos_atuais(paciente)
        self.fields['tratamentos'].initial=lista_tratamentos_atuais

    def save(self, paciente):
        cod_ts = self.cleaned_data["tratamentos"]
        lista_tratamentos_novos = []
        # pega a lista de tratamentos a partir dos códigos
        for t in self.TRATAMENTOS_CHOICES:
            if str(t[0]) in cod_ts:
                tratamento = Tratamento.objects.get(descricao_basica = t[1])
                lista_tratamentos_novos.append(tratamento)
        tratamento_logic.encaminhar_paciente(paciente.id, lista_tratamentos_novos)

class TratamentoCadastroRapido(forms.Form):
    TRATAMENTOS_CHOICES_QUINTA = (
        (3, u'Sala 5'),
    )
    TRATAMENTOS_CHOICES_SEGUNDA = (
        (1, u'Primeira Vez'),
        (2, u'Manutenção')
    )
    TRATAMENTOS_CHOICES = (
        (1, u'Primeira Vez'),
        (2, u'Manutenção'),
        (3, u'Sala 5')
    )
    
    tratamentos = forms.MultipleChoiceField(choices=TRATAMENTOS_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
                
    def update(self):
        if datetime.date.today().weekday() == 0:
            self.fields['tratamentos'].choices = self.TRATAMENTOS_CHOICES_SEGUNDA 
            self.fields['tratamentos'].initial=['1','2']
        if datetime.date.today().weekday() == 3:
            self.fields['tratamentos'].choices = self.TRATAMENTOS_CHOICES_QUINTA
            self.fields['tratamentos'].initial=['3']
        else:
            self.fields['tratamentos'].choices = self.TRATAMENTOS_CHOICES
        
    def save(self, paciente):
        ts = self.cleaned_data["tratamentos"]
        
        if paciente == None:
            return []
        
        lista_dic = []
        for t in self.TRATAMENTOS_CHOICES:
            if str(t[0]) in ts:
                # realiza check-in para o tratamento.
                tratamento = Tratamento.objects.get(descricao_basica = t[1])
                dic = logic_atendimento.checkin_paciente(paciente, tratamento, False, None, False)
                lista_dic.append(dic)

        return lista_dic


def atualizar(request, paciente_id):
    paciente = Paciente.objects.get(pk=paciente_id)
    
    try:
        detalhe_prioridade = DetalhePrioridade.objects.get(paciente=paciente)
    except:
        detalhe_prioridade = None

    if request.method == "POST":
        form_paciente = PacienteForm(request.POST, instance=paciente)
        form_detalhe_prioridade = DetalhePrioridadeForm(request.POST, instance=detalhe_prioridade)
        form_tratamento_paciente = TratamentoPacienteForm(request.POST)
        if form_paciente.is_valid() and form_detalhe_prioridade.is_valid() and form_tratamento_paciente.is_valid():
            try:
                form_paciente.save()
                form_detalhe_prioridade.paciente = paciente
                form_detalhe_prioridade.save()
                form_tratamento_paciente.save(paciente)
                msg = "Paciente atualizado com sucesso."
            except paciente_logic.PacienteException as p_exc:
                msg = "Houve um erro ao atualizar o paciente (%s)" % p_exc
            except ValueError as v_exc:
                msg = "Houve um erro de validação dos dados (%s)" % v_exc
        else:
            msg = "Erro de validação dos dados."

    else:
        form_paciente = PacienteForm(instance=paciente)
        form_detalhe_prioridade = DetalhePrioridadeForm(instance=detalhe_prioridade)
        form_tratamento_paciente = TratamentoPacienteForm()
        form_tratamento_paciente.update(paciente)
        msg = ""

    return render_to_response('crud-paciente.html', {'form_paciente':form_paciente, 'form_detalhe_prioridade':form_detalhe_prioridade, \
        'form_tratamento_paciente':form_tratamento_paciente, 'mensagem':msg})
    

def incluir_paciente(request):

    
    if request.method == "POST":
        form_paciente = PacienteForm(request.POST)
        form_detalhe_prioridade = DetalhePrioridadeForm(request.POST)
        form_tratamento_paciente = TratamentoPacienteForm(request.POST)
        if form_paciente.is_valid() and form_detalhe_prioridade.is_valid() and form_tratamento_paciente.is_valid():
            try:
                paciente = form_paciente.save()
                form_detalhe_prioridade.paciente = paciente
                form_detalhe_prioridade.save()
                form_tratamento_paciente.save(paciente)
                msg = "Paciente cadastrado com sucesso."
            except paciente_logic.PacienteException as p_exc:
                msg = "Erro ao cadastrar o paciente (%s)." % p_exc
            except ValueError as v_exc:
                msg = "Erro de validação dos dados (%s)." % v_exc
        else:
            msg = "Erro de validação dos dados."
    else:
        form_paciente = PacienteForm()
        form_detalhe_prioridade = DetalhePrioridadeForm()
        form_tratamento_paciente = TratamentoPacienteForm()
        msg = ""
        

    return render_to_response('crud-paciente.html', {'form_paciente':form_paciente, 'form_detalhe_prioridade':form_detalhe_prioridade, \
        'form_tratamento_paciente':form_tratamento_paciente, 'mensagem':msg})

def ajax_consultar_paciente(request, paciente_id):
    try:
        paciente_dic = paciente_logic.consultar_paciente(int(paciente_id))
    except paciente_logic.PacienteException as p_exc:
        return HttpResponse ("Houve algum erro ao consultar pelo paciente (%s)" % p_exc)

    return render_to_response ('ajax-consultar-paciente.html', paciente_dic)

def ajaxlistarpessoas (request, nome):
    pacientes = None

    if request.method == 'GET' and nome != '':
        pacientes = paciente_logic.search(nome)
        
    if not pacientes:
        pacientes = []

    lista = paciente_logic.format_table(pacientes)

    return render_to_response ('ajax-listar-pessoas.html', {'lista':lista})

def dialog_detalhe(request, paciente_id, tratamento_id):
    lista = TratamentoPaciente.objects.filter(tratamento__id=tratamento_id, paciente__id=paciente_id)
    
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

def cadastro_rapido_paciente(request):
    if request.method == "POST":
        form = PacienteForm(request.POST)
        trat_form = TratamentoCadastroRapido(request.POST)
        if form.is_valid() and trat_form.is_valid():
            try:
                paciente = form.save()
                lista = []
                dic_paciente = None
                if paciente:
                    dic_paciente = {'sucesso':True, 'mensagem':'Paciente cadastrado com sucesso.'}
                else:
                    dic_paciente = {'sucesso':False, 'mensagem':'Erro no cadastro do paciente.'}
                
                lista.append(dic_paciente)
                lista_dics_atends = trat_form.save(paciente)
                lista = lista + lista_dics_atends 

                return render_to_response ('cadastro-rapido-paciente-resultado.html', {'paciente': paciente, 'lista_dics':lista})
    
            except Exception, e:
                return HttpResponse("Erro: %s" % e)
        else:
            return HttpResponse("Erro %s" % str(form.errors) + str(trat_form.errors))
            
    else:
        form = PacienteForm()
        trat_form = TratamentoCadastroRapido()
        trat_form.update()
        
    return render_to_response ('cadastro-rapido-paciente.html', {'form': form, 'trat_form': trat_form})

