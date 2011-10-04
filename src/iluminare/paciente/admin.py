from iluminare.paciente.models import *
from django.contrib import admin

class PacienteAdmin(admin.ModelAdmin):
    
    search_fields = ['nome']
    #admin.ModelAdmin.actions_on_bottom

admin.site.register(Paciente, PacienteAdmin)
admin.site.register(DetalhePrioridade)

