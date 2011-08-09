from django.conf.urls.defaults import * 

urlpatterns = patterns('iluminare.atendimento.views',
	(r'^$', 'index'),
	(r'^consultar/(?P<paciente_id>[0-9]+)$','exibirAtendimentosPaciente')	
)

