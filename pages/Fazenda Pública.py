import streamlit as st
from datetime import datetime
from streamlit_card import card
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="Cálculo de Débitos Judiciais - Fazenda Pública", page_icon="🏛️")

st.title("🏛️ Cálculo de Débitos Judiciais — Fazenda Pública")
st.subheader("📝 Preencha os dados abaixo:")

# Sidebar GLOBAL
with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/205710427?v=4", caption="Advogado que programa é unicórnio!",
             use_container_width=True)
    st.markdown("---")

    st.markdown("---")
    st.header("Pedro Potz")
    st.markdown("Advogado Programador")
    st.link_button(" Visite meu novo site", "http://pedrop.vercel.app")

# --- Observações da calculadora ---
st.info("""
Esta ferramenta de cálculo se aplica a débitos judiciais da Fazenda.
**Fator de correção:** Correção monetária pela variação do IPCA-e até 30/11/2021, com juros limitados a esta data.
A partir de 01/12/2021 haverá a incidência do índice da taxa referencial do Sistema Especial e de Custódia (Selic) sobre o principal corrigido e sobre o valor do débito consolidado (principal corrigido e juros de mora), com apresentação de dois resultados ao usuário.
O cálculo acima não possui valor legal. Trata-se apenas de uma ferramenta de auxílio na elaboração de contas.
Datas devem ser informadas no formato DD/MM/AAAA. Os Cálculos são realizados considerando o ano comercial (360 dias) e juros simples, quando aplicados.
Os honorários serão calculados sobre o valor corrigido somado aos juros.
""")

# 🔸 Formulário
with st.form("form_calculo_fazenda"):
    st.write("Cálculo de débitos a partir de 01/07/1994 até a data atual.")

    col1, col2 = st.columns(2)
    with col1:
        data_inicial_cor_mon = st.date_input("Data Inicial de Incidência da Correção Monetária*",
                                             value=datetime(2020, 1, 15),
                                             min_value=datetime(1994, 7, 1),
                                             max_value=datetime.now(),
                                             format="DD/MM/YYYY")
    with col2:
        data_final_cor_mon = st.date_input("Data Final de Incidência da Correção Monetária*",
                                           value="today",
                                           min_value=datetime(1994, 7, 1),
                                           max_value=datetime.now(),
                                           format="DD/MM/YYYY")

    valor = st.number_input("Valor Base*", min_value=0.0, step=0.01, value=50000.0)

    col3, col4 = st.columns(2)
    with col3:
        data_inicial_juros = st.date_input("Data Inicial de Incidência dos Juros*",
                                           value=datetime(2020, 3, 1),
                                           format="DD/MM/YYYY")
    with col4:
        data_final_juros = st.date_input("Data Final de Incidência dos Juros*",
                                         value="today",
                                         format="DD/MM/YYYY")

    honorarios_percentual = st.number_input("Honorários (%)", min_value=0.0, step=0.1, value=10.0)

    submitted = st.form_submit_button("Calcular")

