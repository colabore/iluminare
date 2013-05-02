# -*- coding: utf-8 -*-
from    iluminare.tratamento.models     import Tratamento, InstanciaTratamento, TratamentoPaciente, AgendaTratamento
from    iluminare.atendimento.models    import Atendimento, Notificacao, AgendaAtendimento
from    iluminare.voluntario.models     import Voluntario, Trabalho

from    iluminare.paciente.models       import DetalhePrioridade, Paciente
import  iluminare.atendimento.logic     as logic_atendimento
import  iluminare.tratamento.logic      as tratamento_logic
import  iluminare.voluntario.logic      as voluntario_logic

from    django                          import forms
from    django.shortcuts                import render_to_response, get_object_or_404
from    django.forms.models             import modelformset_factory, BaseModelFormSet
from    django.core.paginator           import Paginator
from    django.http                     import HttpResponse
from    django.db.models                import Q
from    django.db                       import transaction
from    django.db.models                import Count
from    django.utils.encoding           import smart_str, smart_unicode

from    operator                        import itemgetter
from    sets                            import Set

from    exceptions                      import Exception

import  csv
import  sys
import  datetime
import  itertools
import  traceback



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
            
            # Verifica se o paciente tem algum agendamento para desobsessão no dia.
            # Caso positivo, a desobsessão passa a ser a opção default.
            try:
                # id=8: desobsessão
                desob = Tratamento.objects.get(id=8)
                ags = AgendaAtendimento.objects.filter(paciente = paciente, agenda_tratamento__tratamento=desob, \
                    agenda_tratamento__data=datetime.datetime.now().date)
                if (len(ags) >=1) and (desob in lista_trat):
                    self.fields['tratamento'].initial = desob
            except:
                pass

            # só atualiza a opção inicial do campo tratamento na segunda para Manutenção se não for voluntário.
            # Em geral, os voluntários não se tratam nas segundas. Logo, só farão os pontos de entrada e saída.
            # Notar que caso o paciente tenha um agendamento para a desob no dia, mas ainda estiver na manutenção,
            # a opção default na tela será a manutenção.
            if not volunt: 
                try:
                    manut = Tratamento.objects.get(id=7)
                    prim = Tratamento.objects.get(id=6)
                    s3s = Tratamento.objects.get(id=12)
                    ats = Atendimento.objects.filter(paciente = paciente).order_by("-instancia_tratamento__data")

                    # Verifica se o tratamento do paciente é Sala 3 - Segunda.
                    tratamentos = [tp.tratamento for tp in paciente.tratamentopaciente_set.filter(status='A')]
                    if s3s in tratamentos:
                        self.fields['tratamento'].initial = s3s

                    # Verifica se não terminou as manutenções.
                    if (manut in lista_trat) and (len(ats) >= 1) and (ats[0].instancia_tratamento.tratamento==manut or \
                        ats[0].instancia_tratamento.tratamento==prim):
                        self.fields['tratamento'].initial = manut
                except:
                    pass
        # AJUSTANDO A TELA PARA AS QUINTAS            
        elif datetime.date.today().weekday() == 3:
            self.fields['tratamento'].queryset = Tratamento.objects.filter(dia_semana = 'N')
            
            # só atualiza a opção inicial do campo tratamento na quinta se não for voluntário 
            # ou for um voluntário entrando na casa.
            # A ideia é que na saída só haja para o voluntário a opção ponto de saída.
            if not volunt:
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

@transaction.autocommit
def ajax_checkin_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    lista_atendimentos = Atendimento.objects.filter(paciente = paciente, status='A').order_by('-instancia_tratamento__data')
    
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
        notificacoes = get_notificacoes_validas(paciente, True, False)
        agendamentos = AgendaAtendimento.objects.filter(paciente = paciente, status = 'A')
        agendamentos_ok = []
        agendamentos_falta = []
        for agendamento in agendamentos:
            if agendamento.agenda_tratamento.data < datetime.datetime.today().date():
                agendamentos_falta.append(agendamento)
            else:
                agendamentos_ok.append(agendamento)

    return render_to_response('ajax-checkin-paciente.html', {'paciente':paciente, \
        'form':checkin_paciente_form, 'lista':lista_atendimentos, 'erros':str(checkin_paciente_form.errors), \
        'voluntario':voluntario, 'notificacoes':notificacoes, 'agendamentos_ok': agendamentos_ok,\
        'agendamentos_falta':agendamentos_falta})

def get_notificacoes_validas(paciente, tela_checkin, impressao):
    """
        Tratamos os 4 casos para as notificações:
        - Fixo
        - Por prazo (X dias, y meses)
        - Por validade (2013-04-10)
        - Por quantidade de atendimentos.
    """
    if tela_checkin:
        notificacoes = Notificacao.objects.filter(paciente = paciente, ativo=True, tela_checkin=tela_checkin)
    if impressao:
        notificacoes = Notificacao.objects.filter(paciente = paciente, ativo=True, impressao=impressao)

    lista = []
    for notificacao in notificacoes:
        if notificacao.fixo:
            lista.append(notificacao)
        elif notificacao.data_validade:
            if notificacao.data_validade >= datetime.date.today():
                lista.append(notificacao)
        elif notificacao.prazo_num:
            if notificacao.prazo_unidade == 'D':
                data_limite = notificacao.data_criacao + datetime.timedelta(days=notificacao.prazo_num)
            elif notificacao.prazo_unidade == 'S':
                data_limite = notificacao.data_criacao + datetime.timedelta(weeks=notificacao.prazo_num)
            elif notificacao.prazo_unidade == 'M':
                data_limite = notificacao.data_criacao + datetime.timedelta(days=30*notificacao.prazo_num)
            if data_limite >= datetime.date.today():
                lista.append(notificacao)
        elif notificacao.qtd_atendimentos:
            ats = Atendimento.objects.filter(paciente = paciente, \
                instancia_tratamento__data__gte=notificacao.data_criacao, status='A')
            if len(ats) < notificacao.qtd_atendimentos:
                lista.append(notificacao)
    return lista

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
           
            info_str = info_str + '[' + str(cont) + '] '

            # LISTA DE TRATAMENTOS
            tps = TratamentoPaciente.objects.filter(paciente = atendimento.paciente, status='A')
            tratamentos = ''
            for tp in tps:
                tratamentos = tratamentos + tp.tratamento.descricao_basica + ', '
            
            # retira o ', ' do final
            tratamentos = tratamentos[:-2]
            
            if tratamentos != "":
                info_str = info_str + '[' + tratamentos + '] '
            
            # [1a VEZ]
            # inclui o [1a vez] se o paciente também está realizando um atendimento de 1a vez no mesmo dia.
            # ATENCAO [1a VEZ] != [1o ATENDIMENTO]
            primeira_vez = Atendimento.objects.filter(paciente__id = atendimento.paciente.id, \
                instancia_tratamento__tratamento__descricao_basica__startswith = "Prime", \
                instancia_tratamento__data = datetime.datetime.today())
            if len(primeira_vez) == 1:
                info_str = info_str + '[1a vez] '
            
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
    # - Está fazendo check-in nas salas 1, 2, 3, 4 ou 5.
    # 
    if len(list(ats)) > 0 and len(list(atendimentos)) == 0 \
        and atendimento.instancia_tratamento.tratamento.descricao_basica[:4] == "Sala":
        ult_at = ats[0]
        if ult_at.instancia_tratamento.tratamento.descricao_basica[:4] == "Manu":
            info_str = info_str + '[1a quinta] '

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
                info_str = info_str + u'[Só tratamento] '
    except Voluntario.DoesNotExist:
        pass
    
    try:
        prioridade =  DetalhePrioridade.objects.filter(paciente__id = atendimento.paciente.id)
        if len(prioridade) > 0:
            if prioridade[0].tipo == 'C':
                info_str = info_str + '[C] '
            else:
                info_str = info_str + '[' + prioridade[0].get_tipo_display() + '] '
    except DetalhePrioridade.DoesNotExist:
        pass
    
    # PRIORIDADE SÓ NO DIA
    if atendimento.prioridade:
        info_str = info_str + '[Prioridade hoje] '
    
    # OBSERVACAO PRIORIDADE
    if atendimento.observacao_prioridade:   
        info_str = info_str + '[' + atendimento.observacao_prioridade + '] ' 

    # ACOMPANHA: ...
    if atendimento.paciente.acompanhante:
        dp = DetalhePrioridade.objects.filter(paciente = atendimento.paciente.acompanhante)
        at = Atendimento.objects.filter(paciente = atendimento.paciente.acompanhante, \
            instancia_tratamento__data = atendimento.instancia_tratamento.data)
        if dp and at:
            nome_prioridade = atendimento.paciente.acompanhante.nome[:15]+'...'
            info_str = info_str + '[Ac. ->: ' + unicode(nome_prioridade) + '] '

    # É ACOMPANHADO POR: ...
    # Verifica se o paciente em questão é acompanhado por alguém. Ou seja, se há algum paciente cujo acompanhante seja o 
    # paciente do atendimento em questão.
    # É importante notar que a semântica dos campos acompanhante e acompanhante_crianca é a seguinte: 
    # Na tela de cadastro do paciente, estamos chamando esses campos de acompanha 1 e acompanha 2.
    # Isso significa que para no registro do acompanhante, nós podemos incluir 2 acompanhados.
    # A variável ps receberá os pacientes que acompanham o paciente do atendimento (atendimento.paciente).
    ps = Paciente.objects.filter(Q(acompanhante = atendimento.paciente) | Q(acompanhante_crianca = atendimento.paciente))
    for p in ps:
        dp = DetalhePrioridade.objects.filter(paciente = atendimento.paciente)
        at = Atendimento.objects.filter(paciente = p, \
            instancia_tratamento__data = atendimento.instancia_tratamento.data)
        # verifica se o paciente de atendimento.paciente é prioridade e se p (o seu acompanhante) fez checkin no dia.
        if dp and at:
            nome_acompanhante = p.nome[:15]+'...'
            info_str = info_str + '[Ac. <-: ' + unicode(nome_acompanhante) + '] '

    # NOTIFICAÇÕES:
    notificacoes = get_notificacoes_validas(atendimento.paciente, False, True)
    for notificacao in notificacoes:
        info_str = info_str + '{' + unicode(notificacao.descricao) + '} '

    # CASAL:
    if atendimento.paciente.casado_com:
        at = Atendimento.objects.filter(paciente = atendimento.paciente.casado_com,
            instancia_tratamento = atendimento.instancia_tratamento)
        if at:
            info_str = info_str + '[Casal: ' + unicode(atendimento.paciente.casado_com.nome) + '] '

    return info_str
    
    
