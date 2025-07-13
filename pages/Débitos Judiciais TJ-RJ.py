import streamlit as st
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import json
from streamlit_lottie import st_lottie
from streamlit_card import card
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

st.set_page_config(page_title="Cálculo de Débitos Judiciais", page_icon="⚖️", layout="wide")

# 🎯 VALORES MOCK PARA DEMONSTRAÇÃO
VALORES_MOCK = {
    "data_inicial": date(2020, 1, 15),
    "data_final": date(2024, 12, 31),
    "valor": 50000.00,
    "tipo_juros": "Juros Simples 12% a.a.",
    "data_juros": date(2020, 1, 15),
    "honorarios": 20.0,
    "aplicar_523": True
}

st.title("⚖️ Cálculo de Débitos Judiciais — Natureza Cível")

# Sidebar GLOBAL
with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/205710427?v=4", caption="Advogado que programa é unicórnio!",
             use_container_width=True)
    st.markdown("---")
    st.link_button("Visite meu novo site!", "https://pedrop.vercel.app/")
    st.markdown("---")
    st.header("Pedro Potz")
    st.markdown("Advogado Programador")

st.subheader("📝 Preencha os dados abaixo:")

# 🔸 Formulário COM VALORES PRÉ-PREENCHIDOS
with st.form("form_calculo"):
    col1, col2 = st.columns(2)
    with col1:
        data_inicial = st.date_input("Data Inicial*", value=VALORES_MOCK["data_inicial"], format="DD/MM/YYYY")
    with col2:
        data_final = st.date_input("Data Final*", value=VALORES_MOCK["data_final"], format="DD/MM/YYYY")

    valor = st.number_input("Valor Base*", value=VALORES_MOCK["valor"], min_value=0.0, step=0.01)

    tipo_juros = st.selectbox(
        "Tipo de Juros*",
        (
            "Sem juros (somente correção monetária)",
            "Juros Simples 6% a.a.",
            "Juros Simples 12% a.a.",
            "Juros do Código Civil (6% ou 12% a.a.)",
            "Taxa legal (Lei 14.905/24) — Em desenvolvimento"
        ),
        index=2
    )

    tipo_obrigacao = None
    if tipo_juros == "Juros do Código Civil (6% ou 12% a.a.)":
        tipo_obrigacao = st.radio(
            "Tipo da obrigação:",
            ("Contratual (12% a.a.)", "Extracontratual (6% a.a.)")
        )

    data_juros = st.date_input("Data Inicial de Incidência dos Juros*", value=VALORES_MOCK["data_juros"],
                               format="DD/MM/YYYY")

    honorarios = st.number_input("Honorários (%)", value=VALORES_MOCK["honorarios"], min_value=0.0, step=0.1)

    aplicar_523 = st.checkbox("Aplicar Art. 523 §1º CPC (10% Multa + 10% Honorários)",
                              value=VALORES_MOCK["aplicar_523"])

    submitted = st.form_submit_button("Calcular")


