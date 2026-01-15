import streamlit as st 
import os
from auth import mostrar_login, mostrar_esqueci_senha, mostrar_cadastro
from supabase import create_client

SUPABASE_URL = st.secrets ["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


st.set_page_config(
    page_title= "Calculadora financeira",
    layout = "wide"
)

if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "nome" not in st.session_state:
    st.session_state.nome = None

def mostrar_app():
   

    st.sidebar.success(f"Olá, {st.session_state.nome}")

    if st.sidebar.button("Sair"):  
       supabase.auth.sign_out()
       st.session_state.clear()
       st.rerun()
    
    st.title("Calculadora Financeira")
    st.caption("Controle simples de ganhos e despesas")


    st.divider()

    

    tab_ganho, tab_despesa, tab_resumo = st.tabs([
        "Registrar Ganho",
        "Registrar Despesa",
        "Resumo"
    ])

    with tab_ganho:
        st.subheader("Registrar Ganho")

                

    with tab_despesa:
        st.subheader("Registrar despesa")
       

    with tab_resumo:
        st.subheader("resumo")


if not st.session_state.logado:
    if st.session_state.pagina == "login":
        mostrar_login()

    elif st.session_state.pagina == "cadastro":
        mostrar_cadastro()

    elif st.session_state.pagina == "esqueci":
        mostrar_esqueci_senha()
    
    st.stop()

mostrar_app()