class ConfirmacaoAtendimentoForm(forms.ModelForm):
    """
        Esta confirmação é para todos os tratamentos, com exceção da primeira vez.
    """
    observacao = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly'}))
    senha = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class':'disabled', \
        'readonly':'readonly', 'size':'5'}))
    nome = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', \
        'readonly':'readonly', 'size':'25'}))
    hora_chegada = forms.TimeField(label='Cheg.',required=False, widget=forms.TextInput(attrs={'class':'disabled',\
        'readonly':'readonly', 'size':'6'}))
    confirma = forms.BooleanField(required = False, label= 'Conf.')
    redireciona = forms.ModelChoiceField(label='Redir.',queryset=Tratamento.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        super(ConfirmacaoAtendimentoForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['confirma', 'senha', 'nome', 'hora_chegada','observacao', 'redireciona']
        atendimento = kwargs.pop('instance')
        
        tratamento_desc = atendimento.instancia_tratamento.tratamento.descricao_basica
        tratamento = atendimento.instancia_tratamento.tratamento
        
        # CAREREGA O CAMPO REDIRECIONA
        if tratamento.id in [1,2,3,4,5,11]:
            self.fields['redireciona'].queryset=Tratamento.objects.filter(id__in=[1,2,3,4,5,11])
        elif tratamento.id in [7,12]:
            self.fields['redireciona'].queryset=Tratamento.objects.filter(id__in=[7,12])
        elif tratamento.id == 6:
            self.fields['redireciona'].queryset=Tratamento.objects.none()
            opcoes = (('X','---------'),) + Paciente.FREQUENCIA
        else:
            self.fields['redireciona'].queryset=Tratamento.objects.none()
                
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

        # CARREGA A OBSERVAÇÃO DO PACIENTE NA TOOLTIP
        self.fields['observacao'].widget.attrs['title'] = atendimento.observacao


    def save(self, commit=True):
        atendimento = super(ConfirmacaoAtendimentoForm, self).save(commit=False)
        confirma_in = self.cleaned_data['confirma']
        redireciona_in = self.cleaned_data['redireciona']

        try:
            if redireciona_in:
                atendimento_atual_str = atendimento.instancia_tratamento.tratamento.descricao_basica
                its = InstanciaTratamento.objects.filter(data=atendimento.instancia_tratamento.data,\
                    tratamento__descricao_basica=redireciona_in)
                # pode ser que ainda não haja a instancia tratamento para o tratamento no dia.
                # dificilmente isso ocorrerá em produção, pois esse processo é executado no final do dia.
                # mas é importante que esteja mais robusto, pois executamos testes com poucos dados.
                if not its:
                    tratamento = Tratamento.objects.get(descricao_basica=redireciona_in)
                    it = InstanciaTratamento(data=atendimento.instancia_tratamento.data, tratamento=tratamento)
                    it.save()
                else:
                    it = its[0]

                if it != atendimento.instancia_tratamento:
                    atendimento.instancia_tratamento = it
                    obs = atendimento.observacao
                    atendimento.observacao = obs + \
                                            '[Checkin: ' + \
                                            smart_unicode(atendimento_atual_str) + \
                                            ' / Hoje foi para '+ \
                                            smart_unicode(str(redireciona_in))+'] ' 
            if confirma_in:
                atendimento.status = 'A'
                
                # verifica se há algum agendamento para esse tratamento que esteja aberto.
                # em caso positivo, o agendamento será fechado.
                ag_ats = AgendaAtendimento.objects.filter(paciente = atendimento.paciente, \
                    agenda_tratamento__tratamento=atendimento.instancia_tratamento.tratamento, status='A')
                if len(ag_ats) > 0:
                    ag_ats[0].status = 'F'
                    ag_ats[0].save()

                # se o tratamento for primeira vez, aproveitamos para atualizar o campo tem ficha.
                if atendimento.instancia_tratamento.tratamento.descricao_basica[:4] == 'Prim':
                    atendimento.paciente.tem_ficha = True
                    atendimento.paciente.save()
            else:
                atendimento.status = 'C'
            if commit:
                atendimento.save()
            
        except:
            traceback.print_exc()

    class Meta:
        model = Atendimento
        exclude = ['prioridade', 'instancia_tratamento', 'senha', 'observacao_prioridade', 'paciente', 'hora_atendimento', 'status']
          
class ConfirmacaoAtendimentoPrimeiraVezForm(forms.ModelForm):
    observacao = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly'}))
    senha = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'5'}))
    nome = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'25'}))
    hora_chegada = forms.TimeField(label='Cheg.',required=False, widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly', 'size':'6'}))
    confirma = forms.BooleanField(required = False, label= 'Conf.')
    encaminha = forms.ModelChoiceField(label='Enc.', queryset=Tratamento.objects.none(), required=False)
    frequencia = forms.ChoiceField(label='Freq', choices=(('X','---------'),) , required=False)

    def __init__(self, *args, **kwargs):
        super(ConfirmacaoAtendimentoPrimeiraVezForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['confirma', 'senha', 'nome', 'hora_chegada','observacao', 'encaminha', 'frequencia']
        atendimento = kwargs.pop('instance')
        
        tratamento_desc = atendimento.instancia_tratamento.tratamento.descricao_basica

        tratamento = atendimento.instancia_tratamento.tratamento
        
        # CAREREGA O CAMPO ENCAMINHA
        if tratamento.id == 6:
            self.fields['encaminha'].queryset=Tratamento.objects.filter(id__in=[1,2,3,4,5,12])
            opcoes = (('X','---------'),) + Paciente.FREQUENCIA
            self.fields['frequencia'].choices=opcoes
        else:
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

        # CARREGA A OBSERVAÇÃO DO PACIENTE NA TOOLTIP
        self.fields['observacao'].widget.attrs['title'] = atendimento.observacao

    def save(self, commit=True):
        atendimento = super(ConfirmacaoAtendimentoPrimeiraVezForm, self).save(commit=False)
        confirma_in = self.cleaned_data['confirma']
        encaminha_in = self.cleaned_data['encaminha']
        frequencia_in = self.cleaned_data['frequencia']
             
        if encaminha_in:
            tratamento = Tratamento.objects.get(descricao_basica = encaminha_in)
            if tratamento:
                lista_t = []
                lista_t.append(tratamento)
                tratamento_logic.encaminhar_paciente(atendimento.paciente.id, lista_t)
                obs = atendimento.observacao 
                atendimento.observacao = obs + '[Encaminhado para '+str(encaminha_in)+'] '
        
        if frequencia_in != 'X':
            # significa que se trata de um atendimento de primeira vez, pois somente estes podem ser alterados.
            atendimento.paciente.frequencia = frequencia_in
            atendimento.paciente.save()
            obs = atendimento.observacao 
            atendimento.observacao = obs + '[Freq: '+str(frequencia_in)+'] '


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

ConfirmacaoAtendimentoPrimeiraVezFormSet = modelformset_factory(Atendimento, extra=0,
    form=ConfirmacaoAtendimentoPrimeiraVezForm)


def confirmacao(request):
    """
    O que preciso melhorar nesta função?
    Ela precisa se tornar dinâmica, isto é, o segundo form (lista de atendimentos) precisa ser dependente da escolha 
    do atendimento.
    Os atendimentos de primeira vez terão campos específicos, como o diagnosticador.. 

    Consegui torna-la dinâmica, mas com um código não muito otimizado.
    Estou criando dois formsets quase idênticos e utilizando os dois. Em função da confirmação que está sendo feita,
    um dos formsets será nulo.
    """
    mensagem_erro = ""
    mensagem_sucesso = ""
    if request.method == 'POST':
        filtro_form = FiltroAtendimentosForm(request.POST)
        atendimentos = ConfirmacaoAtendimentoFormSet(queryset=Atendimento.objects.none())
        atendimentos_pv = ConfirmacaoAtendimentoPrimeiraVezFormSet(queryset=Atendimento.objects.none())
        
        if 'pesquisar' in request.POST:
            if filtro_form.is_valid():
                tratamento = filtro_form.cleaned_data['tratamento']
                data	   = filtro_form.cleaned_data['data']
                
                if tratamento.descricao_basica[:4] == 'Prim':
                    atendimentos_pv = ConfirmacaoAtendimentoPrimeiraVezFormSet(queryset= \
                        Atendimento.objects.filter(instancia_tratamento__data=data,instancia_tratamento__tratamento=tratamento))
                    atendimentos = ConfirmacaoAtendimentoFormSet(queryset=Atendimento.objects.none())
                else:
                    atendimentos = ConfirmacaoAtendimentoFormSet(queryset= \
                        Atendimento.objects.filter(instancia_tratamento__data=data,instancia_tratamento__tratamento=tratamento))
                    atendimentos_pv = ConfirmacaoAtendimentoPrimeiraVezFormSet(queryset=Atendimento.objects.none())
                
                if not atendimentos and not atendimentos_pv:
                    mensagem_erro = 'Nenhum atendimento nesta data.'
            else:
                mensagem_erro = 'Erro no formulário. Verificar se todos os campos ' + \
                    'foram devidamente preenchidos e se a data está correta.'

        elif 'salvar' in request.POST:
            """
                PRECISA MELHORAR..
                Imaginei que somente um dos formsets (atendimentos ou atendimentos_pv) 
                fossem vir com dados.. Mas os dois estão vindo com dados, e idênticos.
                O que vou fazer é ver qual o tratamento e forçar o outro formset para nulo.
            """
            atendimentos = ConfirmacaoAtendimentoFormSet(request.POST)
            atendimentos_pv = ConfirmacaoAtendimentoPrimeiraVezFormSet(request.POST)
            try:
                if atendimentos.total_form_count() != 0 and atendimentos_pv.total_form_count() != 0:
                    if atendimentos_pv[0].instance.instancia_tratamento.tratamento.descricao_basica[:4] == 'Prim':
                        atendimentos = ConfirmacaoAtendimentoFormSet(queryset=Atendimento.objects.none())
                        if atendimentos_pv.is_valid():
                            atendimentos_pv.save()
                            mensagem_sucesso = mensagem_sucesso + 'Dados salvos com sucesso.'
                        else:
                            mensagem_erro = mensagem_erro + 'Erro. Verificar dados inseridos. 1'
                    else:
                        atendimentos_pv = ConfirmacaoAtendimentoPrimeiraVezFormSet(queryset=Atendimento.objects.none())
                        if atendimentos.is_valid():
                            atendimentos.save()
                            mensagem_sucesso = mensagem_sucesso + 'Dados salvos com sucesso.'
                        else:
                            mensagem_erro = mensagem_erro + 'Erro. Verificar dados inseridos. 2'
            except:
                mensagem_erro = str(atendimentos_pv.queryset) + '- ' + str(atendimentos_pv.total_form_count()) + \
                    str(atendimentos.queryset) + '-' + str(atendimentos.total_form_count())
        else:
            mensagem_erro = mensagem_erro + 'Erro na página. Contactar suporte.'

    else:
        filtro_form = FiltroAtendimentosForm()
        atendimentos = ConfirmacaoAtendimentoFormSet(queryset=Atendimento.objects.none())
        atendimentos_pv = ConfirmacaoAtendimentoPrimeiraVezFormSet(queryset=Atendimento.objects.none())
    
    return render_to_response('confirmacao_atendimentos.html', {'filtro_form':filtro_form, 
        'atendimentos':atendimentos, 'mensagem':'', 'titulo': 'CONFIRMAR ATENDIMENTOS', 
        'mensagem_sucesso': mensagem_sucesso, 'mensagem_erro': mensagem_erro, 'atendimentos_pv':atendimentos_pv
        })

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

class ImprimirListagemCriancaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ImprimirListagemCriancaForm, self).__init__(*args, **kwargs)
        self.fields['tratamento'].choices = [('', '----------')] + \
            [(tratamento.id, tratamento.descricao_basica) for tratamento in Tratamento.objects.all()]
        # o id do tratamento Sala 9 é 11. Deixei esse valor na mão.
        self.fields['tratamento'].initial = 11

    tratamento = forms.ChoiceField(choices=())
    data = forms.DateField(initial = datetime.date.today)
    crianca = forms.BooleanField(required = False, initial=True)
    outros = forms.BooleanField(required = False)

class ListagemGeralForm(forms.Form):

	def __init__(self, *args, **kwargs):
        	super(ListagemGeralForm, self).__init__(*args, **kwargs)

	data = forms.DateField(initial = datetime.date.today)

class ListagemGeralFechamentoForm(forms.Form):

    data = forms.DateField(initial = datetime.date.today, required=True)
    tratamento = forms.ChoiceField(choices=(), required=False)
    paciente = forms.CharField(required = False, widget=forms.TextInput(attrs={'size':'20'}))

    def __init__(self, *args, **kwargs):
        super(ListagemGeralFechamentoForm, self).__init__(*args, **kwargs)
        self.fields['tratamento'].choices = [('-', '----------')] + \
            [(tratamento.id, tratamento.descricao_basica) for tratamento in Tratamento.objects.all()]
        self.fields.keyOrder = ['paciente', 'tratamento', 'data']


class RelatorioAtendimentosConsolidadoDiaForm(forms.Form):

	def __init__(self, *args, **kwargs):
        	super(RelatorioAtendimentosConsolidadoDiaForm, self).__init__(*args, **kwargs)

	data = forms.DateField(initial = datetime.date.today)

class RelatorioAtendimentosConsolidadoMesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(RelatorioAtendimentosConsolidadoMesForm, self).__init__(*args, **kwargs)

    data = forms.DateField(initial = datetime.date.today)


def get_lista_atendimentos_previstos(instancia_tratamento, prioridade, voluntario):
    atendimentos_previstos = []

    if instancia_tratamento:
        if not prioridade:
            atendimentos_previstos = Atendimento.objects.filter(instancia_tratamento = instancia_tratamento)
        else:
            # PACIENTES QUE SÃO PRIORIDADE
            atendimentos_previstos1 = Atendimento.objects.filter(instancia_tratamento=instancia_tratamento). \
                exclude(paciente__detalheprioridade=None)

            # PACIENTES QUE SÃO PRIORIDADE NO DIA
            atendimentos_previstos2 = Atendimento.objects.filter(prioridade=True, \
                instancia_tratamento=instancia_tratamento)

            # ACOMPANHANTES
            atendimentos_previstos3 = Atendimento.objects.filter(Q(instancia_tratamento=instancia_tratamento) \
                & ~Q(paciente__acompanhante=None))

            atendimentos_previstos = []
            for at in atendimentos_previstos1:
                if at not in atendimentos_previstos:
                    atendimentos_previstos.append(at)
            for at in atendimentos_previstos2:
                if at not in atendimentos_previstos:
                    atendimentos_previstos.append(at)
            for at in atendimentos_previstos3:
                dps = DetalhePrioridade.objects.filter(paciente = at.paciente.acompanhante)
                ats = Atendimento.objects.filter(paciente = at.paciente.acompanhante, \
                    instancia_tratamento__data = at.instancia_tratamento.data)
                # garante que a pessoa que é acompanha é uma prioridade e que ela fez check-in no dia.
                if dps and ats:
                    if at not in atendimentos_previstos:
                        atendimentos_previstos.append(at)

    return atendimentos_previstos

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
            tratamento = Tratamento.objects.get(id=tratamento_in)

            try:
                instancia_tratamento = InstanciaTratamento.objects.get(tratamento = tratamento, data = data_in)
            except:
                instancia_tratamento = None

            if instancia_tratamento:
                # lista de atendimentos previstos para o tratamento no dia.
                atendimentos_previstos = get_lista_atendimentos_previstos(instancia_tratamento,  prioridade_in, 
                    voluntario_in)
                
                voluntarios = Voluntario.objects.filter(ativo=True)
                pacientes_voluntarios = [v.paciente for v in voluntarios]
                    
                for atendimento in atendimentos_previstos:
                    prioridade = False
                    dps = DetalhePrioridade.objects.filter(paciente = atendimento.paciente)
                    eh_acompanhante = False
                    # quando acompanha algum paciente prioridade também é prioridade..
                    if atendimento.paciente.acompanhante:
                        dp = DetalhePrioridade.objects.filter(paciente = atendimento.paciente.acompanhante)
                        at = Atendimento.objects.filter(paciente = atendimento.paciente.acompanhante, \
                            instancia_tratamento__data = atendimento.instancia_tratamento.data)
                        if dp and at:
                            eh_acompanhante = True

                    # 3 casos possíveis de prioridade: prioridade no dia, prioridade em si, acompanha prioridade.
                    if atendimento.prioridade or dps or eh_acompanhante:
                        prioridade = True

                    if voluntario_in:
                        if atendimento.paciente in pacientes_voluntarios:
                            info_str = retornaInfo(atendimento)
                            retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, \
                                'info': info_str, 'prioridade': prioridade, 'senha':atendimento.senha})
                    else:
                        info_str = retornaInfo(atendimento)
                        retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, \
                            'info': info_str, 'prioridade': prioridade, 'senha':atendimento.senha})
                        
                            
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
                            'tratamento':tratamento,
                            'titulo':'IMPRIMIR ATENDIMENTOS'})

