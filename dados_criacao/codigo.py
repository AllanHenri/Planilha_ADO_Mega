import pandas as pd
import numpy as np

def calcula_valor_unitario(valor, quantidade):
    return np.where(quantidade.isnull(), valor, valor / quantidade)
names=[
    "Cód. Estruturado", "Cód. Alternativo 1", "Cód. Insumo", "Descrição", "Unid.",
    "Quantidade Saldo Solicitação", "Valor Saldo Solicitação", "Quantidade Previsto", "Valor Previsto",
    "Quantidade Solicitação", "Valor Solicitação", "Quantidade Pedido", "Valor Pedido",
    "Quantidade Contrato", "Valor Contrato", "Quantidade Estoque Reservado", "Valor Estoque Reservado",
    "Quantidade Realizado", "Valor Realizado", "Cód. Alternativo 2", "Descrição Serviço 2º Nível"
]

df = pd.read_excel('/home/suporte/Projeto_Orcamento_ADO/grdDemSaldo.xlsx', "grdDemSaldo", skiprows=1, names=names )

df['valor unit Saldo Solicitação'] = calcula_valor_unitario(df['Valor Saldo Solicitação'], df['Quantidade Saldo Solicitação'])
df['valor unit Previsto'] = calcula_valor_unitario(df['Valor Previsto'], df['Quantidade Previsto'])

condicoes = [
    df['Quantidade Saldo Solicitação'].isnull() & (df['valor unit Saldo Solicitação'] < 0),
    df['Quantidade Saldo Solicitação'].isnull() & (df['valor unit Saldo Solicitação'] >= 0),
    df['valor unit Saldo Solicitação'] < df['valor unit Previsto'],
]

# Remove a coluna e salva em uma variável temporária
unit_saldo = df['Valor unit Saldo']
df = df.drop(columns=['Valor unit Saldo'])

# Insere a coluna na posição desejada (índice 7)
df.insert(7, 'Valor unit Saldo', unit_saldo)
df = df.drop(columns = ["Cód. Alternativo 1",  "Cód. Alternativo 2", "Descrição Serviço 2º Nível"])

soma = df.loc[df.index[-1],[
    'Valor Saldo',  'Valor Previsto',
    'Valor Solicitação', 'Valor Pedido',
    'Valor Contrato', 'Valor Estoque Reservado',
    'Valor Realizado'
]]
