
# coding: utf-8

from    datetime                        import date, datetime, timedelta

def get_data_limite():
    """
        Essa função precisa ser atualizada anualmente, pois só saberemos o período do recesso ao final de cada ano.
        Outra opção é criar um arquivo ou um registro na base com esses dados para não precisar mais atualizar o código.
    """
    data_base = datetime.today().date()
    NUMERO_DIAS = 90
    inicio_recesso = datetime(2014,12,12).date()
    final_recesso = datetime(2015,02,05).date()
    diferenca_depois = data_base - final_recesso
    if diferenca_depois.days > NUMERO_DIAS:
        return data_base - timedelta(days=NUMERO_DIAS)
    else:
        return inicio_recesso - timedelta(days=NUMERO_DIAS-diferenca_depois.days)


