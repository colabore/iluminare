from django.contrib import admin
from iluminare.voluntario.models import *

class VoluntarioAdmin(admin.ModelAdmin):
    search_fields = ['paciente__nome']
    list_display = ('paciente', 'tipo', 'ativo')


admin.site.register(Trabalho)
admin.site.register(Funcao)
admin.site.register(Voluntario, VoluntarioAdmin)
admin.site.register(FuncaoVoluntario)
admin.site.register(AgendaTrabalho)

