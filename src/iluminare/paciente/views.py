# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
#from django.forms import ModelForm, CharField, Select, DateField
from django import forms
from iluminare.paciente.models import *
from iluminare.atendimento.models import *
from iluminare.tratamento.models import *

import iluminare.paciente.logic as paciente_logic
import datetime

PRIORIDADE_CHOICES = (
    ('G', 'Grávida'),
    ('L', 'Lactante'),
    ('B', 'Baixa Imunidade'),
    ('C', 'Criança até 12 anos'))

class DetalhePrioridadeForm(forms.ModelForm):
    """ formulário para atualizar os detalhes caso o paciente seja prioritário. """
    class Meta:
        model = DetalhePrioridade
        exclude = ('paciente', )

    def save(self):
        detalhe_prioridade = forms.ModelForm.save(self, commit=False)
       
        # verifica se o objeto detalhe_prioridade está consistente
        paciente_logic.validar_detalhe_prioridade(detalhe_prioridade)
        
        detalhe_prioridade.save()
        self.save_m2m()


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        exclude = ('saude', )

    def save(self):
        forms.ModelForm.save(self)

def atualizar(request, paciente_id):
    paciente = Paciente.objects.get(pk=paciente_id)
    
    try:
        detalhe_prioridade = DetalhePrioridade.objects.get(paciente=paciente)
    except:
        # caso o detalhe_prioridade do paciente não exista, será criado.
        detalhe_prioridade = DetalhePrioridade(paciente=paciente)
        detalhe_prioridade.save()

    if request.method == "POST":
        form_paciente = PacienteForm(request.POST, instance=paciente)
        form_detalhe_prioridade = DetalhePrioridadeForm(request.POST, instance=detalhe_prioridade)

        try:
            form_paciente.save()
            form_detalhe_prioridade.save()
            msg = "Paciente atualizado com sucesso"
        except paciente_logic.PacienteException as p_exc:
            msg = "Houve um erro ao atualizar o paciente (%s)" % p_exc
        except ValueError as v_exc:
            msg = "Houve um erro de validação dos dados (%s)" % v_exc

    else:
        form_paciente = PacienteForm(instance=paciente)
        form_detalhe_prioridade = DetalhePrioridadeForm(instance=detalhe_prioridade)
        
        msg = ""

    return render_to_response('crud-paciente.html', {'form_paciente':form_paciente, 'form_detalhe_prioridade':form_detalhe_prioridade, 'mensagem':msg})

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
        pacientes = Paciente.objects.all()[:10]

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