# 🔸 FUNÇÃO para gerar gráficos (usado tanto para mock quanto para cálculo real)
def gerar_graficos_e_metricas(valor, valor_juros, valor_corrigido, valor_honorarios, multa_523, honorarios_523, total,
                              meses, taxa_mensal, aplicar_523, is_mock=False):
    titulo = "📈 Demonstração - Análise Jurídico-Financeira" if is_mock else "📈 Análise Jurídico-Financeira Profissional"

    st.markdown("---")
    st.header(titulo)

    if is_mock:
        st.info(
            "👆 **Exemplo demonstrativo** - Altere os valores acima e clique em 'Calcular' para ver seu caso específico")

    # Criar dados para os gráficos
    componentes = []
    valores = []
    cores = []

    if valor > 0:
        componentes.append("Valor Base")
        valores.append(valor)
        cores.append("#1f77b4")
    if valor_juros > 0:
        componentes.append("Juros")
        valores.append(valor_juros)
        cores.append("#ff7f0e")
    if valor_honorarios > 0:
        componentes.append("Honorários")
        valores.append(valor_honorarios)
        cores.append("#2ca02c")
    if multa_523 > 0:
        componentes.append("Multa Art. 523")
        valores.append(multa_523)
        cores.append("#d62728")
    if honorarios_523 > 0:
        componentes.append("Hon. Art. 523")
        valores.append(honorarios_523)
        cores.append("#9467bd")

    # Layout em 3 colunas para os gráficos
    col1, col2, col3 = st.columns(3)

    with col1:
        if componentes:
            fig_pizza = px.pie(
                values=valores, names=componentes, title="Composição do Débito Judicial",
                color_discrete_sequence=cores, hole=0.4
            )
            fig_pizza.update_layout(height=400, showlegend=True, font=dict(size=10), title_font_size=14)
            st.plotly_chart(fig_pizza, use_container_width=True)

    with col2:
        if meses > 0 and taxa_mensal and taxa_mensal > 0:
            meses_lista = list(range(0, meses + 1))
            valores_evolucao = [valor * (1 + taxa_mensal * m) for m in meses_lista]

            fig_evolucao = go.Figure(go.Scatter(
                x=meses_lista, y=valores_evolucao, mode='lines+markers', name='Evolução do Débito',
                line=dict(color='#1f77b4', width=3), marker=dict(size=6)
            ))
            fig_evolucao.update_layout(
                title="Evolução Temporal do Débito", xaxis_title="Meses", yaxis_title="Valor (R$)",
                height=400, showlegend=False, font=dict(size=10), title_font_size=14
            )
            st.plotly_chart(fig_evolucao, use_container_width=True)
        else:
            st.info("Evolução temporal disponível apenas para cálculos com juros.")

    with col3:
        taxas_comparativas = {"Sem Juros": 0, "6% a.a.": 0.06, "12% a.a.": 0.12, "Selic (Est.)": 0.10}
        valores_comparativos = [valor * (1 + (taxa / 12 * meses)) for taxa in taxas_comparativas.values()]

        fig_comparativo = px.bar(
            x=list(taxas_comparativas.keys()), y=valores_comparativos, title="Comparativo de Taxas",
            color=valores_comparativos, color_continuous_scale="Blues"
        )
        fig_comparativo.update_layout(
            height=400, showlegend=False, font=dict(size=10), title_font_size=14,
            xaxis_title="Taxa de Juros", yaxis_title="Valor Total (R$)"
        )
        st.plotly_chart(fig_comparativo, use_container_width=True)

    st.markdown("---")
    st.subheader("🎯 Métricas Jurídico-Financeiras")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if valor > 0:
            percentual_juros = (valor_juros / valor) * 100
            st.metric("Impacto dos Juros", f"{percentual_juros:.1f}%", f"R$ {valor_juros:,.2f}")
    with col2:
        if valor > 0:
            percentual_total = ((total - valor) / valor) * 100
            st.metric("Acréscimo Total", f"{percentual_total:.1f}%", f"R$ {total - valor:,.2f}")
    with col3:
        if meses > 0:
            valor_mensal = valor_juros / meses
            st.metric("Juros Mensais", f"R$ {valor_mensal:,.2f}", f"{meses} meses")
    with col4:
        if aplicar_523:
            impacto_523 = multa_523 + honorarios_523
            st.metric("Impacto Art. 523", f"R$ {impacto_523:,.2f}", "20% adicional")

    st.markdown("---")
    st.subheader("📋 Relatório Detalhado")
    if total > 0:
        dados_relatorio = {
            "Componente": componentes,
            "Valor (R$)": [f"R$ {v:,.2f}" for v in valores],
            "Percentual (%)": [f"{(v / total) * 100:.1f}%" for v in valores]
        }
        df_relatorio = pd.DataFrame(dados_relatorio)
        st.dataframe(df_relatorio, use_container_width=True)


# 🔸 FUNÇÃO para gerar a demonstração inicial
def gerar_mock_inicial():
    valor_mock = VALORES_MOCK["valor"]
    data_juros_mock = VALORES_MOCK["data_juros"]
    data_final_mock = VALORES_MOCK["data_final"]

    diff_mock = relativedelta(data_final_mock, data_juros_mock)
    meses_mock = diff_mock.years * 12 + diff_mock.months
    taxa_mensal_mock = 0.12 / 12

    valor_juros_mock = valor_mock * (taxa_mensal_mock * meses_mock)
    valor_corrigido_mock = valor_mock + valor_juros_mock
    valor_honorarios_mock = valor_corrigido_mock * (VALORES_MOCK["honorarios"] / 100)
    multa_523_mock = valor_corrigido_mock * 0.10 if VALORES_MOCK["aplicar_523"] else 0
    honorarios_523_mock = valor_corrigido_mock * 0.10 if VALORES_MOCK["aplicar_523"] else 0
    total_mock = valor_corrigido_mock + valor_honorarios_mock + multa_523_mock + honorarios_523_mock

    st.subheader("📊 Exemplo de Resultado")
    st.write(f"💰 **Valor Base:** R$ {valor_mock:,.2f}")
    st.write(f"📈 **Juros:** R$ {valor_juros_mock:,.2f}")
    st.write(f"🔧 **Valor Corrigido (Base + Juros):** R$ {valor_corrigido_mock:,.2f}")
    st.write(f"⚖️ **Honorários ({VALORES_MOCK['honorarios']}%):** R$ {valor_honorarios_mock:,.2f}")
    if VALORES_MOCK["aplicar_523"]:
        st.write(f"🚨 **Multa (Art. 523 §1º):** R$ {multa_523_mock:,.2f}")
        st.write(f"🚨 **Honorários 523 (Art. 523 §1º):** R$ {honorarios_523_mock:,.2f}")
    st.success(f"💵 **Total Final:** R$ {total_mock:,.2f}")

    gerar_graficos_e_metricas(
        valor_mock, valor_juros_mock, valor_corrigido_mock, valor_honorarios_mock,
        multa_523_mock, honorarios_523_mock, total_mock, meses_mock, taxa_mensal_mock,
        VALORES_MOCK["aplicar_523"], is_mock=True
    )

