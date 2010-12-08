# Create your views here.
from django.shortcuts import render_to_response

def index (request):
    return render_to_response ('listar-pessoas.html')

def listar_pessoas(request):
    return render_to_response ('listar-pessoas.html')    
