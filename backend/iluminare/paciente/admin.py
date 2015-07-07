from paciente.models import *
from django.contrib import admin

class PacienteAdmin(admin.ModelAdmin):

    search_fields = ['nome']

admin.site.register(Paciente, PacienteAdmin)
admin.site.register(DetalhePrioridade)