def exibir_listagem_criancas(request, pagina = None):
    form_listagem = ImprimirListagemCriancaForm()
    mensagem_erro = ''
    retorno = [];
    tratamento = ''

    if request.method == 'POST':
        form_listagem = ImprimirListagemCriancaForm(request.POST)
        if form_listagem.is_valid():
            data_in = form_listagem.cleaned_data['data']
            tratamento_in = form_listagem.cleaned_data['tratamento']
            crianca = form_listagem.cleaned_data['crianca']
            outros = form_listagem.cleaned_data['outros']

            tratamento = Tratamento.objects.get(id=tratamento_in)

            try:
                instancia_tratamento = InstanciaTratamento.objects.get(tratamento = tratamento, data = data_in)
            except:
                instancia_tratamento = None

            if instancia_tratamento:
                # lista de atendimentos previstos para o tratamento no dia.
                atendimentos_previstos = []
                if crianca:
                    atendimentos_previstos = Atendimento.objects.filter(instancia_tratamento = instancia_tratamento, 
                        paciente__detalheprioridade__tipo='C')
                    for atendimento in atendimentos_previstos:
                        info_str = retornaInfo(atendimento)
                        retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, \
                            'info': info_str, 'prioridade': True, 'senha':atendimento.senha})

                if outros:
                    atendimentos_previstos = Atendimento.objects.filter(instancia_tratamento=instancia_tratamento). \
                        exclude(paciente__detalheprioridade__tipo='C')
                    for atendimento in atendimentos_previstos:
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


    return render_to_response('listagem-impressao-criancas.html', {'form_listagem':form_listagem, 
                            'mensagem': mensagem_erro,
                            'pagina_atual':pagina_atual,
                            'tratamento':tratamento,
                            'titulo':'IMPRIMIR ATENDIMENTOS DAS CRIANÇAS'})


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
                            'tratamento':tratamento,
                            'titulo': 'LISTAGEM GERAL DE ATENDIMENTOS'})

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
            paciente_in = form_listagem.cleaned_data['paciente']

            if tratamento_in == '-':
                if paciente_in:
                    atendimentos = Atendimento.objects.filter(instancia_tratamento__data = data_in, \
                        paciente__nome__icontains=paciente_in).order_by('-hora_chegada')
                else:
                    atendimentos = Atendimento.objects.filter(instancia_tratamento__data = data_in).order_by('-hora_chegada')
            else:
                if paciente_in:
                    atendimentos = Atendimento.objects.filter(instancia_tratamento__data = data_in, \
                        instancia_tratamento__tratamento__id = tratamento_in, 
                        paciente__nome__icontains=paciente_in).order_by('-hora_chegada')
                else:
                    atendimentos = Atendimento.objects.filter(instancia_tratamento__data = data_in, \
                        instancia_tratamento__tratamento__id = tratamento_in).order_by('-hora_chegada')
                
            for atendimento in atendimentos:
                info_str = retornaInfo(atendimento)
                retorno.append({'nome': atendimento.paciente, 'hora': atendimento.hora_chegada, 'info': info_str, 'prioridade': False, \
                    'sala': atendimento.instancia_tratamento.tratamento.descricao_basica, 'senha':atendimento.senha, \
                    'status':atendimento.status, 'observacao':atendimento.observacao, 'id':atendimento.id})

            if not retorno:
                mensagem_erro = 'Não há registros'
        else:
            mensagem_erro = 'Formulário inválido';

    return render_to_response('listagem-diaria-geral-fechamento.html', {'form_listagem_fechamento':form_listagem, 
                            'mensagem': mensagem_erro,
                            'retorno':retorno,
                            'tratamento':tratamento,
                            'titulo': 'CONFIRMAR ATENDIMENTOS - DETALHES'})

