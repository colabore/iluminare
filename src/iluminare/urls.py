from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'iluminare.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # a primeira pagina do site e a primeira pagina no madulo 'entrada'
    (r'^$', 'iluminare.limbo.views.index'),
    #(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.ILUMINARE_ROOT + "static"}),

    # o app entrada tera as urls administradas em entrada/urls.py
    (r'^paciente/', include('iluminare.paciente.urls')),
    (r'^voluntario/', include('iluminare.voluntario.urls')),
    (r'^limbo/', include('iluminare.limbo.urls')),
    (r'^util/', include('iluminare.util.urls')),
    (r'^relatorio/', include('iluminare.relatorio.urls')),
    (r'^atendimento/', include('iluminare.atendimento.urls')),
    (r'^tratamento/', include('iluminare.tratamento.urls')),
)
