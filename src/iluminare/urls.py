from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^iluminare/', include('iluminare.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # a primeira pagina do site e a primeira pagina no madulo 'entrada'
    (r'^$', 'iluminare.limbo.views.index'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.ILUMINARE_ROOT + "static"}),

    # o app entrada tera as urls administradas em entrada/urls.py
    (r'^paciente/', include('iluminare.paciente.urls')),
    (r'^voluntario/', include('iluminare.voluntario.urls')),
    (r'^limbo/', include('iluminare.limbo.urls')),
    (r'^relatorio/', include('iluminare.relatorio.urls')),
    (r'^atendimento/', include('iluminare.atendimento.urls')),
)