class ListagemNotificacoesForm(forms.Form):

    data = forms.DateField(initial = datetime.date.today, required=False)
    tratamento = forms.ChoiceField(choices=(), required=False)
    paciente = forms.CharField(required = False, widget=forms.TextInput(attrs={'size':'20'}))

    def __init__(self, *args, **kwargs):
        super(ListagemNotificacoesForm, self).__init__(*args, **kwargs)
        self.fields['tratamento'].choices = [('-', '----------')] + \
            [(tratamento.id, tratamento.descricao_basica) for tratamento in Tratamento.objects.all()]
        self.fields.keyOrder = ['paciente', 'tratamento', 'data']


def exibir_listagem_notificacoes(request):

    form_listagem = ListagemNotificacoesForm()
    mensagem_erro = ''
    notificacoes = []

    if request.method == 'POST':
        form_listagem = ListagemNotificacoesForm(request.POST)

        if form_listagem.is_valid():
            data_in = form_listagem.cleaned_data['data']
            tratamento_in = form_listagem.cleaned_data['tratamento']
            paciente_in = form_listagem.cleaned_data['paciente']

            if tratamento_in == '-':
                if paciente_in:
                    if data_in:
                        notificacoes = Notificacao.objects.filter(data_criacao = data_in, \
                            paciente__nome__icontains=paciente_in).order_by('-atendimento__instancia_tratamento__data')
                    else:
                        notificacoes = Notificacao.objects.filter(paciente__nome__icontains=paciente_in).\
                            order_by('-atendimento__instancia_tratamento__data')
                else:
                    if data_in:
                        notificacoes = Notificacao.objects.filter(data_criacao = data_in).\
                            order_by('-atendimento__instancia_tratamento__data')
                    else:
                        notificacoes = Notificacao.objects.all().order_by('-atendimento__instancia_tratamento__data')[:50]
            else:
                if paciente_in:
                    if data_in:
                        notificacoes = Notificacao.objects.filter(data_criacao = data_in, \
                            paciente__nome__icontains=paciente_in, atendimento__instancia_tratamento__tratamento__id=\
                            tratamento_in).order_by('-atendimento__instancia_tratamento__data')
                    else:
                        notificacoes = Notificacao.objects.filter(\
                            paciente__nome__icontains=paciente_in, atendimento__instancia_tratamento__tratamento__id=\
                            tratamento_in).order_by('-atendimento__instancia_tratamento__data')
                else:
                    if data_in:
                        notificacoes = Notificacao.objects.filter(data_criacao = data_in, \
                            atendimento__instancia_tratamento__tratamento__id=\
                            tratamento_in).order_by('-atendimento__instancia_tratamento__data')
                    else:
                        notificacoes = Notificacao.objects.filter(atendimento__instancia_tratamento__tratamento__id=\
                            tratamento_in).order_by('-atendimento__instancia_tratamento__data')
            if not notificacoes:
                mensagem_erro = 'Nenhuma notificação encontrada.'
        else:
            mensagem_erro = 'Erro nos parâmetros. Verificar se os campos foram devidamente preenchidos.';

    return render_to_response('listagem-notificacoes.html', {'form_listagem':form_listagem,
                            'mensagem_erro': mensagem_erro,
                            'notificacoes':notificacoes,
                            'titulo': 'LISTAGEM DE NOTIFICAÇÕES'})

