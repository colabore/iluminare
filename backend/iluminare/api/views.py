
from rest_framework import viewsets, filters
from api.serializers import *

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    filter_backends = (filters.SearchFilter,filters.DjangoFilterBackend)
    search_fields = ('nome', )
    filter_fields = ('id',)

class AtendimentoViewSet(viewsets.ModelViewSet):
    queryset = Atendimento.objects.all()
    serializer_class = AtendimentoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id', 'status', 'instancia_tratamento__data', 'instancia_tratamento__id')

class InstanciaTratamentoViewSet(viewsets.ModelViewSet):
    queryset = InstanciaTratamento.objects.all()
    serializer_class = InstanciaTratamentoSerializer
    filter_backends = (filters.DjangoFilterBackend,filters.OrderingFilter)
    filter_fields = ('data', 'tratamento__id')
    ordering_fields = ('id',)

class TratamentoViewSet(viewsets.ModelViewSet):
    queryset = Tratamento.objects.all()
    serializer_class = TratamentoSerializer

class VoluntarioViewSet(viewsets.ModelViewSet):
    queryset = Voluntario.objects.all()
    serializer_class = VoluntarioSerializer

class NotificacaoViewSet(viewsets.ModelViewSet):
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer
    filter_backends = (filters.DjangoFilterBackend,filters.SearchFilter)
    search_fields = ('paciente__nome', )
    filter_fields = ('data_criacao', 'atendimento__instancia_tratamento__tratamento__id')
