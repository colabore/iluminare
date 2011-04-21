from django.contrib import admin
from iluminare.voluntario.models import *

admin.site.register(Trabalho)
admin.site.register(Funcao)
admin.site.register(Voluntario)
admin.site.register(FuncaoVoluntario)
admin.site.register(AgendaTrabalho)

