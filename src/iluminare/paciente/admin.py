from iluminare.paciente.models import *
from iluminare.atendimento.models import *
from django.contrib import admin

admin.site.register(Paciente)
admin.site.register(Tipo_Prioridade)

