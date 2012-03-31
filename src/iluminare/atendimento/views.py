# -*- coding: utf-8 -*-
from iluminare.tratamento.models import Tratamento, InstanciaTratamento, TratamentoPaciente
from iluminare.atendimento.models import Atendimento
from iluminare.voluntario.models import Voluntario, Trabalho

from iluminare.paciente.models import DetalhePrioridade, Paciente
import iluminare.atendimento.logic as logic_atendimento
import iluminare.tratamento.logic as tratamento_logic
import iluminare.voluntario.logic as voluntario_logic


from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.core.paginator import Paginator
from django.http import HttpResponse

import datetime

from operator import itemgetter

import itertools

from django.utils.encoding import smart_str

from django.db.models import Q

from sets import Set
from django.db.models import Count

class CheckinPacienteForm(forms.ModelForm):

    PONTO_CHOICES = (
        ('N','------'),
        ('E', 'Entrada'),
        ('S', 'Saída'),
    )
    tratamento          = forms.ModelChoiceField(queryset=Tratamento.objects.all(), required=False)
    ponto_voluntario    = forms.ChoiceField(required=False, choices=PONTO_CHOICES)
    forcar_checkin      = forms.BooleanField(required=False)

    def __init__(self, *args, **kargs):
        super(CheckinPacienteForm, self).__init__(*args, **kargs)
        self.fields.keyOrder = ['tratamento', 'prioridade', 'observacao_prioridade', \
            'ponto_voluntario', 'forcar_checkin']

    def update_tratamentos(self, paciente):

        volunt = False
        volunt_entrada = False
        volunt_saida = False
        
        # AJUSTANDO PONTO DO VOLUNTÁRIO
        vs = Voluntario.objects.filter(paciente = paciente, ativo = True)
        if len(vs) >= 1: # indica que o paciente é um voluntário da casa
            volunt = True
            ts = Trabalho.objects.filter(voluntario = vs[0], data = datetime.date.today())
            if len(ts) == 0: # indica que ele ainda não tem nenhum trabalho no dia. Ou seja, está entrando.
                self.fields['ponto_voluntario'].initial = 'E'
                volunt_entrada = True
            else:
                self.fields['ponto_voluntario'].initial = 'S'
                volunt_saida = True

        # AJUSTANDO A TELA PARA AS SEGUNDAS
        if datetime.date.today().weekday() == 0:
            lista_trat = Tratamento.objects.filter(dia_semana = 'S')
            self.fields['tratamento'].queryset = lista_trat
            
            # só atualiza a opção inicial do campo tratamento na segunda para Manutenção se não for voluntário.
            # Em geral, os voluntários não se tratam nas segundas. Logo, só farão os pontos de entrada e saída.
            if not volunt: 
                trat_manut = Tratamento.objects.filter(descricao_basica__startswith = "Manu")
                if len(trat_manut) > 0:
                    manut = trat_manut[0]
                    if manut in lista_trat:
                        self.fields['tratamento'].initial = manut
                    
            
            
        # AJUSTANDO A TELA PARA AS QUINTAS            
        elif datetime.date.today().weekday() == 3:
            self.fields['tratamento'].queryset = Tratamento.objects.filter(dia_semana = 'N')
            
            # só atualiza a opção inicial do campo tratamento na quinta se não for voluntário 
            # ou for um voluntário entrando na casa.
            # A ideia é que na saída só haja para o voluntário a opção ponto de saída.
            if not volunt or volunt_entrada:
                tratamentos = [tp.tratamento for tp in paciente.tratamentopaciente_set.filter(status='A')]
                if len(tratamentos) > 0:
                    self.fields['tratamento'].initial = tratamentos[0]
                
        # AJUSTANDO A TELA PARA OUTROS DIAS (em geral utilizado para os testes)
        else:
            self.fields['tratamento'].queryset = Tratamento.objects.all()

        # ATUALIZANDO LABEL DA OBSERVAÇÃO PRIORIDADE
        self.fields['observacao_prioridade'].label = "Info. Complementar"
        
        
    class Meta:
        model = Atendimento
        exclude = ['observacao', 'status', 'hora_atendimento', 'hora_chegada', 'instancia_tratamento', 'paciente', 'senha']