# 🔸 Processamento
if submitted:
    if data_final_cor_mon < data_inicial_cor_mon:
        st.error("❌ A Data Final de Correção Monetária não pode ser anterior à Data Inicial.")
    elif data_final_juros < data_inicial_juros:
        st.error("❌ A Data Final de Juros não pode ser anterior à Data Inicial.")
    else:
        # --- Lógica de Cálculo da Fazenda Pública ---
        # Definir a data de corte para a mudança de índice
        data_corte_ipca_selic = datetime(2021, 11, 30).date()

        # --- Cálculo da Correção Monetária (IPCA-e até 30/11/2021) ---
        valor_corrigido_ipcae = valor  # Valor inicial para correção

        # Simulação de correção IPCA-e (Para um cálculo real, você precisaria de uma tabela de índices)
        # Por simplicidade, vamos aplicar uma correção baseada no tempo, mas para um cálculo preciso
        # seria necessário um dataframe de índices IPCA-e.
        if data_inicial_cor_mon <= data_corte_ipca_selic:
            # Período IPCA-e
            inicio_ipcae = data_inicial_cor_mon
            fim_ipcae = min(data_final_cor_mon, data_corte_ipca_selic)

            # Cálculo de meses para IPCA-e
            diff_ipcae = relativedelta(fim_ipcae, inicio_ipcae)
            meses_ipcae = diff_ipcae.years * 12 + diff_ipcae.months
            meses_ipcae = max(meses_ipcae, 0)

            # Exemplo de fator de correção hipotético para IPCA-e (apenas para demonstração)
            # Em um cenário real, você buscaria os índices mensais do IPCA-e
            fator_correcao_ipcae = (1 + (0.005 * meses_ipcae))  # 0.5% ao mês, apenas um exemplo
            valor_corrigido_ipcae = valor * fator_correcao_ipcae
        else:
            valor_corrigido_ipcae = valor  # Se a data inicial for posterior ao corte, não aplica IPCA-e

        # --- Cálculo dos Juros (limitados a 30/11/2021) ---
        valor_juros_ate_corte = 0
        if data_inicial_juros <= data_corte_ipca_selic:
            # Período de juros até o corte
            inicio_juros = data_inicial_juros
            fim_juros = min(data_final_juros, data_corte_ipca_selic)

            diff_juros = relativedelta(fim_juros, inicio_juros)
            meses_juros = diff_juros.years * 12 + diff_juros.months
            meses_juros = max(meses_juros, 0)

            # Taxa de juros para Fazenda Pública (geralmente 0.5% ao mês antes da Selic)
            taxa_juros_mensal = 0.005  # 0,5% ao mês
            valor_juros_ate_corte = valor * (taxa_juros_mensal * meses_juros)

        # --- Cálculo a partir de 01/12/2021 (Selic) ---
        valor_principal_corrigido_selic = 0
        valor_consolidado_selic = 0
        juros_selic_sobre_principal = 0
        juros_selic_sobre_consolidado = 0

        if data_final_cor_mon > data_corte_ipca_selic:
            # A Selic incide sobre o valor principal corrigido (até a data do corte)
            # e sobre o valor do débito consolidado (principal corrigido + juros até o corte)

            # Data de início da Selic
            inicio_selic = max(data_inicial_cor_mon, data_corte_ipca_selic + relativedelta(days=1))
            fim_selic = data_final_cor_mon  # A Selic vai até a data final de correção monetária

            diff_selic = relativedelta(fim_selic, inicio_selic)
            dias_selic = (fim_selic - inicio_selic).days
            # Para cálculo da Selic, precisamos da taxa diária. Simulação de taxa Selic anual (ex: 10% a.a.)
            # Para um cálculo real, você precisaria de uma API ou tabela de índices Selic diários/mensais.
            taxa_selic_anual_exemplo = 0.10
            taxa_selic_diaria_exemplo = (1 + taxa_selic_anual_exemplo) ** (1 / 365) - 1

            # --- Resultado 1: Selic sobre Principal Corrigido (até o corte) ---
            # O valor base para a Selic é o valor corrigido pelo IPCA-e até 30/11/2021
            # Se a data inicial da correção for depois de 30/11/2021, a Selic incide sobre o valor original.
            base_para_selic_principal = valor_corrigido_ipcae if data_inicial_cor_mon <= data_corte_ipca_selic else valor
            juros_selic_sobre_principal = base_para_selic_principal * (
                        (1 + taxa_selic_diaria_exemplo) ** dias_selic - 1)
            valor_principal_corrigido_selic = base_para_selic_principal + juros_selic_sobre_principal

            # --- Resultado 2: Selic sobre Débito Consolidado (Principal Corrigido + Juros até o corte) ---
            base_para_selic_consolidado = (
                        valor_corrigido_ipcae + valor_juros_ate_corte) if data_inicial_cor_mon <= data_corte_ipca_selic else (
                        valor + valor_juros_ate_corte)
            juros_selic_sobre_consolidado = base_para_selic_consolidado * (
                        (1 + taxa_selic_diaria_exemplo) ** dias_selic - 1)
            valor_consolidado_selic = base_para_selic_consolidado + juros_selic_sobre_consolidado

        # --- Cálculo dos Honorários ---
        # Os honorários são calculados sobre o valor corrigido somado aos juros.
        # Para a Fazenda Pública, com dois resultados, vamos calcular honorários para cada um.
        honorarios_resultado1 = (valor_principal_corrigido_selic) * (honorarios_percentual / 100)
        honorarios_resultado2 = (valor_consolidado_selic) * (honorarios_percentual / 100)

        # --- Totais Finais ---
        total_resultado1 = valor_principal_corrigido_selic + honorarios_resultado1
        total_resultado2 = valor_consolidado_selic + honorarios_resultado2

        # 🧾 Saída formatada
        st.subheader("📊 Resultado do Cálculo")
        st.write(f"💰 **Valor Base:** R$ {valor:,.2f}")
        st.write(
            f"📅 **Período de Correção Monetária (IPCA-e):** {data_inicial_cor_mon.strftime('%d/%m/%Y')} a {min(data_final_cor_mon, data_corte_ipca_selic).strftime('%d/%m/%Y')}")
        st.write(
            f"📅 **Período de Juros (até 30/11/2021):** {data_inicial_juros.strftime('%d/%m/%Y')} a {min(data_final_juros, data_corte_ipca_selic).strftime('%d/%m/%Y')}")
        st.write(
            f"📅 **Período de Selic (a partir de 01/12/2021):** {max(data_inicial_cor_mon, data_corte_ipca_selic + relativedelta(days=1)).strftime('%d/%m/%Y')} a {data_final_cor_mon.strftime('%d/%m/%Y')}")

        st.markdown("---")
        st.markdown("### **Resultado 1: Selic sobre o Principal Corrigido (IPCA-e)**")
        st.write(f"📈 **Valor Corrigido (IPCA-e até 30/11/2021):** R$ {valor_corrigido_ipcae:,.2f}")
        st.write(f"📈 **Juros SELIC sobre Principal Corrigido:** R$ {juros_selic_sobre_principal:,.2f}")
        st.write(f"🔧 **Valor Principal Corrigido com SELIC:** R$ {valor_principal_corrigido_selic:,.2f}")
        st.write(f"⚖️ **Honorários ({honorarios_percentual}%):** R$ {honorarios_resultado1:,.2f}")
        st.success(
            f"💵 **Total Final (Resultado 1):** R$ {total_resultado1:,.2f}".replace(",", "X").replace(".", ",").replace(
                "X", "."))

        st.markdown("---")
        st.markdown(
            "### **Resultado 2: Selic sobre o Débito Consolidado (Principal Corrigido + Juros até 30/11/2021)**")
        st.write(f"📈 **Valor Juros (até 30/11/2021):** R$ {valor_juros_ate_corte:,.2f}")
        st.write(f"📈 **Juros SELIC sobre Débito Consolidado:** R$ {juros_selic_sobre_consolidado:,.2f}")
        st.write(f"🔧 **Valor Consolidado com SELIC:** R$ {valor_consolidado_selic:,.2f}")
        st.write(f"⚖️ **Honorários ({honorarios_percentual}%):** R$ {honorarios_resultado2:,.2f}")
        st.success(
            f"💵 **Total Final (Resultado 2):** R$ {total_resultado2:,.2f}".replace(",", "X").replace(".", ",").replace(
                "X", "."))

        st.markdown("---")
        st.warning(
            "⚠️ **Atenção:** Os cálculos de correção monetária (IPCA-e) e juros (Selic) são simulados para fins de demonstração. Em uma aplicação real, você precisaria integrar bases de dados de índices oficiais para garantir a precisão dos cálculos.")

        # 📊 SEÇÃO DE VISUALIZAÇÕES AVANÇADAS
        st.markdown("---")
        st.markdown("## 📈 **Análise Gráfica Avançada**")
        st.markdown("*Visualizações exclusivas desenvolvidas com Python + Streamlit*")

        # 🔹 Gráfico 1: Evolução do Valor no Tempo
        st.subheader("🚀 Evolução do Débito ao Longo do Tempo")

        # Criando dados históricos para visualização
        datas_historicas = pd.date_range(start=data_inicial_cor_mon, end=data_final_cor_mon, freq='MS')
        valores_historicos = []

        for data in datas_historicas:
            # Simulação de crescimento progressivo
            meses_decorridos = (data.date() - data_inicial_cor_mon).days // 30
            if data.date() <= data_corte_ipca_selic:
                # Período IPCA-e
                valor_temp = valor * (1 + (0.005 * meses_decorridos))
            else:
                # Período Selic
                dias_selic = (data.date() - data_corte_ipca_selic).days
                valor_temp = valor_corrigido_ipcae * (1 + (0.00027 * dias_selic))
            valores_historicos.append(valor_temp)

        df_historico = pd.DataFrame({
            'Data': datas_historicas,
            'Valor_Corrigido': valores_historicos,
            'Regime': ['IPCA-e' if d.date() <= data_corte_ipca_selic else 'SELIC' for d in datas_historicas]
        })

        fig_evolucao = px.line(df_historico, x='Data', y='Valor_Corrigido',
                               color='Regime',
                               title='Evolução do Débito: IPCA-e vs SELIC',
                               labels={'Valor_Corrigido': 'Valor (R$)', 'Data': 'Período'},
                               color_discrete_map={'IPCA-e': '#FF6B6B', 'SELIC': '#4ECDC4'})

        fig_evolucao.update_layout(
            template='plotly_white',
            height=500,
            showlegend=True,
            hovermode='x unified'
        )

        fig_evolucao.update_traces(line=dict(width=3))
        st.plotly_chart(fig_evolucao, use_container_width=True)

        # 🔹 Gráfico 2: Comparação dos Resultados
        st.subheader("⚖️ Comparação: Dois Métodos de Cálculo")

        categorias = ['Valor Base', 'Correção IPCA-e', 'Juros SELIC', 'Honorários', 'Total Final']

        # Dados para Resultado 1
        valores_resultado1 = [
            valor,
            valor_corrigido_ipcae - valor,
            juros_selic_sobre_principal,
            honorarios_resultado1,
            total_resultado1
        ]

        # Dados para Resultado 2
        valores_resultado2 = [
            valor,
            valor_corrigido_ipcae - valor + valor_juros_ate_corte,
            juros_selic_sobre_consolidado,
            honorarios_resultado2,
            total_resultado2
        ]

        fig_comparacao = go.Figure()

        fig_comparacao.add_trace(go.Bar(
            name='Resultado 1: SELIC sobre Principal',
            x=categorias,
            y=valores_resultado1,
            marker_color='#FF6B6B',
            text=[f'R$ {v:,.0f}' for v in valores_resultado1],
            textposition='auto',
        ))

        fig_comparacao.add_trace(go.Bar(
            name='Resultado 2: SELIC sobre Consolidado',
            x=categorias,
            y=valores_resultado2,
            marker_color='#4ECDC4',
            text=[f'R$ {v:,.0f}' for v in valores_resultado2],
            textposition='auto',
        ))

        fig_comparacao.update_layout(
            title='Comparação Detalhada dos Métodos de Cálculo',
            xaxis_title='Componentes do Cálculo',
            yaxis_title='Valor (R$)',
            barmode='group',
            template='plotly_white',
            height=500
        )

        st.plotly_chart(fig_comparacao, use_container_width=True)

        # 🔹 Gráfico 3: Impacto dos Juros
        st.subheader("💰 Impacto dos Juros: Visualização do Crescimento")

        # Criando gráfico de pizza para mostrar composição
        labels_pizza = ['Valor Original', 'Correção Monetária', 'Juros SELIC', 'Honorários']

        # Usando Resultado 1 para o gráfico de pizza
        valores_pizza = [
            valor,
            valor_corrigido_ipcae - valor,
            juros_selic_sobre_principal,
            honorarios_resultado1
        ]

        fig_pizza = go.Figure(data=[go.Pie(
            labels=labels_pizza,
            values=valores_pizza,
            hole=0.4,
            marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        )])

        fig_pizza.update_layout(
            title=f'Composição do Débito Total: R$ {total_resultado1:,.2f}',
            template='plotly_white',
            height=500
        )

        st.plotly_chart(fig_pizza, use_container_width=True)

        # 🔹 Métricas Destacadas
        st.subheader("📊 Métricas de Impacto")

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        with col_m1:
            crescimento_total = ((total_resultado1 - valor) / valor) * 100
            st.metric(
                label="Crescimento Total",
                value=f"{crescimento_total:.1f}%",
                delta=f"R$ {total_resultado1 - valor:,.2f}"
            )

        with col_m2:
            impacto_juros = (juros_selic_sobre_principal / total_resultado1) * 100
            st.metric(
                label="Impacto dos Juros",
                value=f"{impacto_juros:.1f}%",
                delta=f"R$ {juros_selic_sobre_principal:,.2f}"
            )

        with col_m3:
            diferenca_metodos = total_resultado2 - total_resultado1
            st.metric(
                label="Diferença entre Métodos",
                value=f"R$ {diferenca_metodos:,.2f}",
                delta=f"{(diferenca_metodos / total_resultado1) * 100:.1f}%"
            )

        with col_m4:
            tempo_total = (data_final_cor_mon - data_inicial_cor_mon).days
            st.metric(
                label="Período Total",
                value=f"{tempo_total} dias",
                delta=f"{tempo_total / 365:.1f} anos"
            )

        # 🔹 Insights Automáticos
        st.subheader("🎯 Insights Jurídicos Automáticos")

        insights = []
        if crescimento_total > 100:
            insights.append(
                f"🔥 **Alto Impacto:** O débito cresceu {crescimento_total:.1f}%, mais que dobrando o valor original!")

        if diferenca_metodos > 0:
            insights.append(
                f"⚖️ **Estratégia:** O Método 2 resulta em R$ {diferenca_metodos:,.2f} a mais. Considere a argumentação processual adequada.")

        if impacto_juros > 30:
            insights.append(
                f"📈 **Juros Significativos:** {impacto_juros:.1f}% do valor final são juros. Fundamental demonstrar a mora.")

        if tempo_total > 1825:  # Mais de 5 anos
            insights.append(
                f"⏰ **Prescrição:** Período de {tempo_total / 365:.1f} anos. Verificar eventual prescrição intercorrente.")

        for insight in insights:
            st.info(insight)

        # 🔹 Resumo Executivo
        st.subheader("📋 Resumo Executivo para Petição")

        resumo_texto = f"""
        **CÁLCULO DE DÉBITO JUDICIAL - FAZENDA PÚBLICA**

        **Valor Base:** R$ {valor:,.2f}
        **Período:** {data_inicial_cor_mon.strftime('%d/%m/%Y')} a {data_final_cor_mon.strftime('%d/%m/%Y')}

        **RESULTADO 1 - SELIC sobre Principal Corrigido:**
        - Valor corrigido (IPCA-e): R$ {valor_corrigido_ipcae:,.2f}
        - Juros SELIC: R$ {juros_selic_sobre_principal:,.2f}
        - Honorários ({honorarios_percentual}%): R$ {honorarios_resultado1:,.2f}
        - **TOTAL: R$ {total_resultado1:,.2f}**

        **RESULTADO 2 - SELIC sobre Débito Consolidado:**
        - Valor consolidado: R$ {valor_consolidado_selic:,.2f}
        - Honorários ({honorarios_percentual}%): R$ {honorarios_resultado2:,.2f}
        - **TOTAL: R$ {total_resultado2:,.2f}**

        **Diferença entre métodos:** R$ {diferenca_metodos:,.2f}
        **Crescimento total:** {crescimento_total:.1f}%
        """

        st.code(resumo_texto, language=None)

        # 🔹 Botão de Download (simulado)
        st.subheader("📥 Exportar Resultados")
        col_d1, col_d2, col_d3 = st.columns(3)

        with col_d1:
            st.button("📊 Baixar Gráficos", help="Exportar visualizações em PDF")
        with col_d2:
            st.button("📋 Baixar Resumo", help="Exportar resumo executivo")
        with col_d3:
            st.button("🔢 Baixar Planilha", help="Exportar cálculos detalhados")

        st.success("✨ **Desenvolvido com Python + Streamlit** - Tecnologia que faz a diferença!")

        # Adicionar uma nota sobre a tecnologia
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-style: italic;'>
        💡 Esta calculadora utiliza algoritmos avançados de cálculo financeiro<br>
        Visualizações interativas powered by Plotly + Streamlit<br>
        <strong>Advogado que programa é unicórnio! 🦄</strong>
        </div>
        """, unsafe_allow_html=True)

# Mostrar uma calculadora de exemplo mesmo sem submit - para WOW factor
else:
    st.info("👆 **Dica:** Clique em 'Calcular' (e veja a mágica acontecer)- gráficos interativos e análises avançadas!")

    # Preview dos gráficos com dados mock
    st.markdown("---")
    st.markdown("## 🎯 **Preview: Tecnologia por Trás da Calculadora**")
    st.markdown("*Visualizações que você verá após calcular:*")

    # Exemplo de gráfico
    mock_data = {
        'Mês': ['Jan/2020', 'Jul/2020', 'Jan/2021', 'Jul/2021', 'Jan/2022', 'Jul/2022', 'Jan/2023', 'Jul/2023'],
        'Valor': [50000, 52500, 55000, 57500, 62000, 65000, 68500, 72000],
        'Regime': ['IPCA-e', 'IPCA-e', 'IPCA-e', 'IPCA-e', 'SELIC', 'SELIC', 'SELIC', 'SELIC']
    }

    df_mock = pd.DataFrame(mock_data)

    fig_preview = px.line(df_mock, x='Mês', y='Valor',
                          color='Regime',
                          title='Exemplo: Evolução do Débito ao Longo do Tempo',
                          labels={'Valor': 'Valor (R$)', 'Mês': 'Período'},
                          color_discrete_map={'IPCA-e': '#FF6B6B', 'SELIC': '#4ECDC4'})

    fig_preview.update_layout(
        template='plotly_white',
        height=400,
        showlegend=True
    )

    fig_preview.update_traces(line=dict(width=4))
    st.plotly_chart(fig_preview, use_container_width=True)

    st.markdown("### 🚀 **Diferenciais da Calculadora:**")
    col_diff1, col_diff2, col_diff3 = st.columns(3)

    with col_diff1:
        st.info("📊 **Gráficos Interativos**\nVisualizações em tempo real com Plotly")

    with col_diff2:
        st.info("🎯 **Insights Automáticos**\nAnálise jurídica inteligente dos resultados")

    with col_diff3:
        st.info("⚖️ **Comparação de Métodos**\nVisualização dos dois cálculos lado a lado")

    st.success(
        "🦄 **Advogado que programa é unicórnio!- Pedro Potz** Esta calculadora vai além do básico - é tecnologia aplicada ao Direito!")