class ListagemAgendamentosForm(forms.Form):

    # quando agendou
    data_marcacao = forms.DateField(required=False)
    # para quando agendou
    data_prevista = forms.DateField(required=False)
    # incluir agendamentos sem data
    # esse campo é necessário, pois há casos em que os tratamentos não tem data prevista.
    sem_data = forms.BooleanField(required = False, initial=False)
    # tratamento de onde originou o agendamento
    tratamento_marcacao = forms.ChoiceField(choices=(), required=False)
    # tratamento realmente agendado
    tratamento_agendado = forms.ChoiceField(choices=(), required=False)
    paciente = forms.CharField(required = False)
    status = forms.ChoiceField(choices=(), required=False)

    def __init__(self, *args, **kwargs):
        super(ListagemAgendamentosForm, self).__init__(*args, **kwargs)
        self.fields['tratamento_marcacao'].choices = [('-', '----------')] + \
            [(tratamento.id, tratamento.descricao_basica) for tratamento in Tratamento.objects.all()]
        self.fields['tratamento_agendado'].choices = [('-', '----------')] + \
            [(tratamento.id, tratamento.descricao_basica) for tratamento in Tratamento.objects.all()]
        self.fields['status'].choices = [('-', '----------')] + list(AgendaAtendimento.STATUS)
        self.fields['status'].initial = 'A'

def exibir_listagem_agendamentos(request):

    form_listagem = ListagemAgendamentosForm()
    mensagem_erro = ''
    agendamentos = []

    if request.method == 'POST':
        form_listagem = ListagemAgendamentosForm(request.POST)

        try:
            if form_listagem.is_valid():
                data_prevista_in = form_listagem.cleaned_data['data_prevista']
                sem_data_in = form_listagem.cleaned_data['sem_data']
                data_marcacao_in = form_listagem.cleaned_data['data_marcacao']
                tratamento_agendado_in = form_listagem.cleaned_data['tratamento_agendado']
                tratamento_marcacao_in = form_listagem.cleaned_data['tratamento_marcacao']
                paciente_in = form_listagem.cleaned_data['paciente']
                status_in = form_listagem.cleaned_data['status']

                if data_prevista_in:
                    if sem_data_in:
                        agendamentos = AgendaAtendimento.objects.filter(Q(agenda_tratamento__data = data_prevista_in) | \
                            Q(agenda_tratamento__data = None))
                    else:
                        agendamentos = AgendaAtendimento.objects.filter(agenda_tratamento__data = data_prevista_in)
                else:
                    if sem_data_in:
                        agendamentos = AgendaAtendimento.objects.filter(Q(agenda_tratamento__data = None))
                    else:
                        agendamentos = AgendaAtendimento.objects.all()

                if data_marcacao_in:
                    agendamentos = agendamentos.filter(data_criacao = data_marcacao_in)

                if tratamento_agendado_in != '-':
                    agendamentos = agendamentos.filter(agenda_tratamento__tratamento__id=tratamento_agendado_in)

                if tratamento_marcacao_in != '-':
                    agendamentos = agendamentos.filter(atendimento_origem__instancia_tratamento__tratamento__id=\
                        tratamento_marcacao_in)

                if paciente_in != '-':
                    agendamentos = agendamentos.filter(paciente__nome__icontains=paciente_in)

                if status_in != '-':
                    agendamentos = agendamentos.filter(status = status_in)

                if not agendamentos:
                        mensagem_erro = 'Nenhum agendamento encontrado.'
            else:
                mensagem_erro = 'Erro nos parâmetros. Verificar se os campos foram devidamente preenchidos.';
        except:
            traceback.print_exc()

    return render_to_response('listagem-agendamentos.html', {'form_listagem':form_listagem,
                            'mensagem_erro': mensagem_erro,
                            'agendamentos':agendamentos,
                            'titulo': 'LISTAGEM DE AGENDAMENTOS'})



def exibir_atendimentos_paciente(request, paciente_id, pagina = None):
	lista_atendimentos = Atendimento.objects.filter(paciente__id = paciente_id).order_by('-instancia_tratamento__data')

	mensagem_erro = ''
	retorno   = [];
	paciente = Paciente.objects.get(id=paciente_id)
	
	
	for atendimento in lista_atendimentos:
		hora_chegada = '-'
		if atendimento.hora_chegada != None:
		    hora_chegada = atendimento.hora_chegada
		observacao = '-'
		if atendimento.observacao != None:
		    observacao = atendimento.observacao

		retorno.append({'data':	atendimento.instancia_tratamento.data, \
		    'tratamento':  atendimento.instancia_tratamento.tratamento.descricao_basica, \
		    'hora_chegada': hora_chegada, 'observacao': observacao, 'status':atendimento.status})
	
	if not retorno:
		mensagem_erro = 'Não foi possível localizar usuário'
		
	paginacao = Paginator(retorno,45)
	if pagina == None:
		num_pagina = 1
	else:	
		num_pagina = int(pagina)
	pagina_atual = paginacao.page(num_pagina)	
	
	return render_to_response('lista-atendimentos.html',{'mensagem': mensagem_erro, \
	    'pagina_atual': pagina_atual, 'paciente_id': paciente_id, 'nome_paciente': paciente.nome,
	    'titulo': 'LISTAGEM DE ATENDIMENTOS' })

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
                            'retorno':retorno,
                            'titulo': 'RELATÓRIO - ATENDIMENTOS POR DIA'})

def relatorio_atendimentos_mes_geral(data_ordinal):
    mensagem_erro = ''
    retorno = []
    tratamento = ''
    lista_datas = []
    lista_rotulos = []
    debug = ''

    data_in = datetime.date.fromordinal(int(data_ordinal))
    # retorna uma lista de dicionários
    atendimentos = Atendimento.objects.filter(instancia_tratamento__data__year = data_in.year, \
        instancia_tratamento__data__month = data_in.month, \
        status='A')

    lista_ids_tratamentos = []
    for at in atendimentos:
        if at.instancia_tratamento.tratamento.id not in lista_ids_tratamentos:
            lista_ids_tratamentos.append(at.instancia_tratamento.tratamento.id)
        if at.instancia_tratamento.data not in lista_datas:
            lista_datas.append(at.instancia_tratamento.data)

    lista_ids_tratamentos.sort()
    lista_datas.sort()
    for tratamento_id in lista_ids_tratamentos:
        ats_filtro = atendimentos.filter(instancia_tratamento__tratamento__id = tratamento_id)
        lista = ats_filtro.values('instancia_tratamento__data').annotate(numero=Count('instancia_tratamento__data'))
        dic = {}
        for item in lista:
            data = item['instancia_tratamento__data']
            dic[str(data)] = item['numero']

        lista_interna = []
        lista_interna.append(smart_str(Tratamento.objects.get(id=tratamento_id).descricao_basica))
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

    lista_rotulos = ['Tratamento'] + [str(data) for data in lista_datas] + ['Total']
    return mensagem_erro, retorno, lista_rotulos

def relatorio_atendimentos_mes(request):

    form = RelatorioAtendimentosConsolidadoMesForm()
    mensagem_erro = ''
    retorno = []
    tratamento = ''
    lista_datas = []
    data_ordinal = ''
    lista_rotulos = []
    debug = ''

    if request.method == 'POST':
        form = RelatorioAtendimentosConsolidadoMesForm(request.POST)

        if form.is_valid():
            data_in = form.cleaned_data['data']
            data_ordinal = data_in.toordinal()
            mensagem_erro, retorno, lista_rotulos = relatorio_atendimentos_mes_geral(data_ordinal)
        else:
            mensagem_erro = 'Formulário inválido';

    return render_to_response('relatorio-atendimentos-mes.html', {'form':form,
                            'mensagem': mensagem_erro,
                            'retorno':retorno,
                            'lista_rotulos': lista_rotulos,
                            'data_ordinal':data_ordinal,
                            'titulo': 'RELATÓRIO - ATENDIMENTOS POR MÊS'})

def relatorio_atendimentos_mes_csv(request, data_ordinal):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=relatorio_atendimentos_mes.csv'

    writer = csv.writer(response)
    mensagem_erro, retorno, lista_rotulos = relatorio_atendimentos_mes_geral(data_ordinal)
    writer.writerow(lista_rotulos)
    for element in retorno:
        writer.writerow(element)

    return response