def ajax_checkin_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    lista_atendimentos = logic_atendimento.atendimentos_paciente(paciente.id)
    
    voluntarios = Voluntario.objects.filter(paciente = paciente, ativo = True)
    voluntario = None
    if len(voluntarios) > 0:
        voluntario = voluntarios[0]
    
    debug = ''
    if request.method == 'POST':
        checkin_paciente_form = CheckinPacienteForm(request.POST)
        if checkin_paciente_form.is_valid():
            tratamento              = checkin_paciente_form.cleaned_data['tratamento']
            prioridade              = checkin_paciente_form.cleaned_data['prioridade']
            observacao_prioridade   = checkin_paciente_form.cleaned_data['observacao_prioridade']
            ponto_voluntario        = checkin_paciente_form.cleaned_data['ponto_voluntario']
            forcar_checkin          = checkin_paciente_form.cleaned_data['forcar_checkin']

            dic_ponto = None
            dic_checkin = None
            msg_validacao = None

            if tratamento == None and ponto_voluntario == 'N':
                msg_validacao = "Favor informar o tratamento ou confirmar o ponto do voluntário"

            if ponto_voluntario == 'S' and tratamento != None:
                msg_validacao = "Operação não realizada: Para efetuar o ponto de saída do voluntário é necessário que \
                    todos os outros campos estejam vazios"
            
            try:
                if msg_validacao == None and tratamento:
                    dic_checkin = logic_atendimento.checkin_paciente(paciente, tratamento, \
                        prioridade, observacao_prioridade, forcar_checkin)
                
                if msg_validacao == None and ponto_voluntario != 'N':
                    dic_ponto = voluntario_logic.ponto_voluntario(paciente, ponto_voluntario)

                return render_to_response('ajax-checkin-paciente-resultado.html', {'paciente':paciente, \
                    'voluntario':voluntario, 'dic_checkin':dic_checkin, 'dic_ponto':dic_ponto, \
                    'msg_validacao':msg_validacao})
                
            except Exception, e:
                return HttpResponse("Erro: %s" % str(e) +  debug)
        else:
            return HttpResponse("Erro %s" % str(checkin_paciente_form.errors))
    else:
        checkin_paciente_form = CheckinPacienteForm()
        checkin_paciente_form.update_tratamentos(paciente)

    return render_to_response('ajax-checkin-paciente.html', {'paciente':paciente, \
        'form':checkin_paciente_form, 'lista':lista_atendimentos, 'erros':str(checkin_paciente_form.errors), 'voluntario':voluntario})

def get_info(paciente):
    info = ""
    
    try:
        prioridade = paciente.detalheprioridade_set.get()
    except DetalhePrioridade.DoesNotExist:
        prioridade = DetalhePrioridade(paciente=paciente)
        prioridade.save()
    except DetalhePrioridade.MultipleObjectsReturned:
        prioridade = paciente.detalheprioridade_set.all()[0]
    finally:
        info = prioridade.get_tipo_display()

    return info

class FiltroAtendimentosForm(forms.Form):
    tratamento      = forms.ModelChoiceField(queryset=Tratamento.objects.all(), help_text ="Tratamento")
    data            = forms.DateField(help_text="Data")

    def __init__(self, *args, **kwargs):
        super(FiltroAtendimentosForm, self).__init__(*args, **kwargs)
        self.fields['data'].initial = datetime.date.today()

