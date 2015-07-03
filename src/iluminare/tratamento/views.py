# coding: utf-8
import  traceback
from django import forms
from django.shortcuts import render_to_response
from iluminare.tratamento.models import AgendaTratamento, Tratamento

class AgendaTratamentoForm(forms.ModelForm):
    class Meta:
        model = AgendaTratamento

    def __init__(self, *args, **kwargs):
        super(AgendaTratamentoForm, self).__init__(*args, **kwargs)
        self.fields['tratamento'].queryset=Tratamento.objects.filter(id__in=[8,9,10])

    def save(self):
        dic = {}
        agenda_tratamento = super(AgendaTratamentoForm, self).save(commit=False)
        ats = AgendaTratamento.objects.filter(tratamento=agenda_tratamento.tratamento, data=agenda_tratamento.data)
        if len(ats) > 0:
            dic['sucesso'] = False
            dic['mensagem'] = "Agenda não cadastrada. Já existe uma agenda para este tratamento neste dia."
        else:
            agenda_tratamento.save()
            dic['sucesso'] = True
            dic['mensagem'] = "Agenda cadastrada com sucesso."

        return dic

def incluir_agenda_tratamento(request):
    mensagem_sucesso = ''
    mensagem_erro = ''

    if request.method == "POST":
        form_agenda = AgendaTratamentoForm(request.POST)
        if form_agenda.is_valid():
            try:
                dic = form_agenda.save()
                if dic['sucesso'] == True:
                    mensagem_sucesso = dic['mensagem']
                else:
                    mensagem_erro = dic['mensagem']
            except:
                mensagem_erro = "Erro na criação da agenda."
                traceback.print_exc()
        else:
            traceback.print_exc()
            mensagem_erro = "Erro na criação da agenda. Favor verificar os campos."
    else:
        form_agenda = AgendaTratamentoForm()

    return render_to_response('crud-agenda-tratamento.html',
        {'form_agenda':form_agenda,\
        'mensagem_sucesso':mensagem_sucesso, \
        'mensagem_erro':mensagem_erro, \
        'titulo':'INCLUIR AGENDA'})
