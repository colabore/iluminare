# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from iluminare.tratamento.models import Tratamento
from iluminare.atendimento.models import Atendimento
from django import forms
from django.forms.models import modelformset_factory, BaseModelFormSet

class FiltroAtendimentosForm(forms.Form):
    tratamento      = forms.ModelChoiceField(queryset=Tratamento.objects.all())
    data            = forms.DateField()
    prioridades     = forms.BooleanField()
    nao_prioridades = forms.BooleanField()

class ConfirmacaoAtendimentoForm(forms.ModelForm):
    paciente = forms.CharField()
    observacao = forms.CharField()

    class Meta:
        model = Atendimento
        exclude = ['prioridade', 'instancia_tratamento']

class BaseConfirmacaoAtendimentoFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super(BaseConfirmacaoAtendimentoFormSet, self).add_fields(form, index)
        #paciente = Paciente.objects.get(pk=1)
        form.fields["Nome"] = forms.CharField()

ConfirmacaoAtendimentoFormSet = modelformset_factory(Atendimento, extra=0,
    form=ConfirmacaoAtendimentoForm, formset=BaseConfirmacaoAtendimentoFormSet)

def confirmacao(request):
    if request.method == "POST":
        filtro_form = FiltroAtendimentosForm(request.POST)

        atendimentos = ConfirmacaoAtendimentoFormSet(request.POST)
        if atendimentos.is_valid():
            atendimentos.save()
    else:
        filtro_form = FiltroAtendimentosForm()
        atendimentos = ConfirmacaoAtendimentoFormSet(queryset=Atendimento.objects.all())
    
    return render_to_response('confirmacao_atendimentos.html', {'filtro_form':filtro_form, 'atendimentos':atendimentos})

def index(request):
	return render_to_response('index.html')
