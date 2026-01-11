import pandas as pd
import streamlit as st
import os 
import hashlib

SALT = st.secrets["SALT"]
USERS_FILE = "users.csv"

def hash_senha(senha):
    return hashlib.sha256((senha + SALT).encode()).hexdigest()

def carregar_usuarios():
    if not os.path.exists(USERS_FILE):
       df = pd.DataFrame(columns=["nome", "email", "senha"])
       df.to_csv(USERS_FILE, index=False)
    return pd.read_csv(USERS_FILE)
        

def autenticar(email, senha):
    df = carregar_usuarios()
    senha_hash = hash_senha(senha)

    usuario = df[(df["email"] == email) & (df["senha"] == senha_hash)]
    
    if not usuario.empty:
        return usuario.iloc[0]["nome"]
    
    return None

def cadastrar_usuario(nome, email, senha):
    df = carregar_usuarios()

    if email in df["email"].values:
        return False
    
    novo = pd.DataFrame(
        [[nome, email, hash_senha(senha)]],
        columns=["nome", "email", "senha"]
    )

    df = pd.concat([df, novo], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)
    return True



def mostrar_login():
    st.title("Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        nome = autenticar(email, senha)

        if nome: 
            st.session_state.logado = True
            st.session_state.usuario = email
            st.session_state.nome = nome
            st.session_state.pagina = "app"
            st.rerun()
        
        else:
            st.error("Email ou senha inválidos")

    st.button(
       "Criar conta",
       on_click=lambda: mudar_pagina("cadastro")
    )

    st.button(
        "Esqueci minha senha",
        on_click=lambda:mudar_pagina("esqueci")
    )


def mostrar_cadastro():
    st.title("Cadastro")

    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")

    if st.button("Cadastrar"):
        if senha != confirmar:
            st.error("As senhas devem ser idênticas!")
        
        elif cadastrar_usuario(nome, email, senha):
            st.success("Conta criada com sucesso!")
            mudar_pagina("login")
            st.rerun()
        else:
            st.error("Email ja cadastrado")
        
    st.button("Voltar", on_click=lambda: mudar_pagina("login"))



def mostrar_esqueci_senha():
    st.title("Recuperar senha")
    st.info("Funcionalidade em desenvolvimento")


    st.button("Voltar", on_click=lambda: mudar_pagina("login"))

def mudar_pagina(pagina):
    st.session_state.pagina = pagina
    