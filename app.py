import streamlit as st 
import os
from auth import mostrar_login, mostrar_esqueci_senha, mostrar_cadastro
from supabase import create_client

SUPABASE_URL = st.secrets ["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

def get_supabase():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    if "access_token" in st.session_state:
        client.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )
    return client

def salvar_ganho(data, descricao, valor):
    supabase = get_supabase()
    user = supabase.auth.get_user()

    if user is None or user.user is None:
        st.error("Usuário não autenticado")
        return

    supabase.table("ganhos").insert({
        "user_id": user.user.id,
        "data_lancamento": data.isoformat(),
        "descricao": descricao,
        "valor": valor
    }).execute()

def salvar_despesa(data, descricao, valor):
    supabase = get_supabase()
    user = supabase.auth.get_user()

    if user is None or user.user is None:
        st.error("Usuario não autenticado")
        return

    supabase.table("despesas").insert({
        "user_id": user.user.id,
        "data_lancamento": data.isoformat(),
        "descricao": descricao,
        "valor": valor
    }).execute()

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
       supabase = get_supabase 
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

        data = st.date_input("Data", key="ganho_data")
        descricao = st.text_input("Descrição", key="ganho_descricao")
        valor = st.number_input("valor", min_value=0.0, format="%.2f", key="ganho_valor")

        if st.button("Salvar ganho"):
            if descricao.strip() == "" or valor <=0:
                st.warning("Preencha todos os campos corretamente")
            
            else:
                salvar_ganho(data, descricao, valor)
                st.success("Ganho registrado com sucesso!")
                

    with tab_despesa:
        st.subheader("Registrar Despesa")

        data = st.date_input("Data", key="despesa_data")
        descricao = st.text_input("Descrição", key="despesa_descricao")
        valor = st.number_input("valor", min_value=0.0, format="%.2f", key="despesa_valor")

        if st.button("Salvar despesa"):
            if descricao.strip() == "" or valor <=0:
                st.warning("Preencha todos os campos corretamente")
            
            else:
                salvar_despesa(data, descricao, valor)
                st.success("Despesa registrada com sucesso!")
       

    with tab_resumo:
        st.subheader("Resumo")

        supabase = get_supabase()
        user = supabase.auth.get_user()

        ganhos = (
            supabase
            .table("ganhos")
            .select("valor")
            .eq("user_id", user.user.id)
            .execute()
            .data
        )
        despesas =( 
            supabase
            .table("despesas")
            .select("*")
            .eq("user_id", user.user.id)
            .execute()
            .data
        )
        total_ganhos = sum(item["valor"] for item in ganhos)
        total_despesas = sum(item["valor"] for item in despesas)

        st.metric("Total de ganhos", f"R$ {total_ganhos:.2f}")
        st.metric("Total de despesas", f"R$ {total_despesas:.2f}")
        st.metric("Saldo", f"R$ {(total_ganhos - total_despesas):.2f}")

if not st.session_state.logado:
    if st.session_state.pagina == "login":
        mostrar_login()

    elif st.session_state.pagina == "cadastro":
        mostrar_cadastro()

    elif st.session_state.pagina == "esqueci":
        mostrar_esqueci_senha()
    
    st.stop()

mostrar_app()