def retornaInfo(atendimento):

    info_str = ''
    
    try:
        tratamento = atendimento.instancia_tratamento.tratamento
        
        if tratamento.descricao_basica[:4] == "Manu":
            data_limite = datetime.datetime.today().date() - datetime.timedelta(days=90)

            
            # CONTAGEM DE MANUTENÇÕES
            # com essa restrição dos 90 dias, estamos garantindo que a contagem de manutenções 
            # realizadas se restrinjam aos atendimentos recentes.
            # Dessa forma, se o paciente há 1 ano fez a primeira vez e as manutenções, 
            # essa contagem será ignorada.
            cont = len(Atendimento.objects.filter(paciente__id = atendimento.paciente.id, \
                instancia_tratamento__tratamento = tratamento, status='A', \
                instancia_tratamento__data__gte=data_limite))
           
            info_str = info_str + '[' + str(cont) + ']'

            # LISTA DE TRATAMENTOS
            tps = TratamentoPaciente.objects.filter(paciente = atendimento.paciente, status='A')
            tratamentos = ''
            for tp in tps:
                tratamentos = tratamentos + tp.tratamento.descricao_basica + ', '
            
            # retira o ', ' do final
            tratamentos = tratamentos[:-2]
            
            if tratamentos != "":
                info_str = info_str + '[' + tratamentos + ']'
            
            # [1a VEZ]
            # inclui o [1a vez] se o paciente também está realizando um atendimento de 1a vez no mesmo dia.
            # ATENCAO [1a VEZ] != [1o ATENDIMENTO]
            primeira_vez = Atendimento.objects.filter(paciente__id = atendimento.paciente.id, \
                instancia_tratamento__tratamento__descricao_basica__startswith = "Prime", \
                instancia_tratamento__data = datetime.datetime.today())
            if len(primeira_vez) == 1:
                info_str = info_str + '[1a vez]'
            
    except Tratamento.DoesNotExist:
        pass


    # 1o QUINTA.
    data_limite = datetime.datetime.today().date() - datetime.timedelta(days=90)

    # manutencoes nos ultimos 90 dias.    
    manutencao = Atendimento.objects.filter(paciente__id = atendimento.paciente.id, 
        instancia_tratamento__tratamento__descricao_basica__startswith = "Manu", status='A', \
        instancia_tratamento__data__gte=data_limite)

    atendimentos = Atendimento.objects.filter(paciente__id = atendimento.paciente.id, 
        instancia_tratamento__tratamento__descricao_basica__startswith ="Sala", status='A', \
        instancia_tratamento__data__gte=data_limite)

    # último atendimento
    ats = Atendimento.objects.raw("""select ate.* from paciente_paciente as p
        join atendimento_atendimento as ate
            on p.id = ate.paciente_id
        join tratamento_instanciatratamento as it
            on ate.instancia_tratamento_id = it.id
        where p.id = %d and ate.status = 'A'
        order by it.data desc
        limit 1;""" % atendimento.paciente.id)

    # condição para que seja [1a quinta]:
    # - o último atendimento foi de manutenção
    # - a quantidade de atendimentos nos últimos 3 meses em algum tratamento nas salas 1 a 5 = 0.
    # - o atendimento (param) é sala 1 a 5.
    # 
    if len(list(ats)) > 0 and len(list(atendimentos)) == 0 \
        and atendimento.instancia_tratamento.tratamento.descricao_basica[:4] == "Sala":
        ult_at = ats[0]
        if ult_at.instancia_tratamento.tratamento.descricao_basica[:4] == "Manu":
            info_str = info_str + '[1a quinta]'

    # [SÓ TRATAMENTO] - caso dos voluntários que estão só se tratando.
    try:
        voluntario = Voluntario.objects.filter(paciente__id = atendimento.paciente.id, ativo = True)
        if len(voluntario) > 0:
            trabalho = Trabalho.objects.filter(voluntario = voluntario[0], data = atendimento.instancia_tratamento.data)
            info_str = info_str + '[' + voluntario[0].get_tipo_display() + ']'
            # caso o trabalhador tenha efetuado o ponto de entrada, constará na lista de impressão a informação
            # [Só tratamento]
            # Dessa forma, a pessoa que estiver chamando não o deixará para o final.
            if len(trabalho) == 0:
                info_str = info_str + u'[Só tratamento]'
    except Voluntario.DoesNotExist:
        pass
    
    try:
        prioridade =  DetalhePrioridade.objects.filter(paciente__id = atendimento.paciente.id)
        if len(prioridade) > 0:
            info_str = info_str + '[' + prioridade[0].get_tipo_display() + ']'
    except DetalhePrioridade.DoesNotExist:
        pass
    
    # PRIORIDADE SÓ NO DIA
    if atendimento.prioridade:
        info_str = info_str + '[Prioridade hoje]'
    
    # OBSERVACAO PRIORIDADE
    if atendimento.observacao_prioridade:   
        info_str = info_str + '[' + atendimento.observacao_prioridade + ']' 

    # ACOMPANHA: ...
    if atendimento.paciente.acompanhante:
        dp = DetalhePrioridade.objects.filter(paciente = atendimento.paciente.acompanhante)
        at = Atendimento.objects.filter(paciente = atendimento.paciente.acompanhante, \
            instancia_tratamento__data = atendimento.instancia_tratamento.data)
        if dp and at:
            nome_prioridade = atendimento.paciente.acompanhante.nome[:10]+'...'
            info_str = info_str + '[Acompanha: ' + unicode(nome_prioridade) + ']'

    return info_str
    
    
