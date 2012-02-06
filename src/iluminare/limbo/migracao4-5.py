lista_status = ['C','A', 'E', 'D', 'T', '',' ']
lista_status_len = []
for s in lista_status:
    lista = TratamentoPaciente.objects.filter(status=s)
    v = (s, len(lista))
    lista_status_len.append(v)

lista_status_len
    

lista_salas = [t.descricao_basica for t in Tratamento.objects.all()]
lista_salas_len = []
for s in lista_salas:
    lista = TratamentoPaciente.objects.filter(tratamento__descricao_basica=s)
    v = (s, len(lista))
    lista_salas_len.append(v)

lista_salas_len




s4a = TratamentoPaciente.objects.filter(tratamento__descricao_basica='Sala 4', status='A')
s5a = TratamentoPaciente.objects.filter(tratamento__descricao_basica='Sala 5', status='A')
lista_geral = []
for tp in s4a:
    tp.status = 'C'
    tp.data_fim = datetime.date(2012,02,01)
    t = Tratamento.objects.get(descricao_basica = 'Sala 5')
    tp_novo = TratamentoPaciente(paciente = tp.paciente, tratamento = t, data_inicio = datetime.date(2012,02,01), status = 'A')
    lista_geral.append(tp)
    lista_geral.append(tp_novo)
    
for tp in s5a:
    tp.status = 'C'
    tp.data_fim = datetime.date(2012,02,01)
    t = Tratamento.objects.get(descricao_basica = 'Sala 4')
    tp_novo = TratamentoPaciente(paciente = tp.paciente, tratamento = t, data_inicio = datetime.date(2012,02,01), status = 'A')
    lista_geral.append(tp)
    lista_geral.append(tp_novo)

for tp in lista_geral:
    tp.save()
