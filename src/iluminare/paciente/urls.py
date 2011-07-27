from django.conf.urls.defaults import * 

urlpatterns = patterns('iluminare.paciente.views',
    (r'^$', 'index'),
    (r'^search/(?P<nome>.*)$', 'ajaxlistarpessoas'),
    (r'^consultar/(?P<paciente_id>[0-9]+)$', 'ajax_consultar_paciente'),
    (r'^dialog/detalhe/(?P<paciente_id>[0-9]+)/(?P<tratamento_id>[0-9]+)$', 'dialog_detalhe')
)

