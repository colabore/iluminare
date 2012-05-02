from django.conf.urls.defaults import * 

urlpatterns = patterns('iluminare.voluntario.views',
    (r'^$', 'render'),
	(r'^registra-ponto/$', 'registra_ponto'),
	(r'^consulta-ponto/$', 'consulta_ponto'),
    (r'^(?P<voluntario_id>[0-9]+)$', 'atualizar'),
    (r'^relatorio-trabalhos/$', 'relatorio_trabalhos'),
    (r'^relatorio-trabalhos-csv/(?P<data_inicial_ordinal>[0-9]+)/(?P<data_final_ordinal>[0-9]+)/(?P<dia_semana_int>[0-9]+)$', 'relatorio_trabalhos_csv'),
)

