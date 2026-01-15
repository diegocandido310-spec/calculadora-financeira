import streamlit as st 
import pandas as pd
import os
from auth import mostrar_login, mostrar_esqueci_senha, mostrar_cadastro
from supabase import create_client

SUPABASE_URL = st.secrets ["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DATA_DIR = "data"

if "ganho_salvo" not in st.session_state:
    st.session_state.ganho_salvo = False

if "despesa_salva" not in st.session_state:
    st.session_state.despesa_salva = False



if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def normalizar_email(email):
    return email.replace("@", "_").replace(".", "_")

def ganhos_file_usuario():
    email = normalizar_email(st.session_state.usuario)
    return f"{DATA_DIR}/{email}_ganhos.csv"

def despesas_file_usuario():
    email = normalizar_email(st.session_state.usuario)
    return f"{DATA_DIR}/{email}_despesas.csv"

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


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


    GANHOS_FILE = ganhos_file_usuario()
    DESPESAS_FILE = despesas_file_usuario()

    if not os.path.exists(GANHOS_FILE):
        pd.DataFrame(columns=["data", "valor", "descricao"]).to_csv(GANHOS_FILE, index=False)

    if not os.path.exists(DESPESAS_FILE):
        pd.DataFrame(columns=["data", "valor", "tipo"]).to_csv(DESPESAS_FILE, index=False)


    def carregar_dados():
        ganhos = pd.read_csv(GANHOS_FILE, parse_dates=["data"])
        despesas = pd.read_csv(DESPESAS_FILE, parse_dates=["data"])
        return ganhos, despesas

    ganhos, despesas = carregar_dados()

    total_ganhos = ganhos["valor"].sum()
    total_despesas = despesas["valor"].sum()
    saldo = total_ganhos - total_despesas
   

    ganhos["data"] = pd.to_datetime(ganhos["data"])
    despesas["data"] = pd.to_datetime(despesas["data"])

    if ganhos.empty and despesas.empty:
        ultimo_mes = None
    
    datas = []

    
    if not ganhos.empty:
        datas.append(ganhos["data"].max())
        
    if not despesas.empty:
        datas.append(despesas["data"].max())

    if datas:
        ultimo_mes = max(datas).to_period("M")

    else: 
        ultimo_mes = pd.Timestamp.today().to_period("M")
        
       

    if ultimo_mes is not None:
        ganhos_mes = ganhos[ganhos["data"].dt.to_period("M") == ultimo_mes]
        despesas_mes = despesas[despesas["data"].dt.to_period("M") == ultimo_mes]

        total_ganhos_mes = ganhos_mes["valor"].sum()
        total_despesas_mes = despesas_mes["valor"].sum()
        saldo_mes = total_ganhos_mes - total_despesas_mes

    else:
        total_ganhos_mes = 0
        total_despesas_mes = 0
        saldo_mes = 0


    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Ganhos", f"R$ {total_ganhos_mes:,.2f}")

    with col2: 
        st.metric("Despesas", f"R$ {total_despesas_mes:,.2f}")

    with col3: 
        st.metric("saldo", f"R$ {saldo_mes:,.2f}")

    if ganhos.empty and despesas.empty:
        total_ganhos_mes = total_despesas_mes = saldo_mes = 0

    tab_ganho, tab_despesa, tab_resumo = st.tabs([
        "Registrar Ganho",
        "Registrar Despesa",
        "Resumo"
    ])

    with tab_ganho:
        st.subheader("Registrar Ganho")

        with st.form("form_ganho"):
            data = st.date_input("Data")
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)

            submit = st.form_submit_button("Salvar")

            if submit:
                if descricao.strip() == "" or valor <= 0:
                    st.warning("Preencha todos os campos corretamente!")
                else:
                    novo = pd.DataFrame([[data, descricao, valor]],
                                columns=["data", "descricao", "valor"])
                
                    ganhos = pd.read_csv(GANHOS_FILE)
                    ganhos = pd.concat([ganhos, novo], ignore_index=True)
                    ganhos.to_csv(GANHOS_FILE, index=False)

                    st.session_state.ganho_salvo = True
                    st.session_state.despesa_salva = False
                    st.rerun()

            if st.session_state.ganho_salvo:
                st.success("Ganho registrado com sucesso!")
                

    with tab_despesa:
        st.subheader("Registrar Despesa")

        with st.form("form_despesa"):
            data = st.date_input("Data")
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)

            submit = st.form_submit_button("Salvar")

            if submit:
                if descricao.strip() == "" or valor <= 0:
                    st.warning("Preeencha todos os campos corretamente")
                else:
                    novo = pd.DataFrame([[data, descricao, valor]],
                                    columns=["data", "descricao", "valor"])
                
                    despesas = pd.read_csv(DESPESAS_FILE)
                    despesas = pd.concat([despesas, novo], ignore_index=True)
                    despesas.to_csv(DESPESAS_FILE, index = False)

                    st.session_state.ganho_salvo = False
                    st.session_state.despesa_salva = True
                    st.rerun()

            if st.session_state.despesa_salva:
                st.success("Despesa registrada com sucesso!")

    with tab_resumo:
        st.session_state.ganho_salvo = False
        st.session_state.despesa_salva = False
        st.subheader("Resumo financeiro")

        st.divider()

        st.subheader("Filtros")

        ganhos = pd.read_csv(GANHOS_FILE)
        despesas = pd.read_csv(DESPESAS_FILE)

        ganhos["data"] = pd.to_datetime(ganhos["data"])
        despesas["data"] = pd.to_datetime(despesas["data"])

        col1, col2, col3 = st.columns(3)

        with col1:
            periodo = st.selectbox(
                "Período",
                ["Dia", "Semana", "Mês"]
            )
    
        with col2:
            if periodo in ["Dia", "Semana"]:
                data_escolhida = st.date_input("Data")
            
            else:
                mes_escolhido = st.selectbox(
                    "Mês",
                    list(range(1,13))
                )
    
        with col3:
            ano_escolhido = st.number_input(
                "Ano",
                min_value= 2020,
                max_value=2100,
                value=pd.Timestamp.today().year
            )

        hoje = pd.Timestamp.today()

        if periodo == "Dia":
            ganhos_filtrado = ganhos[
                ganhos["data"].dt.date == data_escolhida
            ]

            despesas_filtrado = despesas[
                despesas["data"].dt.date == data_escolhida
            ]

        elif periodo == "Semana":
            data_base = pd.to_datetime(data_escolhida)
            inicio_semana = data_base - pd.Timedelta(days=data_base.weekday())
            fim_semana = inicio_semana + pd.Timedelta(days=6)

            ganhos_filtrado = ganhos[
                (ganhos["data"]>= inicio_semana)&
                (ganhos["data"]<= fim_semana)
            ]

            despesas_filtrado= despesas[
                (despesas["data"]>= inicio_semana)&
                (despesas["data"]<= fim_semana)
            ]

        else:
            ganhos_filtrado = ganhos[
                (ganhos["data"].dt.month == mes_escolhido)&
                (ganhos["data"].dt.year == ano_escolhido)
            ]

            despesas_filtrado = despesas[
                (despesas["data"].dt.month == mes_escolhido)&
                (despesas["data"].dt.year == ano_escolhido)
            ]
        
        total_ganhos = ganhos_filtrado["valor"].sum()
        total_despesas = despesas_filtrado["valor"].sum()
        lucro = total_ganhos - total_despesas

        st.metric("Total de ganhos", f"R$ {total_ganhos:,.2f}")
        st.metric("Total de despesas", f"R$ {total_despesas:,.2f}")
        st.metric("Saldo", f"R$ {lucro:,.2f}")

        st.divider()
        st.subheader("Relatório detalhado")

        col_g, col_d = st.columns(2)

        with col_g:
            st.markdown("Ganhos")

            if ganhos_filtrado.empty:
                st.info("Nenhum ganho registrado nesse período.")

            else:
                tabela_ganhos = ganhos_filtrado.sort_values("data").copy()
                tabela_ganhos["data"] = tabela_ganhos["data"].dt.strftime("%d/%m/%y")
                tabela_ganhos["valor"] = tabela_ganhos["valor"].map("R$ {:,.2f}".format)

                st.dataframe(
                    tabela_ganhos,
                    use_container_width=True,
                    hide_index=True
                )

        with col_d:
            st.markdown("Despesas")

            if despesas_filtrado.empty:
                st.info("Nenhuma despesa registrada nesse período.")

            else:
                tabela_despesas = despesas_filtrado.sort_values("data").copy()
                tabela_despesas["data"] = tabela_despesas["data"].dt.strftime("%d/%m/%y")
                tabela_despesas["valor"] = tabela_despesas["valor"].map("R$ {:,.2f}".format)

                st.dataframe(
                    tabela_despesas,
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
    
    st.stop()

mostrar_app()