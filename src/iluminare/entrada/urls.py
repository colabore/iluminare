from django.conf.urls.defaults import * 

urlpatterns = patterns('iluminare.entrada.views',
    (r'^$', 'index'),
    (r'^search/(?P<nome>\w*)$', 'ajaxlistarpessoas'),
    (r'^dialog/detalhe/(?P<paciente_id>[0-9]+)/(?P<tratamento_id>[0-9]+)$', 'dialog_detalhe')
)

