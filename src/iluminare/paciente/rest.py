
from json import loads,dumps
from django.http import JsonResponse
from django.core import serializers

import iluminare.paciente.logic as paciente_logic
import iluminare.paciente.queries as paciente_queries

def make_response(result):
    response = JsonResponse(result)
    response['Access-Control-Allow-Origin'] = "*"
    return response

def models_to_json(models):
    return loads(serializers.serialize("json", models))
'''
dic = {
    'tratamentos': tratamentos,
    'paciente':paciente,
    'atendimento': it,
    'salas': "TODO",
    'hoje': 'TODO',
    'jtc': jtc,
    'eh_vol': eh_vol
}
'''
def search(request, nome):
    result = []

    if request.method == 'GET' and nome != '':
        pacientes = paciente_logic.search(nome)
        result = models_to_json(pacientes)

    return make_response({'result': result})

def detailed_search(request, nome):
    result = []

    if request.method == 'GET' and nome != '':
        pacientes = paciente_logic.search(nome)
        result = dumps(paciente_queries.detailed_search(pacientes))

    return make_response({'result': result})