class ConfirmacaoAtendimentoForm(forms.ModelForm):
    observacao = forms.CharField(required=False)
    senha = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'5'}))
    nome = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'25'}))
    hora_chegada = forms.TimeField(label='Cheg.',required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'6'}))
    confirma = forms.BooleanField(required = False, label= 'Conf.')
    redireciona = forms.ModelChoiceField(label='Redir.',queryset=Tratamento.objects.none(), required=False)
    encaminha = forms.ModelChoiceField(label='Enc.', queryset=Tratamento.objects.none(), required=False)
    frequencia = forms.ChoiceField(label='Freq', choices=(('X','---------'),) , required=False)

    def __init__(self, *args, **kwargs):
        super(ConfirmacaoAtendimentoForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['confirma', 'senha', 'nome', 'hora_chegada','observacao', 'frequencia', 'redireciona', 'encaminha']
        atendimento = kwargs.pop('instance')
        
        tratamento_desc = atendimento.instancia_tratamento.tratamento.descricao_basica
        
        # CAREREGA OS CAMPOS REDIRECIONA E ENCAMINHA
        if tratamento_desc[:4] == 'Sala':
            self.fields['redireciona'].queryset=Tratamento.objects.filter(descricao_basica__startswith='Sala')
            self.fields['encaminha'].queryset=Tratamento.objects.filter(descricao_basica__startswith='Sala')
        elif tratamento_desc[:4] == 'Manu':
            self.fields['redireciona'].queryset=Tratamento.objects.none()
            self.fields['encaminha'].queryset=Tratamento.objects.none()
        elif tratamento_desc[:4] == 'Prim':
            self.fields['redireciona'].queryset=Tratamento.objects.none()
            self.fields['encaminha'].queryset=Tratamento.objects.filter(descricao_basica__startswith='Sala')
            opcoes = (('X','---------'),) + Paciente.FREQUENCIA
            self.fields['frequencia'].choices=opcoes
        else:
            self.fields['redireciona'].queryset=Tratamento.objects.none()
            self.fields['encaminha'].queryset=Tratamento.objects.none()
                
        # CARREGA O NOME DO PACIENTE
        self.fields['nome'].initial = atendimento.paciente.nome
        
        # CARREGA A SENHA DO DIA DO PACIENTE
        self.fields['senha'].initial = atendimento.senha
        
        # CARREGA STATUS DO ATENDIMENTO
        if atendimento.status == 'A':
            status = True
        else:
            status = False
        self.fields['confirma'].initial = status

    def save(self, commit=True):
        atendimento = super(ConfirmacaoAtendimentoForm, self).save(commit=False)
        confirma_in = self.cleaned_data['confirma']
        redireciona_in = self.cleaned_data['redireciona']
        encaminha_in = self.cleaned_data['encaminha']
        frequencia_in = self.cleaned_data['frequencia']
        
        if redireciona_in:
            atendimento_atual_str = atendimento.instancia_tratamento.tratamento.descricao_basica
            its = InstanciaTratamento.objects.filter(data=atendimento.instancia_tratamento.data, tratamento__descricao_basica=redireciona_in)
            if its and its[0] != atendimento.instancia_tratamento:
                atendimento.instancia_tratamento = its[0]
                obs = atendimento.observacao 
                atendimento.observacao = obs + '[Checkin: ' + atendimento_atual_str + ' / Hoje foi para '+str(redireciona_in)+']'
        
        if encaminha_in:
            tratamento = Tratamento.objects.get(descricao_basica = encaminha_in)
            if tratamento:
                lista_t = []
                lista_t.append(tratamento)
                tratamento_logic.encaminhar_paciente(atendimento.paciente.id, lista_t)
                obs = atendimento.observacao 
                atendimento.observacao = obs + '[Encaminhado para '+str(encaminha_in)+']'
        
        if frequencia_in != 'X':
            # significa que se trata de um atendimento de primeira vez, pois somente estes podem ser alterados.
            atendimento.paciente.frequencia = frequencia_in
            atendimento.paciente.save()
            obs = atendimento.observacao 
            atendimento.observacao = obs + '[Freq: '+str(frequencia_in)+']'

        
        if confirma_in:
            atendimento.status = 'A'
            
            # se o tratamento for primeira vez, aproveitamos para atualizar o campo tem ficha.
            if atendimento.instancia_tratamento.tratamento.descricao_basica[:4] == 'Prim':
                atendimento.paciente.tem_ficha = True
                atendimento.paciente.save()
        else:
            atendimento.status = 'C'
        if commit:
            atendimento.save()

    class Meta:
        model = Atendimento
        exclude = ['prioridade', 'instancia_tratamento', 'senha', 'observacao_prioridade', 'paciente', 'hora_atendimento', 'status']
          

ConfirmacaoAtendimentoFormSet = modelformset_factory(Atendimento, extra=0,
    form=ConfirmacaoAtendimentoForm)

def confirmacao(request):
    if request.method == "POST":
        filtro_form = FiltroAtendimentosForm(request.POST)
        atendimentos = ConfirmacaoAtendimentoFormSet(request.POST)
	
        if atendimentos.is_valid():
            atendimentos.save()
	
        if filtro_form.is_valid() and atendimentos.is_valid():
            tratamento = filtro_form.cleaned_data['tratamento']
            data	   = filtro_form.cleaned_data['data']
            atendimentos = ConfirmacaoAtendimentoFormSet(queryset=Atendimento.objects.filter(instancia_tratamento__data=data,instancia_tratamento__tratamento=tratamento))

    else:
        filtro_form = FiltroAtendimentosForm()
        atendimentos = ConfirmacaoAtendimentoFormSet(queryset=Atendimento.objects.none())
    
    return render_to_response('confirmacao_atendimentos.html', {'filtro_form':filtro_form, 'atendimentos':atendimentos, 'mensagem':atendimentos.errors})

def index(request):
	return render_to_response('index.html')

#codigo aqui

class ImprimirListagemForm(forms.Form):

	def __init__(self, *args, **kwargs):
        	super(ImprimirListagemForm, self).__init__(*args, **kwargs)
        	self.fields['tratamento'].choices = [('', '----------')] + [(tratamento.id, tratamento.descricao_basica) for tratamento in Tratamento.objects.all()]
	tratamento = forms.ChoiceField(choices=())
	data = forms.DateField(initial = datetime.date.today)
	prioridade = forms.BooleanField(required = False)
	voluntario = forms.BooleanField(required = False)

class ListagemGeralForm(forms.Form):

	def __init__(self, *args, **kwargs):
        	super(ListagemGeralForm, self).__init__(*args, **kwargs)

	data = forms.DateField(initial = datetime.date.today)

class ListagemGeralFechamentoForm(forms.Form):

	def __init__(self, *args, **kwargs):
        	super(ListagemGeralFechamentoForm, self).__init__(*args, **kwargs)
        	self.fields['tratamento'].choices = [('-', '----------')] + [(tratamento.id, tratamento.descricao_basica) for tratamento in Tratamento.objects.all()]

	data = forms.DateField(initial = datetime.date.today)
	tratamento = forms.ChoiceField(choices=())

class RelatorioAtendimentosConsolidadoDiaForm(forms.Form):

	def __init__(self, *args, **kwargs):
        	super(RelatorioAtendimentosConsolidadoDiaForm, self).__init__(*args, **kwargs)

	data = forms.DateField(initial = datetime.date.today)

class RelatorioAtendimentosConsolidadoMesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(RelatorioAtendimentosConsolidadoMesForm, self).__init__(*args, **kwargs)

    data = forms.DateField(initial = datetime.date.today)

class RelatorioAtendimentoData(forms.Form):

	def __init__(self, *args, **kwargs):
		super(RelatorioAtendimentoData,self).__init__(*args, **kwargs)
		self.fields['tratamento'].choices = [('', '----------')] + [(tratamento.id, tratamento.descricao_basica) for tratamento in 			  			Tratamento.objects.all	()]

	STATUS = (
		('C','CHECK-IN'), 
		('I','IMPRESSO'), 
		('X','CHAMADO'), 
		('A','ATENDIDO'), 
		('N','NAO-ATENDIDO'))
	
	status = forms.ChoiceField(choices= STATUS)

	data = forms.DateField(initial = datetime.date.today)
	tratamento = forms.ChoiceField(choices=())


	

def exibir_relatorio_atendimento(rquest):

	form_relatorio = RelatorioAtendimentoData()
	mensagem_erro = ''	
	
	if request.method == "POST":
		
		if form_listagem.is_valid():
			data_in = form_listagem.cleaned_data['data']
			tratamento_in = form_listagem.cleaned_data['tratamento']
		else:
			mensagem_erro = 'formulário inválido'	
		

	return render_to_response('relatorio-atendimento.html', {'form_relatorio':form_relatorio})

def exibir_listagem(request, pagina = None):

    form_listagem = ImprimirListagemForm()
    mensagem_erro = ''
    retorno = [];
    tratamento = ''

    if request.method == 'POST':
        form_listagem = ImprimirListagemForm(request.POST)

        if form_listagem.is_valid():
            data_in = form_listagem.cleaned_data['data']
            tratamento_in = form_listagem.cleaned_data['tratamento']
            prioridade_in = form_listagem.cleaned_data['prioridade']
            voluntario_in = form_listagem.cleaned_data['voluntario']

            tratamentos_marcados = InstanciaTratamento.objects.filter(tratamento__id  = tratamento_in, data = data_in)
            tratamento = Tratamento.objects.get(id=tratamento_in)
            for tratamentos in tratamentos_marcados:
                if not prioridade_in:
                    atendimentos_previstos = Atendimento.objects.filter(instancia_tratamento__id = tratamentos.id)
                else:
                    # PACIENTES QUE SÃO PRIORIDADE
                    atendimentos_previstos1 = Atendimento.objects.filter(instancia_tratamento=tratamentos.id). \
                        exclude(paciente__detalheprioridade=None)

                    # PACIENTES QUE SÃO PRIORIDADE NO DIA
                    atendimentos_previstos2 = Atendimento.objects.filter(prioridade=True, \
                        instancia_tratamento__id=tratamentos.id)

                    # ACOMPANHANTES
                    atendimentos_previstos3 = Atendimento.objects.filter(Q(instancia_tratamento__id=tratamentos.id) \
                        & ~Q(paciente__acompanhante=None))
                        
                    atendimentos_previstos = []
                    for at in atendimentos_previstos1:
                        atendimentos_previstos.append(at)
                    for at in atendimentos_previstos2:
                        atendimentos_previstos.append(at)
                    for at in atendimentos_previstos3:
                        dps = DetalhePrioridade.objects.filter(paciente = at.paciente.acompanhante)
                        ats = Atendimento.objects.filter(paciente = at.paciente.acompanhante, \
                            instancia_tratamento__data = at.instancia_tratamento.data)
                        # garante que a pessoa que é acompanha é uma prioridade e que ela fez check-in no dia.
                        if dps and ats:
                            atendimentos_previstos.append(at)
                
                voluntarios = Voluntario.objects.filter(ativo=True)
                pacientes_voluntarios = []
                for v in voluntarios:
                    pacientes_voluntarios.append(v.paciente)
                    
                for atendimento in atendimentos_previstos:
                    if voluntario_in:
                        if atendimento.paciente in pacientes_voluntarios:
                            info_str = retornaInfo(atendimento)
                            retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, \
                                'info': info_str, 'prioridade': False})
                    else:
                        info_str = retornaInfo(atendimento)
                        retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, \
                            'info': info_str, 'prioridade': False, 'senha':atendimento.senha})
                        
                            
            retorno_com_hora = [];
            retorno_sem_hora = [];

            for elemento in retorno:
                if (elemento['hora'] == None):
                    retorno_sem_hora.append(elemento)
                else:
                    retorno_com_hora.append(elemento)

            retorno_com_hora = sorted(retorno_com_hora, key= itemgetter('hora'))
            retorno = retorno_com_hora + retorno_sem_hora

            if not retorno:
                mensagem_erro = 'Não há registros'
        else:
            mensagem_erro = 'Formulário inválido';

    paginacao = Paginator(retorno,25) 
    if pagina == None:
        num_pagina = 1
    else:
        num_pagina = int(pagina)
    pagina_atual = paginacao.page(num_pagina)

	
    return render_to_response('listagem-diaria.html', {'form_listagem':form_listagem, 
                            'mensagem': mensagem_erro,
                            'pagina_atual':pagina_atual,
                            'tratamento':tratamento})

