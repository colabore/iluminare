from django.conf.urls.defaults import * 

urlpatterns = patterns('iluminare.atendimento.views',
	(r'^$', 'index'),
	(r'^consultar/(?P<paciente_id>[0-9]+)$','exibir_atendimentos_paciente'),
	(r'^listagem/(?P<pagina>[0-9]+)/$', 'exibir_listagem'),
	(r'^listagem/$', 'exibir_listagem'),	
)

