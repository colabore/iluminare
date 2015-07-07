from tratamento.models import *
from django.contrib import admin

#sadmin.site.register(Tratamento)

class TratamentoAdmin(admin.ModelAdmin):
    fields = ('sala','descricao_completa','dia_semana','horario_limite',  'descricao_basica')
    excludes = ('max_agendamentos',)

    search_fields = ['descricao_basica']
    list_display = ('descricao_basica', 'sala', 'dia_semana')
    #admin.ModelAdmin.actions_on_bottom

admin.site.register(Tratamento, TratamentoAdmin)
admin.site.register(TratamentoPaciente)
admin.site.register(InstanciaTratamento)
admin.site.register(AgendaTratamento)
admin.site.register(Sala)
