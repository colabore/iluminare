# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django import forms
from iluminare.voluntario.models import *

class voluntarioForm(forms.ModelForm):
	class Meta:
		model = Voluntario

def render(request):
	if request.method == "POST":
		form_voluntario = voluntarioForm(request.POST)
		form_voluntario.save()
		msg = "novo voluntario cadastrado com sucesso"
	else:
		form_voluntario = voluntarioForm()
		msg = ""

	return render_to_response('add-voluntario.html',{'form_voluntario': form_voluntario, 'msg': msg})


def index(request):
	return render_to_response('index.html')


