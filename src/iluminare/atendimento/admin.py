from iluminare.atendimento.models import *
from django.contrib import admin

class AtendimentoAdmin(admin.ModelAdmin):
    
    search_fields = ['paciente__nome']
    list_display = ('paciente', 'instancia_tratamento', 'hora_chegada', 'status')
    #admin.ModelAdmin.actions_on_bottom

admin.site.register(Atendimento, AtendimentoAdmin)