def exibir_listagem_geral(request):

    form_listagem = ListagemGeralForm()
    mensagem_erro = ''
    retorno = [];
    tratamento = ''

    if request.method == 'POST':
        form_listagem = ListagemGeralForm(request.POST)

        if form_listagem.is_valid():
            data_in = form_listagem.cleaned_data['data']

            tratamentos_marcados = InstanciaTratamento.objects.filter(data = data_in)
            atendimentos_previstos = Atendimento.objects.filter(instancia_tratamento__data = data_in).order_by('-hora_chegada')
            
            for atendimento in atendimentos_previstos:
                info_str = retornaInfo(atendimento)
                retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': info_str, 'prioridade': False, \
                    'sala': atendimento.instancia_tratamento.tratamento.descricao_basica, 'senha':atendimento.senha})
                

            if not retorno:
                mensagem_erro = 'Não há registros'
        else:
            mensagem_erro = 'Formulário inválido';

    return render_to_response('listagem-diaria-geral.html', {'form_listagem':form_listagem, 
                            'mensagem': mensagem_erro,
                            'retorno':retorno,
                            'tratamento':tratamento})

def exibir_listagem_geral_fechamento(request):

    form_listagem = ListagemGeralFechamentoForm()
    mensagem_erro = ''
    retorno = [];
    tratamento = ''

    if request.method == 'POST':
        form_listagem = ListagemGeralFechamentoForm(request.POST)

        if form_listagem.is_valid():
            data_in = form_listagem.cleaned_data['data']
            tratamento_in = form_listagem.cleaned_data['tratamento']

            if tratamento_in == '-':
                atendimentos = Atendimento.objects.filter(instancia_tratamento__data = data_in).order_by('-hora_chegada')
            else:
                atendimentos = Atendimento.objects.filter(instancia_tratamento__data = data_in, \
                    instancia_tratamento__tratamento__id = tratamento_in).order_by('-hora_chegada')
                
            for atendimento in atendimentos:
                info_str = retornaInfo(atendimento)
                retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': info_str, 'prioridade': False, \
                    'sala': atendimento.instancia_tratamento.tratamento.descricao_basica, 'senha':atendimento.senha, \
                    'status':atendimento.status, 'observacao':atendimento.observacao})

            if not retorno:
                mensagem_erro = 'Não há registros'
        else:
            mensagem_erro = 'Formulário inválido';

    return render_to_response('listagem-diaria-geral-fechamento.html', {'form_listagem_fechamento':form_listagem, 
                            'mensagem': mensagem_erro,
                            'retorno':retorno,
                            'tratamento':tratamento})


