# coding: utf-8

def detailed_search(pacientes):
    lista = []
    for paciente in pacientes:
        tratamentos = paciente.get_tratamentos()
        atendimento = paciente.get_last_atendimento()
        jtc = paciente.checked_in_today()
        is_voluntario = paciente.is_voluntario()

        dic = {
			'tratamentos': tratamentos or None,
			'paciente': paciente.nome,
            'atendimento': atendimento or None,
            'salas': None,
			'hoje': None,
			'jtc': jtc,
			'eh_vol': is_voluntario
        }

        lista.append(dic)
    return lista