class AtualizarPaciente_ConfirmacaoForm(forms.Form):
    tratamento              = forms.ModelChoiceField(queryset=Tratamento.objects.all(),required=False)
    frequencia              = forms.ChoiceField(required=False)
    prioridade              = forms.ChoiceField(required=False)
    observacao_atendimento  = forms.CharField(max_length=200, required=False)

    def __init__(self, *args, **kwargs):
        super(AtualizarPaciente_ConfirmacaoForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['tratamento', 'frequencia', 'prioridade', 'observacao_atendimento']
        self.fields['tratamento'].queryset=Tratamento.objects.filter(id__in=[1,2,3,11,4,5,12,7]).order_by("descricao_basica")
        self.fields['frequencia'].choices=opcoes = (('X','---------'),) + Paciente.FREQUENCIA
        self.fields['prioridade'].choices=opcoes = (('X','---------'),) + DetalhePrioridade.TIPO

    def save(self, atendimento):
        tratamento_in = self.cleaned_data['tratamento']
        frequencia_in = self.cleaned_data['frequencia']
        prioridade_in = self.cleaned_data['prioridade']
        observacao_atendimento_in = self.cleaned_data['observacao_atendimento']

        mensagens_list = []

        if tratamento_in:
            tratamento = Tratamento.objects.get(descricao_basica = tratamento_in)
            if tratamento:
                lista_t = []
                lista_t.append(tratamento)
                try:
                    # ainda preciso ajustar as mensagens.. quando caracteres como ç ou acentos, dá problemas..
                    # mesmo com o smart_str, que utilizo em outras partes do código, está dando problemas.
                    tratamento_logic.encaminhar_paciente(atendimento.paciente.id, lista_t)
                    dic_retorno = {}
                    dic_retorno['sucesso'] = True
                    dic_retorno['mensagem'] = smart_str("Mudanca de tratamento realizada com sucesso: \
                        %s " % tratamento.descricao_basica)
                    obs = atendimento.observacao
                    if not obs:
                        obs = ''
                    atendimento.observacao = obs + "[Encaminhado para "+str(tratamento_in)+"] "
                except:
                    mensagem = smart_str("Erro na mudanca do tratamento.")
                    dic_retorno = {'sucesso':False, 'mensagem':mensagem}
                    traceback.print_exc()
                mensagens_list.append(dic_retorno)

        if frequencia_in != 'X':
            atendimento.paciente.frequencia = frequencia_in
            try:
                atendimento.paciente.save()
                dic_retorno = {'sucesso':True, 'mensagem':'Ajuste da frequencia realizada com sucesso. Frequencia ' + \
                    atendimento.paciente.get_frequencia_display()}
                obs = atendimento.observacao
                if not obs:
                    obs = ''
                atendimento.observacao = obs + '[Freq: '+str(frequencia_in)+'] '
            except:
                dic_retorno = {'sucesso':False, 'mensagem':'Erro no ajuste da frequencia.'}
                traceback.print_exc()
            mensagens_list.append(dic_retorno)
        if prioridade_in != 'X':
            try:
                detalhe_prioridade = DetalhePrioridade.objects.get(paciente=atendimento.paciente)
            except:
                detalhe_prioridade = None
            if detalhe_prioridade:
                detalhe_prioridade.tipo = prioridade_in
            else:
                detalhe_prioridade = DetalhePrioridade(paciente = atendimento.paciente, tipo=prioridade_in)
            try:
                detalhe_prioridade.save()
                dic_retorno = {'sucesso':True, 'mensagem':'Prioridade ajustada com sucesso: ' \
                    + detalhe_prioridade.get_tipo_display()}
                obs = atendimento.observacao
                if not obs:
                    obs = ''
                atendimento.observacao = obs + '[Prior: '+detalhe_prioridade.get_tipo_display()+'] '
            except:
                dic_retorno = {'sucesso':False, 'mensagem':'Erro no estabelecimento da prioridade.'}
                traceback.print_exc()
            mensagens_list.append(dic_retorno)
        if observacao_atendimento_in:
            try:
                obs = atendimento.observacao
                if not obs:
                    obs = ''
                atendimento.observacao = obs + '['+observacao_atendimento_in+'] '
                dic_retorno = {'sucesso':True, 'mensagem':'Observacao ajustada com sucesso: '+obs}
            except:
                dic_retorno = {'sucesso':False, 'mensagem':'Observacao nao registrada.'}
                traceback.print_exc()
            mensagens_list.append(dic_retorno)

        atendimento.save()
        return (atendimento.paciente, mensagens_list)
        
class AgendamentoForm(forms.Form):
    fone                            = forms.CharField(max_length=45, required=False)
    agenda_tratamento_acolhimento   = forms.ChoiceField(choices=(),required=False)
    agenda_tratamento_desobsessao   = forms.ChoiceField(choices=(),required=False)
    agenda_tratamento_af            = forms.ChoiceField(choices=(),required=False)

    def __init__(self, *args, **kwargs):
        super(AgendamentoForm, self).__init__(*args, **kwargs)
        acolhimento = Tratamento.objects.get(id=10)
        ats = AgendaTratamento.objects.filter(tratamento = acolhimento, data__gte=datetime.date.today())
        choices = (('X','---------'),) + tuple([(at.id,at.data) for at in ats]) + (('N','Sem data'),)
        self.fields['agenda_tratamento_acolhimento'].choices= choices

        desob = Tratamento.objects.get(id=8)
        ats = AgendaTratamento.objects.filter(tratamento = desob, data__gte=datetime.date.today())
        choices = (('X','---------'),) + tuple([(at.id,at.data) for at in ats]) + (('N','Sem data'),)
        self.fields['agenda_tratamento_desobsessao'].choices=choices

        af = Tratamento.objects.get(id=9)
        ats = AgendaTratamento.objects.filter(tratamento = af, data__gte=datetime.date.today())
        choices = (('X','---------'),) + tuple([(at.id,at.data) for at in ats]) + (('N','Sem data'),)
        self.fields['agenda_tratamento_af'].choices=choices

        self.fields['fone'].widget.attrs['title'] = 'Telefone do paciente. Caso o telefone informado ' + \
            'na fichinha não seja o mesmo registrado, favor atualizá-lo.'

    def update(self, atendimento):
        if atendimento.paciente.telefones:
            self.fields['fone'].initial = atendimento.paciente.telefones
        else:
            self.fields['fone'].initial = 'Fone'

    def save(self, atendimento):
        """
            Ainda preciso, antes de incluir o agendamento, verificar se já existe
            outro agendamento para o mesmo dia, mesmo paciente, mesmo tratamento.
            Essa verificação não está sendo feita ainda.
        """
        agenda_tratamento_acolhimento_in = self.cleaned_data['agenda_tratamento_acolhimento']
        agenda_tratamento_desobsessao_in = self.cleaned_data['agenda_tratamento_desobsessao']
        agenda_tratamento_af_in = self.cleaned_data['agenda_tratamento_af']
        fone_in = self.cleaned_data['fone']
        mensagens_list = []

        if agenda_tratamento_acolhimento_in != 'X':
            if agenda_tratamento_acolhimento_in != 'N':
                agenda_tratamento = AgendaTratamento.objects.get(id=agenda_tratamento_acolhimento_in)
            else:
                acolhimento = Tratamento.objects.get(id=10)
                agenda_tratamentos = AgendaTratamento.objects.filter(data=None, tratamento=acolhimento)
                if not agenda_tratamentos:
                    agenda_tratamento = AgendaTratamento(tratamento = acolhimento, data=None)
                    agenda_tratamento.save()
                else:
                    agenda_tratamento = agenda_tratamentos[0]
            dic_retorno = {}
            try:
                agenda_atendimento = AgendaAtendimento(paciente = atendimento.paciente, \
                    agenda_tratamento = agenda_tratamento, atendimento_origem = atendimento, status = 'A',\
                    data_criacao = atendimento.instancia_tratamento.data)
                obs = atendimento.observacao
                if not obs:
                    obs = ''
                novo_agendamento = unicode('[Novo agendamento: ' + \
                    agenda_atendimento.agenda_tratamento.tratamento.descricao_basica + ']')
                atendimento.observacao = obs + novo_agendamento
                atendimento.save()
                agenda_atendimento.save()
                dic_retorno = {'sucesso':True, 'mensagem':'Agendamento do Acolhimento realizado com sucesso. '}
            except:
                dic_retorno = {'sucesso':False, 'mensagem':'Erro: Agendamento do Acolhimento nao realizado. '}
                traceback.print_exc()

            mensagens_list.append(dic_retorno)

            if fone_in != 'Fone' and fone_in != atendimento.paciente.telefones:
                atendimento.paciente.telefones = fone_in
                try:
                    atendimento.paciente.save()
                    dic_retorno = {'sucesso':True, 'mensagem':'Telefone atualizado com sucesso. '}
                except:
                    dic_retorno = {'sucesso':False, 'mensagem':'Erro na atualização do telefone. '}
                mensagens_list.append(dic_retorno)

        if agenda_tratamento_desobsessao_in != 'X':
            if agenda_tratamento_desobsessao_in != 'N':
                agenda_tratamento = AgendaTratamento.objects.get(id=agenda_tratamento_desobsessao_in)
            else:
                desob = Tratamento.objects.get(id=8)
                agenda_tratamentos = AgendaTratamento.objects.filter(data=None, tratamento=desob)
                if not agenda_tratamentos:
                    agenda_tratamento = AgendaTratamento(tratamento = desob, data=None)
                    agenda_tratamento.save()
                else:
                    agenda_tratamento = agenda_tratamentos[0]
            dic_retorno = {}
            try:
                agenda_atendimento = AgendaAtendimento(paciente = atendimento.paciente, \
                    agenda_tratamento = agenda_tratamento, atendimento_origem = atendimento, status = 'A', \
                    data_criacao = atendimento.instancia_tratamento.data)
                agenda_atendimento.save()
                obs = atendimento.observacao
                if not obs:
                    obs = ''
                novo_agendamento = unicode('[Novo agendamento: ' + \
                    agenda_atendimento.agenda_tratamento.tratamento.descricao_basica + ']')
                atendimento.observacao = obs + novo_agendamento
                atendimento.save()
                dic_retorno = {'sucesso':True, 'mensagem':'Agendamento da Desobsessao realizado com sucesso. '}
            except:
                dic_retorno = {'sucesso':False, 'mensagem':'Erro: Agendamento da Desobsessao nao realizado. '}
                traceback.print_exc()

            mensagens_list.append(dic_retorno)

        if agenda_tratamento_af_in != 'X':
            if agenda_tratamento_af_in != 'N':
                agenda_tratamento = AgendaTratamento.objects.get(id=agenda_tratamento_af_in)
            else:
                af = Tratamento.objects.get(id=9)
                agenda_tratamentos = AgendaTratamento.objects.filter(data=None, tratamento=af)
                if not agenda_tratamentos:
                    agenda_tratamento = AgendaTratamento(tratamento = af, data=None)
                    agenda_tratamento.save()
                else:
                    agenda_tratamento = agenda_tratamentos[0]
            dic_retorno = {}
            try:
                agenda_atendimento = AgendaAtendimento(paciente = atendimento.paciente, \
                    agenda_tratamento = agenda_tratamento, atendimento_origem = atendimento, status = 'A', \
                    data_criacao = atendimento.instancia_tratamento.data)
                agenda_atendimento.save()
                obs = atendimento.observacao
                if not obs:
                    obs = ''
                novo_agendamento = unicode('[Novo agendamento: ' + \
                    agenda_atendimento.agenda_tratamento.tratamento.descricao_basica + ']')
                atendimento.observacao = obs + novo_agendamento
                atendimento.save()
                dic_retorno = {'sucesso':True, 'mensagem':'Agendamento do Atendimento Fraterno realizado com sucesso. '}
            except:
                dic_retorno = {'sucesso':False, 'mensagem':'Erro: Agendamento da Atendimento Fraterno nao realizado. '}
                traceback.print_exc()

            mensagens_list.append(dic_retorno)

        return mensagens_list

class NotificacaoForm(forms.Form):
    descricao                       = forms.CharField(max_length=200, required=False, widget=forms.TextInput( \
        attrs={'size':'40'}))
    impressao                  = forms.BooleanField(required=False)
    tela_checkin                    = forms.BooleanField(required=False)
    fixo                            = forms.BooleanField(required=False)
    data_validade                   = forms.DateField(required=False, widget=forms.TextInput(attrs={'size':'8'}))
    prazo_num                       = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'4'}))
    prazo_unidade                   = forms.ChoiceField(choices=Notificacao.UNIDADE, required=False)
    qtd_atendimentos                = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size':'4'}))

    def __init__(self, *args, **kwargs):
        super(NotificacaoForm, self).__init__(*args, **kwargs)

    def update(self, atendimento):
        pass

    def save(self, atendimento):
        descricao_in = self.cleaned_data['descricao']
        impressao_in = self.cleaned_data['impressao']
        tela_checkin_in = self.cleaned_data['tela_checkin']
        fixo_in = self.cleaned_data['fixo']
        data_validade_in = self.cleaned_data['data_validade']
        prazo_num_in = self.cleaned_data['prazo_num']
        prazo_unidade_in = self.cleaned_data['prazo_unidade']
        qtd_atendimentos_in = self.cleaned_data['qtd_atendimentos']

        mensagens_list = []

        if descricao_in:
            try:
                notificacao = Notificacao(descricao=descricao_in, impressao=impressao_in, tela_checkin=tela_checkin_in,\
                    ativo=True, data_criacao = datetime.date.today(), paciente = atendimento.paciente, \
                    atendimento = atendimento)
                if fixo_in:
                    notificacao.fixo = True
                elif data_validade_in:
                    notificacao.data_validade = data_validade_in
                elif prazo_num_in:
                    notificacao.prazo_num = prazo_num_in
                    notificacao.prazo_unidade = prazo_unidade_in
                elif qtd_atendimentos_in:
                    notificacao.qtd_atendimentos = qtd_atendimentos_in
                notificacao.save()
                obs = atendimento.observacao
                if not obs:
                    obs = ''
                nova_notificacao = smart_unicode('[Nova notificação: ') + smart_unicode(notificacao.descricao) + \
                    smart_unicode(']')
                atendimento.observacao = obs + nova_notificacao
                atendimento.save()
                dic_retorno = {'sucesso':True, 'mensagem':'Notificação cadastrada com sucesso.'}
            except:
                dic_retorno = {'sucesso':False, 'mensagem':'Erro no cadastro da notificação.'}
                traceback.print_exc()
            mensagens_list.append(dic_retorno)
        return mensagens_list