def exibir_atendimentos_paciente(request, paciente_id, pagina = None):
	lista_atendimentos = Atendimento.objects.filter(paciente__id = paciente_id).order_by('-instancia_tratamento__data')

	mensagem_erro = ''
	retorno   = [];
	paciente = Paciente.objects.get(id=paciente_id)
	
	
	for atendimento in lista_atendimentos:
		retorno.append({'data':	atendimento.instancia_tratamento.data, 'tratamento': atendimento.instancia_tratamento.tratamento.descricao_basica, 			'hora_chegada': atendimento.hora_chegada, 'observacao': atendimento.observacao, 'status':atendimento.status})
		
		
	if not retorno:
		mensagem_erro = 'Não foi possível localizar usuário'
		
	paginacao = Paginator(retorno,45)
	if pagina == None:
		num_pagina = 1
	else:	
		num_pagina = int(pagina)
	pagina_atual = paginacao.page(num_pagina)	
	
	return render_to_response('lista-atendimentos.html',{'mensagem': mensagem_erro, 'pagina_atual': pagina_atual, 'paciente_id': paciente_id, \
	    'nome_paciente': paciente.nome })	

def relatorio_atendimentos_dia(request):

    form = RelatorioAtendimentosConsolidadoDiaForm()
    mensagem_erro = ''
    retorno = [];
    tratamento = ''

    if request.method == 'POST':
        form = RelatorioAtendimentosConsolidadoDiaForm(request.POST)

        if form.is_valid():
            data_in = form.cleaned_data['data']

            # retorna uma lista de dicionários
            aten_conf = Atendimento.objects.filter(instancia_tratamento__data = data_in, \
                status='A').values('instancia_tratamento__tratamento').annotate(numero=Count('instancia_tratamento__tratamento'))

            aten_nconf = Atendimento.objects.filter(instancia_tratamento__data = data_in, \
                status='C').values('instancia_tratamento__tratamento').annotate(numero=Count('instancia_tratamento__tratamento'))

            lista_ids_tratamentos = []
            for at in aten_conf:
                if at['instancia_tratamento__tratamento'] not in lista_ids_tratamentos:
                    lista_ids_tratamentos.append(at['instancia_tratamento__tratamento'])

            for at in aten_nconf:
                if at['instancia_tratamento__tratamento'] not in lista_ids_tratamentos:
                    lista_ids_tratamentos.append(at['instancia_tratamento__tratamento'])

            # gera uma única lista com os tratamentos
            conjunto = Set(lista_ids_tratamentos)
            lista_ids_tratamentos = list(conjunto)
            
            total_conf = 0
            total_nconf = 0
            
            for tratamento_id in lista_ids_tratamentos:
                numero_conf = 0
                numero_nconf = 0
                for at in aten_conf:
                    if at['instancia_tratamento__tratamento'] == tratamento_id:
                        numero_conf = at['numero']
                        total_conf += numero_conf
                        break

                for at in aten_nconf:
                    if at['instancia_tratamento__tratamento'] == tratamento_id:
                        numero_nconf = at['numero']
                        total_nconf += numero_nconf
                        break

                tratamento = Tratamento.objects.get(id=tratamento_id)
                numero_total = numero_conf + numero_nconf
                
                retorno.append({'tratamento': tratamento.descricao_basica, 'numero_conf': numero_conf, \
                    'numero_nconf': numero_nconf, 'numero_total': numero_total})
            
            
            if not retorno:
                mensagem_erro = 'Não há registros'
            else:
                retorno.append({'tratamento': 'Total', 'numero_conf': total_conf, \
                    'numero_nconf': total_nconf, 'numero_total': total_conf+total_nconf})
                
        else:
            mensagem_erro = 'Formulário inválido';

    return render_to_response('relatorio-atendimentos-dia.html', {'form':form, 
                            'mensagem': mensagem_erro,
                            'retorno':retorno})

