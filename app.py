import streamlit as st 
import pandas as pd
import os
import calendar
from datetime import timedelta, date
from auth import mostrar_login, mostrar_esqueci_senha, mostrar_cadastro, mostrar_redefinir_senha
from supabase import create_client

SUPABASE_URL = st.secrets ["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

query_params = st.query_params

if "type" in query_params and query_params["type"] == "recovery":
    st.session_state.pagina = "redefinir_senha"

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
       supabase = get_supabase()
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
        
        st.markdown("Filtro de períodos")

        tipo_filtro = st.radio(
            "Visualizar por:",
            ["Dia", "Semana", "Mês"],
            horizontal=True
        )

        if tipo_filtro == "Dia":
            data_inicio = st.date_input("Escolha o dia")
            data_fim = data_inicio

        elif tipo_filtro == "Semana":
            data_ref = st.date_input("Escolha uma data da semana")

            data_inicio = data_ref - timedelta(days=data_ref.weekday())
            data_fim = data_inicio + timedelta(days=6)

            st.caption(
                f"Semana: {data_inicio.strftime('%d/%m/%y')}"
                f"até {data_fim.strftime('%d/%m/%y')}"
            )

        else:
            col1, col2 = st.columns(2)

            with col1:
                mes = st.selectbox(
                    "Mês",
                    list(range(1, 13)),
                    format_func=lambda x: calendar.month_name[x]
                )

            with col2:
                ano = st.selectbox(
                    "Ano",
                    list(range(2026, 2040))
                )

            ultimo_dia = calendar.monthrange(ano, mes)[1]

            data_inicio = date(ano, mes, 1)
            data_fim = date(ano, mes, ultimo_dia)

            

        ganhos = supabase.table("ganhos") \
            .select("*") \
            .eq("user_id", st.session_state.user_id) \
            .gte("data_lancamento", data_inicio.isoformat()) \
            .lte("data_lancamento", data_fim.isoformat()) \
            .execute().data
        
        despesas = supabase.table("despesas") \
            .select("*") \
            .eq("user_id", st.session_state.user_id) \
            .gte("data_lancamento", data_inicio.isoformat()) \
            .lte("data_lancamento", data_fim.isoformat()) \
            .execute().data
        
        
        total_ganhos = sum(item["valor"] for item in ganhos)
        total_despesas = sum(item["valor"] for item in despesas)

        st.divider()

        col1, col2, col3 = st.columns(3)


        col1.metric("Total de ganhos", f"R$ {total_ganhos:.2f}")
        col2.metric("Total de despesas", f"R$ {total_despesas:.2f}")
        col3.metric("Saldo", f"R$ {(total_ganhos - total_despesas):.2f}")

        st.divider()
        st.subheader("Relatório detalhado")

        col_g, col_d = st.columns(2)

        with col_g:
            st.markdown("Ganhos")

            if not ganhos:
                st.info("Nenhum ganho registrado nesse período.")

            else:
                df_ganhos = pd.DataFrame(ganhos)

                df_ganhos = df_ganhos[[
                    "data_lancamento",
                    "descricao",
                    "valor"
                ]]

                df_ganhos["data_lancamento"] = pd.to_datetime(
                    df_ganhos["data_lancamento"]
                ).dt.strftime("%d/%m/%y")

                df_ganhos["valor"] = df_ganhos["valor"].map(
                    lambda x: f"R$ {x:,.2f}"
                )

                df_ganhos.columns = ["Data", "Descrição", "Valor"]

                st.dataframe(
                    df_ganhos,
                    use_container_width=True,
                    hide_index=True
                )
        
        with col_d:
            st.markdown("Despesas")

            if not despesas:
                st.info("Nenhuma despesa registrada nesse período.")

            else:
                df_despesas = pd.DataFrame(despesas)

                df_despesas = df_despesas[[
                    "data_lancamento",
                    "descricao",
                    "valor"
                ]]

                df_despesas["data_lancamento"] = pd.to_datetime(
                    df_despesas["data_lancamento"]
                ).dt.strftime("%d/%m/%y")

                df_despesas["valor"] = df_despesas["valor"].map(
                    lambda x: f"R$ {x:,.2f}"
                )

                df_despesas.columns = ["Data", "Descrição", "Valor"]

                st.dataframe(
                    df_despesas,
                    use_container_width=True,
                    hide_index=True
                )

if not st.session_state.logado:
    if st.session_state.pagina == "login":
        mostrar_login()

    elif st.session_state.pagina == "cadastro":
        mostrar_cadastro()

    elif st.session_state.pagina == "esqueci":
        mostrar_esqueci_senha()

    elif st.session_state.pagina == "esqueci_senha":
        mostrar_esqueci_senha()

    elif st.session_state.pagina == "redefinir_senha":
        mostrar_redefinir_senha()
    
    st.stop()

mostrar_app()