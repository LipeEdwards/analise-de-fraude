import pandas as pd


DF = pd.read_csv('transacoes.csv')

#
print(DF.head())
print(DF.info())
print(DF.describe())

DF = DF.dropna(subset=['valor', 'id_cliente'])  # remove linhas sem dados essenciais
DF['data'] = pd.to_datetime(DF['data'], errors='coerce')  # converte coluna de data

media_por_cliente = DF.groupby('id_cliente')['valor'].transform('mean')
desvio_por_cliente = DF.groupby('id_cliente')['valor'].transform('std')

DF['limite_superior'] = media_por_cliente + 3 * desvio_por_cliente
DF['fraude_valor_alto'] = DF['valor'] > DF['limite_superior']


DF = DF.sort_values(['id_cliente', 'data'])
DF['tempo_desde_ultima'] = DF.groupby('id_cliente')['data'].diff().dt.total_seconds()
DF['fraude_velocidade'] = DF['tempo_desde_ultima'] < 60  # menos de 60s entre transações

DF['hora'] = DF['data'].dt.hour
DF['fraude_horario'] = DF['hora'].between(0, 5)


LIMITE_FIXO = 10000
DF['fraude_valor_fixo'] = DF['valor'] > LIMITE_FIXO

colunas_fraude = ['fraude_valor_alto', 'fraude_velocidade', 'fraude_horario', 'fraude_valor_fixo']
DF['score_fraude'] = DF[colunas_fraude].sum(axis=1)


DF['suspeita_de_fraude'] = DF['score_fraude'] >= 2

suspeitas = DF[DF['suspeita_de_fraude']]
print(f"\nTotal de transações: {len(DF)}")
print(f"Transações suspeitas: {len(suspeitas)}")
print(suspeitas[['id_cliente', 'valor', 'data', 'score_fraude']])


DF.to_csv('transacoes_analisadas.csv', index=False)