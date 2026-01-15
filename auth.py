import streamlit as st
import os 
from supabase import create_client

SUPABASE_URL = st.secrets("SUPABASE_URL")
SUPABASE_KEY = st.secrets("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def mostrar_login():
    st.title("Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": senha
            })

            user = response.user
            nome = user.user_metadata.get("nome", "Usuário")

            st.session_state.logado = True
            st.session_state.usuario = user.email
            st.session_state.nome = nome
            st.session_state.pagina = "app"
            st.rerun()

        except Exception:
            st.error("Email ou senha inválidos")

    st.button("Criar conta", on_click=lambda: mudar_pagina("cadastro"))


def mostrar_cadastro():
    st.title("Cadastro")

    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")

    if st.button("Cadastrar"):
        if senha != confirmar:
            st.error("As senhas devem ser idênticas!")
            return
        
        try:
            supabase.auth.sign_up({
                "email": email,
                "password": senha,
                "options":{
                    "data":{
                        "nome": nome
                    }
                }
            })

            st.success("Conta criada com sucesso!")
            mudar_pagina("login")
            st.rerun()

        except Exception as e:
            st.error("Erro ai criar conta")
        
    st.button("Voltar", on_click=lambda: mudar_pagina("login"))



def mostrar_esqueci_senha():
    st.title("Recuperar senha")
    st.info("Funcionalidade em desenvolvimento")

    st.button("Voltar", on_click=lambda: mudar_pagina("login"))

def mudar_pagina(pagina):
    st.session_state.pagina = pagina
    