from django.conf.urls.defaults import * 

urlpatterns = patterns('iluminare.voluntario.views',
    (r'^$', 'render'),
	(r'^registra-ponto/$', 'registra_ponto'),
	(r'^consulta-ponto/$', 'consulta_ponto'),
)

