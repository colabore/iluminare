from iluminare.atendimento.models import *
from django.contrib import admin

class AtendimentoAdmin(admin.ModelAdmin):
    
    search_fields = ['paciente__nome']
    list_display = ('paciente', 'instancia_tratamento', 'hora_chegada', 'status')
    #admin.ModelAdmin.actions_on_bottom

class AgendaAtendimentoAdmin(admin.ModelAdmin):
    exclude = ('atendimento_origem', 'atendimento_realizado')

class NotificacaoAdmin(admin.ModelAdmin):
    exclude = ('atendimento',)

admin.site.register(Atendimento, AtendimentoAdmin)
admin.site.register(AgendaAtendimento, AgendaAtendimentoAdmin)
admin.site.register(Notificacao, NotificacaoAdmin)
