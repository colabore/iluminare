from django.conf.urls.defaults import * 

urlpatterns = patterns('iluminare.atendimento.views',
    (r'^$', 'index'),
    (r'^confirmacao$', 'confirmacao'),
    (r'^checkin/(?P<paciente_id>[0-9]+)$', 'ajax_checkin_paciente'),
	(r'^consultar/(?P<paciente_id>[0-9]+)$','exibir_atendimentos_paciente'),
	(r'^consultar/(?P<paciente_id>[0-9]+)/(?P<pagina>[0-9]+)$','exibir_atendimentos_paciente'),
	(r'^listagem/(?P<pagina>[0-9]+)/$', 'exibir_listagem'),
	(r'^listagem/$', 'exibir_listagem'),
	(r'^relatorio/$', 'exibir_relatorio_atendimento'),	
)