# --- LÓGICA PRINCIPAL DA PÁGINA ---

if submitted:
    if data_final < data_inicial:
        st.error("❌ A Data Final não pode ser anterior à Data Inicial.")
    else:
        diff = relativedelta(data_final, data_juros)
        meses = max(0, diff.years * 12 + diff.months)

        st.info(f"Período considerado para juros: {meses} meses.")

        taxa_mensal = 0
        if tipo_juros == "Juros Simples 6% a.a.":
            taxa_mensal = 0.06 / 12
        elif tipo_juros == "Juros Simples 12% a.a.":
            taxa_mensal = 0.12 / 12
        elif tipo_juros == "Juros do Código Civil (6% ou 12% a.a.)":
            taxa_mensal = 0.12 / 12 if tipo_obrigacao == "Contratual (12% a.a.)" else 0.06 / 12
        elif tipo_juros == "Taxa legal (Lei 14.905/24) — Em desenvolvimento":
            st.warning("⚠️ Cálculo da Taxa Legal (Lei 14.905/24) está em desenvolvimento.")
            taxa_mensal = None

        if taxa_mensal is not None:
            valor_juros = valor * (taxa_mensal * meses)
            valor_corrigido = valor + valor_juros
            valor_honorarios = valor_corrigido * (honorarios / 100)
            multa_523 = valor_corrigido * 0.10 if aplicar_523 else 0
            honorarios_523 = valor_corrigido * 0.10 if aplicar_523 else 0
            total = valor_corrigido + valor_honorarios + multa_523 + honorarios_523

            st.subheader("📊 Resultado do Cálculo")
            st.write(f"💰 **Valor Base:** R$ {valor:,.2f}")
            st.write(f"📈 **Juros:** R$ {valor_juros:,.2f}")
            st.write(f"🔧 **Valor Corrigido (Base + Juros):** R$ {valor_corrigido:,.2f}")
            st.write(f"⚖️ **Honorários ({honorarios}%):** R$ {valor_honorarios:,.2f}")
            if aplicar_523:
                st.write(f"🚨 **Multa (Art. 523 §1º):** R$ {multa_523:,.2f}")
                st.write(f"🚨 **Honorários 523 (Art. 523 §1º):** R$ {honorarios_523:,.2f}")
            st.success(f"💵 **Total Final:** R$ {total:,.2f}")

            gerar_graficos_e_metricas(
                valor, valor_juros, valor_corrigido, valor_honorarios,
                multa_523, honorarios_523, total, meses, taxa_mensal,
                aplicar_523, is_mock=False
            )
else:
    # Mostra a demonstração inicial se o formulário ainda não foi enviado
    gerar_mock_inicial()

# --- SEÇÕES QUE APARECEM SEMPRE ---

st.markdown("---")
st.info("""
        💡 **Observações Técnicas:**
        - O cálculo de juros é realizado de forma simples (não composta).
        - A ferramenta ainda não aplica índices de correção monetária (ex: IPCA, INPC), apenas os juros selecionados.
        - Honorários são calculados sobre o valor corrigido (principal + juros).
        - A multa e os honorários do Art. 523, §1º do CPC incidem sobre o valor corrigido em caso de inadimplemento na fase de cumprimento de sentença.
        """)

st.markdown("---")
st.markdown("""
        <div style='text-align: center; color: #666; font-size: 12px;'>
        Cálculo realizado por ferramenta desenvolvida por Pedro Potz<br>
        Advogado especializado em soluções jurídico-tecnológicas<br>
        🦄 <em>Advogado que programa é unicórnio!</em>
        </div>
        """, unsafe_allow_html=True)
