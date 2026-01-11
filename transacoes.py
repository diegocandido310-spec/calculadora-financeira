import pandas as pd
import os
import streamlit as st

TRANSACOES_FILE = "transacoes.csv"

def carregar_transacoes():
    if not os.path.exists(TRANSACOES_FILE):
        df = pd.DataFrame(columns=[
            "usuario", "tipo", "valor", "descricao", "data"
        ])
        df.to_csv(TRANSACOES_FILE, index=False)
    return pd.read_csv(TRANSACOES_FILE)

def salvar_transacao(usuario, tipo, valor, descricao, data):
    df = carregar_transacoes()

    nova = pd.DataFrame([{
        "usuario": usuario,
        "tipo": tipo,
        "valor": valor,
        "descricao": descricao,
        "data": data
    }])

    df = pd.concat([df, nova], ignore_index=True)
    df.to_csv(TRANSACOES_FILE, index=False)

def transacoes_usuario(usuario):
    df = carregar_transacoes()
    return df[df["usuario"]== usuario]
    
df = transacoes_usuario(st.session_state)

ganhos = df[df["tipo"] == "ganho"]["valor"].sum
despesas = df[df["tipo"] == "despesa"]["valor"].sum
saldo = ganhos - despesas