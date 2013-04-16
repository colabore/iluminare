from django.conf.urls.defaults import * 

urlpatterns = patterns('iluminare.atendimento.views',
    (r'^$', 'index'),
    (r'^confirmacao$', 'confirmacao'),
    (r'^checkin/(?P<paciente_id>[0-9]+)$', 'ajax_checkin_paciente'),
	(r'^consultar/(?P<paciente_id>[0-9]+)$','exibir_atendimentos_paciente'),
	(r'^consultar/(?P<paciente_id>[0-9]+)/(?P<pagina>[0-9]+)$','exibir_atendimentos_paciente'),
	(r'^listagem/(?P<pagina>[0-9]+)/$', 'exibir_listagem'),
	(r'^listagem/$', 'exibir_listagem'),
	(r'^listagem-criancas/(?P<pagina>[0-9]+)/$', 'exibir_listagem_criancas'),
	(r'^listagem-criancas/$', 'exibir_listagem_criancas'),
	(r'^listagem-geral/$', 'exibir_listagem_geral'),
	(r'^listagem-geral-fechamento/$', 'exibir_listagem_geral_fechamento'),
	(r'^relatorio-atendimentos-dia/$', 'relatorio_atendimentos_dia'),
	(r'^relatorio-atendimentos-mes/$', 'relatorio_atendimentos_mes'),
	(r'^relatorio-atendimentos-mes-csv/(?P<data_ordinal>[0-9]+)$', 'relatorio_atendimentos_mes_csv'),
    (r'^atualizar-paciente-confirmacao/(?P<atendimento_id>[0-9]+)$', 'ajax_atualizar_paciente_confirmacao'),
    (r'^listagem-notificacoes/$', 'exibir_listagem_notificacoes'),
    (r'^listagem-agendamentos/$', 'exibir_listagem_agendamentos'),
    (r'^incluir-notificacao/(?P<paciente_id>[0-9]+)$', 'incluir_notificacao'),
    (r'^atualizar-notificacao/(?P<notificacao_id>[0-9]+)$', 'atualizar_notificacao'),
)

