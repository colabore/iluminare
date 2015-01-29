from django.conf.urls import * 

urlpatterns = patterns('iluminare.tratamento.views',
    (r'^incluir-agenda-tratamento/$', 'incluir_agenda_tratamento'),
)

