from django.conf.urls.defaults import * 

urlpatterns = patterns('iluminare.tratamento.views',
    (r'^incluir-agenda-tratamento/$', 'incluir_agenda_tratamento'),
)

