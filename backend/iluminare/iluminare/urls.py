from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    (r'^paciente/', include('paciente.urls')),
    (r'^voluntario/', include('voluntario.urls')),
    (r'^atendimento/', include('atendimento.urls')),
    (r'^tratamento/', include('tratamento.urls')),
    (r'^$', 'atendimento.views.index'),
)