def relatorio_atendimentos_mes(request):

    form = RelatorioAtendimentosConsolidadoMesForm()
    mensagem_erro = ''
    retorno = [];
    tratamento = ''
    lista_datas = []
    lista_datas_str = []
    debug = ''

    if request.method == 'POST':
        form = RelatorioAtendimentosConsolidadoMesForm(request.POST)

        if form.is_valid():
            data_in = form.cleaned_data['data']

            # retorna uma lista de dicionários
            atendimentos = Atendimento.objects.filter(instancia_tratamento__data__year = data_in.year, \
                instancia_tratamento__data__month = data_in.month, \
                status='A')

            for at in atendimentos:
                if at.instancia_tratamento.data not in lista_datas:
                    lista_datas.append(at.instancia_tratamento.data)
                    lista_datas_str.append(str(at.instancia_tratamento.data))

            lista_ids_tratamentos = []
            for at in atendimentos:
                if at.instancia_tratamento.tratamento.id not in lista_ids_tratamentos:
                    lista_ids_tratamentos.append(at.instancia_tratamento.tratamento.id)

            lista_ids_tratamentos.sort()
            for tratamento_id in lista_ids_tratamentos:
                ats_filtro = atendimentos.filter(instancia_tratamento__tratamento__id = tratamento_id)
                lista = ats_filtro.values('instancia_tratamento__data').annotate(numero=Count('instancia_tratamento__data'))
                dic = {}
                for item in lista:
                    data = item['instancia_tratamento__data']
                    dic[str(data)] = item['numero']

                lista_interna = []
                lista_interna.append(Tratamento.objects.get(id=tratamento_id).descricao_basica)
                soma_tratamento = 0
                for data in lista_datas:
                    if str(data) in dic.keys():
                        lista_interna.append(dic[str(data)])
                        soma_tratamento += dic[str(data)]
                    else:
                        lista_interna.append('-')
                lista_interna.append(soma_tratamento)
                retorno.append(lista_interna)

            if not retorno:
                mensagem_erro = 'Não há registros' +  debug
            else:
                lista_soma = ['Total']
                soma_tratamento = 0
                lista = atendimentos.values('instancia_tratamento__data').annotate(numero=Count('instancia_tratamento__data'))
                dic = {}
                for item in lista:
                    data = item['instancia_tratamento__data']
                    dic[str(data)] = item['numero']
                for data in lista_datas:
                    if str(data) in dic.keys():
                        lista_soma.append(dic[str(data)])
                        soma_tratamento += dic[str(data)]
                    else:
                        lista_soma.append('-')

                lista_soma.append(soma_tratamento)
                retorno.append(lista_soma)

        else:
            mensagem_erro = 'Formulário inválido';

    return render_to_response('relatorio-atendimentos-mes.html', {'form':form,
                            'mensagem': mensagem_erro,
                            'retorno':retorno,
                            'lista_rotulos':['Tratamento'] + lista_datas_str + ['Total']})

