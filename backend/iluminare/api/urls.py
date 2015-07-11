from rest_framework import routers
from api.views import *

router = routers.DefaultRouter()
router.register(r'paciente', PacienteViewSet)
router.register(r'atendimento', AtendimentoViewSet)
router.register(r'tratamento', TratamentoViewSet)
router.register(r'voluntario', VoluntarioViewSet)
router.register(r'notificacao', NotificacaoViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
