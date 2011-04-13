from iluminare.paciente.models import *
from iluminare.atendimento.models import *
from django.contrib import admin


admin.site.register(Tratamento)
admin.site.register(Atendimento)
admin.site.register(Tratamento_Paciente)
admin.site.register(Instancia_Tratamento)
admin.site.register(TratamentoEmAndamento)
admin.site.register(Agenda_Atendimento)
admin.site.register(Sala)

