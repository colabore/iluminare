from django.conf.urls import *
from iluminare.paciente.views import cadastro_rapido_paciente
import iluminare.paciente.rest as rest

urlpatterns = patterns('iluminare.paciente.views',
    (r'^$', 'index'),
    (r'^(?P<paciente_id>[0-9]+)$', 'atualizar'),
    (r'^search/(?P<nome>.*)$', 'ajaxlistarpessoas'),
    (r'^consultar/(?P<paciente_id>[0-9]+)$', 'ajax_consultar_paciente'),
    (r'^incluir', 'incluir_paciente'),
    (r'^dialog/detalhe/(?P<paciente_id>[0-9]+)/(?P<tratamento_id>[0-9]+)$', 'dialog_detalhe'),
    url(r'^cadastro-rapido/$', cadastro_rapido_paciente, name='cadastro_rapido_paciente'),
    (r'^relatorio-pacientes/$', 'relatorio_pacientes'),
    url(r'^json/search/(?P<nome>.*)$', rest.search),
    url(r'^json/detailed_search/(?P<nome>.*)$', rest.detailed_search),
)
