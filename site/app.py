from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
LAST_FILE = os.path.join(UPLOAD_FOLDER, 'last_uploaded.xlsx')

def process_excel(path):
    df = pd.read_excel(path, "grdDemSaldo", skiprows=1, names=[
        "Cód. Estruturado", "Cód. Alternativo 1", "Cód. Insumo", "Descrição", "Unid.",
        "Quant Saldo", "Valor Saldo", "Quant Previsto", "Valor Previsto",
        "Quant Solicitação", "Valor Solicitação", "Quant Pedido", "Valor Pedido",
        "Quant Contrato", "Valor Contrato", "Quant Estoque Reservado", "Valor Estoque Reservado",
        "Quant Realizado", "Valor Realizado", "Cód. Alternativo 2", "Descrição Serviço 2º Nível"])

    def calcula_valor_unitario(valor, quantidade):
        return np.where(quantidade.isnull(), valor, valor / quantidade)

    df['Valor unit Saldo'] = calcula_valor_unitario(df['Valor Saldo'], df['Quant Saldo'])
    df['Valor unit Previsto'] = calcula_valor_unitario(df['Valor Previsto'], df['Quant Previsto'])

    condicoes = [
        df['Cód. Insumo'].isnull(),
        df['Quant Saldo'] < 0,
        df['Quant Saldo'].isnull() & (df['Valor unit Saldo'] < 0),
        df['Quant Saldo'].isnull() & (df['Valor unit Saldo'] >= 0),
        df['Valor unit Saldo'] < df['Valor unit Previsto'],
    ]
    valores = [2,0,0, 1, 0]
    default = 1
    df['sit orcamento'] = np.select(condicoes, valores, default=default)
  # Remove a coluna e salva em uma variável temporária
    unit_saldo = df['Valor unit Saldo']
    df = df.drop(columns=['Valor unit Saldo'])

    # Insere a coluna na posição desejada (índice 7)
    df.insert(7, 'Valor unit Saldo', unit_saldo)

    unit_saldo = df['Valor unit Previsto']
    df = df.drop(columns=['Valor unit Previsto'])

    # Insere a coluna na posição desejada (índice 7)
    df.insert(10, 'Valor unit Previsto', unit_saldo)
    df = df.drop(columns = ["Cód. Alternativo 1",  "Cód. Alternativo 2", "Descrição Serviço 2º Nível"])

    soma = df.loc[df.index[-1],[
        'Valor Saldo',  'Valor Previsto',
        'Valor Solicitação', 'Valor Pedido',
        'Valor Contrato', 'Valor Estoque Reservado',
        'Valor Realizado'
    ]]

    return df, soma
@app.route('/', methods = ['GET', 'POST'])
def index():
    df = None
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, 'last_uploaded.xlsx')
            file.save(filepath)
            return redirect('/')
        
    if os.path.exists(LAST_FILE):
        df, soma = process_excel(LAST_FILE)
        df = df.fillna('')
        soma_dict = soma.to_dict()
        table_data = df.to_dict(orient='records')
        columns = df.columns.tolist()
    else:
        table_data=[]
        columns = []
    return render_template('index.html', table_data=table_data, columns= columns, totais = soma_dict)
if __name__ == '__main__':
    app.run(debug=True)