class NotificacaoForm2(forms.ModelForm):
    class Meta:
        model = Notificacao
        fields = ('descricao','ativo','impressao','tela_checkin','fixo',\
            'data_validade','prazo_num','prazo_unidade','qtd_atendimentos','paciente')

    def __init__(self, *args, **kwargs):
        try:
            pacienteid = kwargs.pop('pacienteid')
        except:
            pacienteid = -1
        super(NotificacaoForm2, self).__init__(*args, **kwargs)
        if pacienteid != -1:
            self.fields['paciente'].initial = Paciente.objects.get(id=pacienteid)
#        self.fields['paciente'].widget.attrs['readonly'] = True
#        self.fields['paciente'].widget.attrs['disabled'] = 'disabled'
        self.fields['data_validade'].widget.attrs['size'] = 8
        self.fields['prazo_num'].widget.attrs['size'] = 4
        self.fields['qtd_atendimentos'].widget.attrs['size'] = 4
        self.fields['descricao'].widget.attrs['size'] = 40
        self.fields['descricao'].max_length = 200
        self.fields['ativo'].initial = True

    def save(self):
        notificacao = forms.ModelForm.save(self)
        if not notificacao.data_criacao:
            notificacao.data_criacao = datetime.date.today()
            notificacao.save()
        return notificacao


def ajax_atualizar_paciente_confirmacao(request, atendimento_id):
    atendimento = get_object_or_404(Atendimento, pk=atendimento_id)

    debug = ''
    if request.method == 'POST':
        atualizar_paciente_form = AtualizarPaciente_ConfirmacaoForm(request.POST)
        agendamento_form = AgendamentoForm(request.POST)
        notificacao_form = NotificacaoForm(request.POST)
        mensagens = []
        
        if atualizar_paciente_form.is_valid():
            (paciente, mensagens_list) = atualizar_paciente_form.save(atendimento)
            mensagens = mensagens + mensagens_list
        else:
            mensagens.append({'sucesso':False, 'mensagem':'Erro nos dados gerais. Verificar dados inseridos.'})
        if agendamento_form.is_valid():
            mensagens_list = agendamento_form.save(atendimento)
            mensagens = mensagens + mensagens_list
        else:
            mensagens.append({'sucesso':False, 'mensagem':'Erro no agendamento. Verificar dados inseridos.'})
        if notificacao_form.is_valid():
            mensagens_list = notificacao_form.save(atendimento)
            mensagens = mensagens + mensagens_list
        else:
            mensagens.append({'sucesso':False, 'mensagem':'Erro na notificação. Verificar dados inseridos.'})

        if len(mensagens) == 0:
            mensagens.append({'sucesso':False, 'mensagem':'Nenhuma atualização realizada. Confirmar dados.'})

        return render_to_response('ajax-atualizar-paciente-confirmacao-resultado.html', {'paciente':paciente, \
                    'mensagens':mensagens})
    else:
        try:
            atualizar_paciente_form = AtualizarPaciente_ConfirmacaoForm()
            agendamento_form = AgendamentoForm()
            agendamento_form.update(atendimento)
            notificacao_form = NotificacaoForm()
        except:
            traceback.print_exc()

    return render_to_response('ajax-atualizar-paciente-confirmacao.html', {'atendimento':atendimento, \
        'form':atualizar_paciente_form, 'agendamento_form': agendamento_form, 'notificacao_form':notificacao_form})

