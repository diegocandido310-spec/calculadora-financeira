import streamlit as st
import os 
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

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
            st.session_state.user_id = user.id
            st.session_state.pagina = "app"
            st.session_state.access_token = response.session.access_token
            st.session_state.refresh_token = response.session.refresh_token
            st.rerun()
        except Exception:
            st.error("Email ou senha inválidos")

    st.button("Criar conta", on_click=lambda: mudar_pagina("cadastro"))
    st.button("Esqueci minha senha", on_click=lambda: mudar_pagina("esqueci_senha"))

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
            st.error(str(e))
        
    st.button("Voltar", on_click=lambda: mudar_pagina("login"))



def mostrar_esqueci_senha():
    st.title("Recuperar senha")
    
    email = st.text_input("Digite seu email")

    if st.button("Enviar link de recuperação"):
        if not email:
            st.warning("Informe seu email")
            return
        
        try:
            supabase.auth.reset_password_for_email(email)
            st.success("Enviamos um link de recuperação para seu email.")
            st.info("Verifique sua caixa de entradda ou spam.")
        except Exception as e:
            st.error("Erro ao enviar email de recuperação")
            st.error(str(e))
    
    st.button("Voltar", on_click=lambda: mudar_pagina("login"))


def mostrar_redefinir_senha():
    st.title("Definir nova senha")
    
    nova_senha = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar nova senha", type="password")

    if st.button("Atualizar senha"):
        if nova_senha != confirmar:
            st.error("As senhas devem ser idênticas")
            return
        
        try:
            supabase.auth.update_user({
                "password": nova_senha
            })

            st.success("Senha atualizada com sucesso!")
            st.info("Agora você já pode fazer login")
            mudar_pagina("login")
            st.rerun()

        except Exception as e:
            st.error("Erro ao atualizar senha")
            st.error(str(e))

def mudar_pagina(pagina):
    st.session_state.pagina = pagina
    