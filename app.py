import streamlit as st
from streamlit_card import card
from streamlit_lottie import st_lottie
import json
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Cálculos Jurídicos - Por Pedro Potz", page_icon="⚖️", layout="wide")

# Carregar animação Lottie
with open("cat1.json") as f:
    lottie_json = json.load(f)

# Sidebar GLOBAL
with st.sidebar:
    # Corrigido: use_column_width por use_container_width
    st.image("https://avatars.githubusercontent.com/u/205710427?v=4", caption="Advogado que programa é unicórnio!", use_container_width=True) # Sua imagem com uma frase de poder
    st.markdown("---")
    st.header("Pedro Potz")
    st.markdown("Advogado Programador")
    st.link_button("Conheça meu novo site", "https://pedrop.vercel.app/")

# --- Página Principal ---
st.title('👈🏻⚖️ Calculadoras Jurídicas' )

st_lottie(lottie_json, height=250, key="cat1", speed=1, loop=True)

st.markdown("""

Este projeto, 'Calculadoras Jurídicas', foi **desenvolvido com vocês em mente**: meus alunos, meus clientes e todos que buscam otimizar a prática jurídica com a tecnologia.  Aqui, a complexidade dos cálculos judiciais encontra a simplicidade da automação, permitindo que você economize tempo precioso e aumente a precisão em suas análises.

Atualmente, você encontrará duas calculadoras essenciais aqui:

* **Calculadora de Débitos Judiciais:** Ideal para atualizar valores em processos cíveis, trabalhistas, etc., considerando juros, correção monetária e multas.
* **Calculadora da Fazenda Pública:** Específica para cálculos envolvendo débitos contra a Fazenda Pública, com as nuances de juros e correção aplicáveis a esses casos.

Mas este aplicativo é mais do que apenas calculadoras. Ele é uma **demonstração viva do que é possível criar** com programação, mesmo sem ser um desenvolvedor "tradicional".
""")

st.markdown("---")

st.header("Por Que um Advogado Deve Aprender a Programar?")

st.markdown("""
No mundo jurídico atual, a tecnologia não é mais um diferencial, é uma necessidade. Dominar conceitos de programação, mesmo que básicos, abre um leque de possibilidades:

* **Automação de Tarefas Repetitivas:** Chega de copiar e colar! Imagine gerar petições, contratos ou relatórios automaticamente.
* **Análise de Dados Jurídicos:** Extraia insights de grandes volumes de informações processuais para tomar decisões mais estratégicas.
* **Criação de Ferramentas Personalizadas:** Desenvolva suas próprias calculadoras, dashboards ou assistentes virtuais jurídicos, como este que você está usando agora.
* **Inovação na Advocacia:** Esteja na vanguarda da advocacia 4.0, oferecendo serviços mais eficientes e inovadores aos seus clientes.
* **Entendimento de Legal Design e Legal Tech:** Compreenda profundamente as ferramentas que moldam o futuro do direito, não apenas como usuário, mas como criador.
""")

st.info("""
**Que tal pensar em qual outra tarefa repetitiva do seu dia a dia jurídico poderia ser automatizada com um pouco de código?**
""")

st.markdown("---")

st.subheader("Comece Sua Jornada na Programação Jurídica:")

# Novo gráfico interativo
st.markdown("#### Visualize o Potencial dos Seus Honorários com Programação")

st.write("Mova os sliders para ver o impacto da automação no seu tempo e, consequentemente, nos seus honorários!")

col_slider1, col_slider2 = st.columns(2)

with col_slider1:
    tempo_manual_dia = st.slider(
        'Horas diárias em tarefas repetitivas (manual)',
        min_value=0.5, max_value=4.0, value=2.0, step=0.5,
        format="%.1f horas"
    )

with col_slider2:
    reducao_programacao = st.slider(
        'Redução percentual de tempo com automação',
        min_value=10, max_value=90, value=60, step=5,
        format="%d%%"
    )

horas_trabalhadas_dia = 8
valor_hora_advogado = st.slider(
    'Valor médio da sua hora de trabalho (R$)',
    min_value=50, max_value=500, value=250, step=10,
    format="R$ %d"
)

# Cálculos
tempo_automatizado_dia = tempo_manual_dia * (1 - reducao_programacao / 100)
tempo_ganho_dia = tempo_manual_dia - tempo_automatizado_dia
honorarios_potenciais_ganho_dia = tempo_ganho_dia * valor_hora_advogado * 0.8 # Assumindo 80% do tempo ganho é convertível em produtividade/honorários

# Dados para o gráfico
data = {
    'Cenário': ['Manual', 'Com Programação'],
    'Horas Repetitivas por Dia': [tempo_manual_dia, tempo_automatizado_dia],
    'Valor Potencial por Dia (R$)': [tempo_manual_dia * valor_hora_advogado, tempo_automatizado_dia * valor_hora_advogado] # Apenas para visualização inicial
}
df = pd.DataFrame(data)

# Criar gráfico de barras comparativo para Horas Repetitivas
fig_horas = px.bar(
    df,
    x='Cenário',
    y='Horas Repetitivas por Dia',
    color='Cenário',
    title='Horas Dedicadas a Tarefas Repetitivas por Dia',
    labels={'Horas Repetitivas por Dia': 'Horas'},
    text='Horas Repetitivas por Dia',
    color_discrete_map={'Manual': '#FF6347', 'Com Programação': '#4682B4'} # Cores atraentes
)
fig_horas.update_traces(texttemplate='%{y:.1f}h', textposition='outside')
fig_horas.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', yaxis_title="Horas")
st.plotly_chart(fig_horas, use_container_width=True)

st.success(f"Com a programação, você poderia **ganhar aproximadamente {tempo_ganho_dia:.1f} horas por dia** de tempo produtivo, o que representa um potencial de **R$ {honorarios_potenciais_ganho_dia:,.2f} em honorários adicionais por dia** (considerando 80% de conversão do tempo ganho em trabalho útil).")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Linhas de Código Escritas", value="Milhares")
    st.markdown("A cada linha, você constrói um novo futuro para sua prática.")

with col2:
    st.metric(label="Tempo Economizado (Estimado)", value="Horas por semana")
    st.markdown("Menos tempo com tarefas braçais, mais tempo com o que realmente importa.")

with col3:
    st.metric(label="Potencial de Inovação", value="Infinito")
    st.markdown("Sua criatividade é o único limite para o que você pode criar.")

st.markdown("---")

st.write("Estou aqui para guiá-los nessa jornada. Juntos, vamos desmistificar a tecnologia")

st.markdown("### Não perca meus tutoriais e outras ferrramentas gratuitas! ")
st.link_button("Vamos juntos!" , "https://pedrop.vercel.app/", help="Aprenda a programar do zero ao avançado!")




st.markdown("---")
st.link_button("Geo -visualização Avançada", "https://runmapy.streamlit.app/")
st.link_button("Visualização de dados simples","https://sleepdataview.streamlit.app/")
st.link_button("Bem-vindo ao Futuro: Esqueça Excel","https://pedroduck.streamlit.app")
st.markdown("---")

st.markdown("---")
st.markdown("""
        <div style='text-align: center; color: #666; font-size: 12px;'>
        Cálculo realizado por ferramenta desenvolvida por Pedro Potz<br>
        Advogado especializado em soluções jurídico-tecnológicas<br>
        🦄 <em>Advogado que programa é unicórnio!</em>
        </div>
        """, unsafe_allow_html=True)