def incluir_notificacao(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    mensagem_sucesso = ''
    mensagem_erro = ''

    if request.method == "POST":
        form_notificacao = NotificacaoForm2(request.POST)
        if form_notificacao.is_valid():
            try:
                form_notificacao.save()
                mensagem_sucesso = "Notificação incluída com sucesso."
            except:
                mensagem_erro = "Houve um erro ao atualizar a notificação"
                traceback.print_exc()
        else:
            print str(form_notificacao.errors)
            traceback.print_exc()
            mensagem_erro = "Notificação não incluída. Favor verificar os campos."
    else:
        form_notificacao = NotificacaoForm2(pacienteid = paciente.id)

    return render_to_response('crud-notificacao.html',
        {'paciente':paciente, \
        'form_notificacao':form_notificacao,\
        'mensagem_sucesso':mensagem_sucesso, \
        'mensagem_erro':mensagem_erro, \
        'titulo':'INCLUIR NOTIFICAÇÃO'})

def atualizar_notificacao(request, notificacao_id):
    notificacao = Notificacao.objects.get(pk=notificacao_id)

    mensagem_sucesso = ''
    mensagem_erro = ''

    if request.method == "POST":
        form_notificacao = NotificacaoForm2(request.POST, instance=notificacao, pacienteid = notificacao.paciente.id)
        if form_notificacao.is_valid():
            try:
                form_notificacao.save()
                mensagem_sucesso = "Notificação atualizada com sucesso."
            except:
                mensagem_erro = "Houve um erro ao atualizar a notificação"
        else:
            mensagem_erro = "Atualização não efetuada. Favor verificar os campos."
    else:
        form_notificacao = NotificacaoForm2(instance=notificacao, pacienteid = notificacao.paciente.id)

    return render_to_response('crud-notificacao.html', \
        {'paciente':notificacao.paciente,\
        'form_notificacao':form_notificacao,
        'notificacao':notificacao, \
        'mensagem_sucesso':mensagem_sucesso, \
        'mensagem_erro':mensagem_erro, \
        'titulo': 'ATUALIZAR NOTIFICAÇÃO', \
        })


class AgendaAtendimentoForm2(forms.ModelForm):
    fone = forms.CharField(required=False)
    class Meta:
        model = AgendaAtendimento
        fields = ('agenda_tratamento','paciente','status')

    def __init__(self, *args, **kwargs):
        try:
            # no caso de estar atualizando uma agenda_atendimento já existente
            agenda_atendimento_id = kwargs.pop('agenda_atendimento_id')
        except:
            agenda_atendimento_id = -1
        try:
            # no caso de estar criando uma nova agenda_atendimento.
            pacienteid = kwargs.pop('pacienteid')
        except:
            pacienteid = -1
        super(AgendaAtendimentoForm2, self).__init__(*args, **kwargs)
        self.fields['agenda_tratamento'].widget.attrs['id']='agenda'
        self.fields['agenda_tratamento'].widget.attrs['onchange']='show_hide_fone()'
        self.fields['agenda_tratamento'].widget.attrs['onload']='show_hide_fone()'
        self.fields['fone'].widget.attrs['id']='fone_field'
        self.fields['fone'].widget.attrs['title']='Atualizar esse campo implica na atualização do telefone da ficha do paciente.'
        # Criando nova agenda_atendimento
        if agenda_atendimento_id == -1:
            if pacienteid != -1:
                paciente = Paciente.objects.get(id=pacienteid)
                self.fields['paciente'].initial = paciente
                self.fields['fone'].initial = paciente.telefones
            # somente agendas_tratamento com datas no futuro serão exibidas.
            self.fields['agenda_tratamento'].queryset = AgendaTratamento.objects.filter(Q(data__gte=datetime.date.today()) \
                | Q(data=None)).order_by("tratamento__descricao_basica")
        # atualizando agenda_atendimento já existente.
        else:
            at = AgendaAtendimento.objects.get(id=agenda_atendimento_id)
            self.fields['paciente'].initial = at.paciente
            self.fields['agenda_tratamento'].initial = at.agenda_tratamento
            self.fields['status'].initial = at.status
            self.fields['fone'].initial = at.paciente.telefones

    def save(self, agenda_atendimento=None):
        dic = {}
        paciente = self.cleaned_data['paciente']
        agenda_tratamento = self.cleaned_data['agenda_tratamento']

        # significa que está criando um novo agenda_atendimento
        if not agenda_atendimento:
            aas = AgendaAtendimento.objects.filter(paciente = paciente, agenda_tratamento = agenda_tratamento)
            # verifica se já não há algum agendamento para o paciente.
            if len(aas) == 0:
                agenda_atendimento = forms.ModelForm.save(self)
                agenda_atendimento.status = 'A'
                agenda_atendimento.data_criacao = datetime.date.today()
                agenda_atendimento.save()
                paciente = agenda_atendimento.paciente
                paciente.telefones = self.cleaned_data['fone']
                paciente.save()
                dic['sucesso']=True
                dic['mensagem']='Agendamento realizado com sucesso.'

            else:
                dic['sucesso']=False
                dic['mensagem']='Agendamento já existente.'

        # significa que está atualizando uma agenda_atendimento existente.
        else:
            agenda_atendimento.agenda_tratamento = agenda_tratamento
            agenda_atendimento.status = self.cleaned_data['status']
            agenda_atendimento.save()
            paciente = agenda_atendimento.paciente
            paciente.telefones = self.cleaned_data['fone']
            paciente.save()
            dic['sucesso']=True
            dic['mensagem']='Agendamento atualizado com sucesso.'

        return dic


def realizar_agendamento(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    mensagem_sucesso = ''
    mensagem_erro = ''

    if request.method == "POST":
        form_agendamento = AgendaAtendimentoForm2(request.POST)
        if form_agendamento.is_valid():
            try:
                dic = form_agendamento.save()
                if dic['sucesso'] == True:
                    mensagem_sucesso = dic['mensagem']
                else:
                    mensagem_erro = dic['mensagem']
            except:
                mensagem_erro = "Erro no agendamento."
                traceback.print_exc()
        else:
            traceback.print_exc()
            mensagem_erro = "Erro no agendamento. Verificar campos."
    else:
        form_agendamento = AgendaAtendimentoForm2(pacienteid = paciente.id)

    return render_to_response('realizar-agendamento.html',
        {'paciente':paciente, \
        'form_agendamento':form_agendamento,\
        'mensagem_sucesso':mensagem_sucesso, \
        'mensagem_erro':mensagem_erro, \
        'titulo':'REALIZAR AGENDAMENTO'})

def atualizar_agendamento(request, agenda_atendimento_id):
    """
        É importante deixar registrado que essa atualização está levando em conta
        a existência de um atendimento realizado que deveria estar relacionado a um agendamento que foi fechado.
        Da forma como está, podemos ter algumas pequenas inconsistências, como:
        - Um agendamento marcado como fechado, mas que não está ligado a nenhum agenda_atendimento.
        Por enquanto não é muito grave.
    """
    agenda_atendimento = get_object_or_404(AgendaAtendimento, pk=agenda_atendimento_id)
    mensagem_sucesso = ''
    mensagem_erro = ''

    if request.method == "POST":
        form_agendamento = AgendaAtendimentoForm2(request.POST)
        if form_agendamento.is_valid():
            try:
                dic = form_agendamento.save(agenda_atendimento)
                if dic['sucesso'] == True:
                    mensagem_sucesso = dic['mensagem']
                else:
                    mensagem_erro = dic['mensagem']
            except:
                mensagem_erro = "Erro no agendamento."
                traceback.print_exc()
        else:
            traceback.print_exc()
            mensagem_erro = "Erro no agendamento. Verificar campos."
    else:
        form_agendamento = AgendaAtendimentoForm2(agenda_atendimento_id = agenda_atendimento_id)

    return render_to_response('atualizar-agendamento.html',
        {'agenda_atendimento':agenda_atendimento, \
        'form_agendamento':form_agendamento,\
        'mensagem_sucesso':mensagem_sucesso, \
        'mensagem_erro':mensagem_erro, \
        'titulo':'ATUALIZAR AGENDAMENTO'})

