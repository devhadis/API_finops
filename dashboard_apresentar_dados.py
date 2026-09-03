import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import glob
import os
import base64

# 1. Configuração de Tela Cheia (Modo TV / NOC)
st.set_page_config(
    page_title="FinOps Operations Cockpit", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Limpa o cache antigo travado na memória para evitar problemas de rastreamento
st.cache_data.clear()

# Inicialização das variáveis de controle de acesso na memória do navegador
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "email_usuario" not in st.session_state:
    st.session_state.email_usuario = ""

# -----------------------------------------------------------------------------
# BANCO DE DADOS DE USUÁRIOS
# -----------------------------------------------------------------------------
USUARIOS_PERMITIDOS = {
    "hadisdev261@gmail.com": "XP@2026_FinOps",
    "diretoria@xp.com.br": "Mudar@123"
}

# -----------------------------------------------------------------------------
# RESOLUÇÃO INTELIGENTE DE CAMINHO (Compatível com Local e Nuvem)
# -----------------------------------------------------------------------------
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))

# Se já estiver dentro da pasta XP (comum no deploy do Streamlit Cloud), usa a própria pasta atual.
if os.path.basename(DIRETORIO_ATUAL) == "XP":
    CAMINHO_BASE = DIRETORIO_ATUAL
else:
    CAMINHO_BASE = os.path.join(DIRETORIO_ATUAL, "XP")

# -----------------------------------------------------------------------------
# FUNÇÃO PARA CONVERTER IMAGEM LOCAL PARA BASE64 (ESSENCIAL PARA HTML)
# -----------------------------------------------------------------------------
def obtener_imagem_base64(caminho_imagem):
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

# -----------------------------------------------------------------------------
# FLUXO DE AUTENTICAÇÃO DIRETA (SEM TOKEN POR E-MAIL)
# -----------------------------------------------------------------------------
caminho_logo = os.path.join(CAMINHO_BASE, "logo_scaleup.png")
logo_b64 = obtener_imagem_base64(caminho_logo)

if not st.session_state.autenticado:
    st.markdown("""
        <style>
            .main, .stApp { background-color: #0B0F19 !important; color: #E2E8F0 !important; }
            
            /* Caixa Central do Formulário de Login */
            .login-box { 
                background-color: #111827; 
                padding: 40px; 
                border-radius: 12px; 
                border: 1px solid #1F2937; 
                max-width: 450px; 
                margin: 80px auto 10px auto; 
                box-shadow: 0 12px 30px rgba(0,0,0,0.6);
            }
            
            /* Container da imagem centralizada */
            .logo-container {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                margin-bottom: 20px;
            }
            
            .logo-container img {
                max-width: 120px;
                height: auto;
                object-fit: contain;
            }
            
            .login-title { 
                text-align: center; 
                font-size: 19px; 
                font-weight: 600; 
                color: #FFFFFF; 
                margin-bottom: 25px; 
                letter-spacing: 0.5px;
            }
            div[data-testid="stNotification"] {
                margin-top: 15px !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        if logo_b64:
            st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_b64}"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="text-align:center; color:#F59E0B;">⚠️ Arquivo "logo_scaleup.png" não detectado.</p>', unsafe_allow_html=True)
            
        st.markdown('<div class="login-title">🔒 Cockpit FinOps — ScaleUp</div>', unsafe_allow_html=True)
        
        email_input = st.text_input("E-mail Corporativo")
        senha_input = st.text_input("Senha de Acesso", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Avançar", width="stretch"):
            email_limpo = email_input.strip()
            if email_limpo in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[email_limpo] == senha_input:
                st.session_state.autenticado = True
                st.session_state.email_usuario = email_limpo
                st.success("Acesso liberado!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# =============================================================================
# EXECUÇÃO DO COCKPIT COMPLETO (APÓS LOGIN SUCEDIDO)
# =============================================================================

# 2. CSS Customizado para o Layout de Caixas Integradas e KPIs de Destaque
st.markdown("""
    <style>
        /* Reset Geral do Streamlit para Fundo Escuro Puro */
        .main, .stApp, .stWidgetFormContainer, [data-testid="stHeader"] { 
            background-color: #0B0F19 !important; 
            color: #E2E8F0 !important; 
        }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        
        /* Cabeçalho Superior Fixo */
        .header-container {
            display: flex; justify-content: space-between; align-items: center;
            padding: 12px 20px; background-color: #111827; border-bottom: 2px solid #1F2937;
            border-radius: 8px; margin-bottom: 15px;
        }
        .header-title { font-size: 20px; font-weight: 700; color: #FFFFFF; }
        .company-badge {
            background-color: #1E3A8A; color: #38BDF8; padding: 4px 14px;
            border-radius: 6px; font-size: 13px; font-weight: bold; border: 1px solid #3B82F6;
        }
        
        /* Bloco de KPIs de Impacto Financeiro (Potential vs Realized) */
        .kpi-container {
            display: flex; gap: 20px; margin-bottom: 20px; width: 100%;
        }
        .kpi-card {
            flex: 1; background-color: #111827; border: 1px solid #1F2937;
            padding: 15px 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        }
        .kpi-label { font-size: 12px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; }
        .kpi-value-potential { font-size: 28px; font-weight: 700; color: #38BDF8; margin-top: 5px; }
        .kpi-value-realized { font-size: 28px; font-weight: 700; color: #10B981; margin-top: 5px; }
        
        /* Customização Estrita das Caixas Grandes do Gráfico */
        .chart-box {
            background-color: #111827 !important; 
            padding: 20px !important; 
            border-radius: 12px !important;
            border: 1px solid #1F2937 !important; 
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
            margin-bottom: 20px;
        }
        .chart-title {
            font-size: 13px !important; font-weight: 600 !important; color: #94A3B8 !important;
            text-transform: uppercase !important; letter-spacing: 0.5px !important; margin-bottom: 12px;
        }
        
        /* Ajuste de Espaçamento das Colunas */
        [data-testid="column"] { padding: 0px 8px !important; }
        .element-container, .stPlotlyChart { margin-bottom: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Limpeza de Strings e Formatação Numérica dos CSVs da IBM
def clean_numeric(val):
    if pd.isna(val): return 0.0
    val_str = str(val).strip().replace(' ', '')
    if val_str.startswith('-'):
        val_str = val_str[1:]
    if '.' in val_str and ',' in val_str:
        if val_str.find('.') < val_str.find(','):
            val_str = val_str.replace('.', '').replace(',', '.')
        else:
            val_str = val_str.replace(',', '')
    elif ',' in val_str:
        val_str = val_str.replace(',', '.')
    try: 
        return abs(float(val_str))
    except: 
        return 0.0

@st.cache_data(ttl=60)
def carregar_dados_da_estrutura(caminho_diretorio):
    lista_potencial = []
    lista_parking = []
    
    if not os.path.exists(caminho_diretorio):
        st.error(f"❌ **Diretório Não Encontrado**")
        st.markdown(f"O script procurou os arquivos em: `{caminho_diretorio}`")
        st.stop()
        
    # Busca recursiva ampla por arquivos de dados
    arquivos_potencial = glob.glob(os.path.join(caminho_diretorio, "*Potencial*.csv")) + \
                         glob.glob(os.path.join(caminho_diretorio, "**", "*Potencial*.csv"), recursive=True)
                         
    arquivos_parking = glob.glob(os.path.join(caminho_diretorio, "*Parking*.csv")) + \
                       glob.glob(os.path.join(caminho_diretorio, "**", "*Parking*.csv"), recursive=True)
    
    arquivos_potencial = list(set(arquivos_potencial))
    arquivos_parking = list(set(arquivos_parking))
    
    if not arquivos_potencial and not arquivos_parking:
        st.warning(f"⚠️ Nenhum arquivo .csv localizado dentro de: `{caminho_diretorio}`")
        st.stop()
    
    for arquivo in arquivos_potencial:
        try:
            df = pd.read_csv(arquivo, sep=";")
            df['saving_clean'] = df['saving'].apply(clean_numeric) if 'saving' in df.columns else 0.0
            df['savingmensal_clean'] = df['savingmensal'].apply(clean_numeric) if 'savingmensal' in df.columns else 0.0
            df['valor_final'] = df[['saving_clean', 'savingmensal_clean']].max(axis=1)
            df['parsed_time'] = pd.to_datetime(df['time'], errors='coerce')
            lista_potencial.append(df)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo {os.path.basename(arquivo)}: {e}")
            
    for arquivo in arquivos_parking:
        try:
            df = pd.read_csv(arquivo, sep=";")
            df['saving_mes_clean'] = df['Savings ($/mes)'].apply(clean_numeric) if 'Savings ($/mes)' in df.columns else 0.0
            df['saving_hr_clean'] = df['Savings ($/hr)'].apply(clean_numeric) if 'Savings ($/hr)' in df.columns else 0.0
            df['valor_realized'] = df.apply(
                lambda r: r['saving_mes_clean'] if r['saving_mes_clean'] > 0 else r['saving_hr_clean'] * 720, axis=1
            )
            df['parsed_time'] = pd.to_datetime(df['Date'], errors='coerce')
            lista_parking.append(df)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo {os.path.basename(arquivo)}: {e}")
            
    if lista_potencial:
        df_pot_total = pd.concat(lista_potencial, ignore_index=True)
        df_pot_total = df_pot_total[df_pot_total['valor_final'] > 0]
        df_pot_total['category'] = df_pot_total['category'].fillna('Outros')
        df_pot_total['actiontype'] = df_pot_total['actiontype'].fillna('RESIZE')
        df_pot_total['accountName'] = df_pot_total['accountName'].fillna('Contas Gerais')
    else:
        df_pot_total = pd.DataFrame(columns=['valor_final', 'parsed_time', 'category', 'actiontype', 'accountName', 'entityname', 'entitytype'])
        
    if lista_parking:
        df_park_total = pd.concat(lista_parking, ignore_index=True)
    else:
        df_park_total = pd.DataFrame(columns=['valor_realized', 'parsed_time', 'Action Type'])
        
    return df_pot_total, df_park_total

# Inicialização da coleta de dados
df_pot_total, df_park_total = carregar_dados_da_estrutura(CAMINHO_BASE)

# Botão de Logout posicionado na barra lateral recolhida
if st.sidebar.button("🚪 Sair do Sistema"):
    st.session_state.autenticado = False
    st.session_state.email_usuario = ""
    st.rerun()

# 5. Painel de Controle de Tempo do NOC
ctrl_col1, ctrl_col2 = st.columns(2)

with ctrl_col1:
    st.markdown("**Mês de Análise**")
    meses_disponiveis = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    mes_nome = st.segmented_control(
        "Mês", meses_disponiveis, default="Maio", label_visibility="collapsed"
    )
    meses_map = {m: i+1 for i, m in enumerate(meses_disponiveis)}
    mes_selecionado = meses_map[mes_nome]

with ctrl_col2:
    st.markdown("**Ano de Operação**")
    ano_selecionado = st.segmented_control(
        "Ano", [2025, 2026], default=2026, label_visibility="collapsed"
    )

# Filtros Temporais Dinâmicos
if not df_pot_total.empty and 'parsed_time' in df_pot_total.columns:
    df_pot = df_pot_total[
        (df_pot_total['parsed_time'].dt.year == ano_selecionado) & 
        (df_pot_total['parsed_time'].dt.month == mes_selecionado)
    ]
    if df_pot.empty: df_pot = df_pot_total
else:
    df_pot = df_pot_total

if not df_park_total.empty and 'parsed_time' in df_park_total.columns:
    df_park = df_park_total[
        (df_park_total['parsed_time'].dt.year == ano_selecionado) & 
        (df_park_total['parsed_time'].dt.month == mes_selecionado)
    ]
    if df_park.empty: df_park = df_park_total
else:
    df_park = df_park_total

# 6. Renderização do Cabeçalho Superior Fixo (Mostrando Usuário Logado)
st.markdown(f"""
    <div class="header-container">
        <div class="header-title">IBM TURBONOMIC & CLOUDABILITY — EXECUTIVE COCKPIT</div>
        <div class="company-badge">EMPRESA: XP | USER: {st.session_state.email_usuario}</div>
    </div>
""", unsafe_allow_html=True)

# 7. Exibição Estatística de Impacto Financeiro (Cards Superiores)
total_potential = df_pot['valor_final'].sum() if 'valor_final' in df_pot.columns else 0.0
total_realized = df_park['valor_realized'].sum() if 'valor_realized' in df_park.columns else 0.0

st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">Potential Saving (Oportunidades Identificadas)</div>
            <div class="kpi-value-potential">US$ {total_potential:,.2f}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Realized Saving (Economia Executada / Parking)</div>
            <div class="kpi-value-realized">US$ {total_realized:,.2f}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# 8. Grid de Caixas Gráficas do Dashboard

# LINHA 1
row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    st.markdown('<div class="chart-box"><div class="chart-title">1. Evolução de Oportunidades ($)</div>', unsafe_allow_html=True)
    if not df_pot_total.empty and 'parsed_time' in df_pot_total.columns:
        df_trend = df_pot_total.copy()
        df_trend['Período'] = df_trend['parsed_time'].dt.strftime('%m/%Y')
        df_trend = df_trend.groupby('Período')['valor_final'].sum().reset_index(name='Economia')
        df_trend = df_trend.sort_values(by='Período')
        
        fig1 = px.area(df_trend, x='Período', y='Economia', template='plotly_dark', markers=True)
        fig1.update_traces(line_color='#00F0FF', fillcolor='rgba(0, 240, 255, 0.15)')
    else:
        fig1 = go.Figure()
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig1, width='stretch', config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with row1_col2:
    st.markdown('<div class="chart-box"><div class="chart-title">2. Distribuição por Categoria</div>', unsafe_allow_html=True)
    if not df_pot.empty and 'category' in df_pot.columns:
        df_cat = df_pot.groupby('category')['valor_final'].sum().reset_index(name='Impacto')
        fig2 = px.pie(df_cat, values='Impacto', names='category', hole=0.6, template='plotly_dark',
                      color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'])
    else:
        fig2 = go.Figure()
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280, 
                      margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", yanchor="bottom", y=-0.1, x=0.0))
    st.plotly_chart(fig2, width='stretch', config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with row1_col3:
    st.markdown('<div class="chart-box"><div class="chart-title">3. Eficiência de Desligamento (Parking)</div>', unsafe_allow_html=True)
    if not df_park.empty and 'Action Type' in df_park.columns:
        total_p = len(df_park)
        susp_p = len(df_park[df_park['Action Type'] == 'SUSPEND'])
        pct_parking = (susp_p / total_p * 100) if total_p > 0 else 0.0
    else:
        pct_parking = 0.0
        
    fig3 = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = pct_parking,
        number = {'suffix': "%", 'font': {'color': '#FFFFFF', 'size': 38}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
            'bar': {'color': "#10B981"},
            'bgcolor': "#1F2937",
            'borderwidth': 1,
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [50, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
            ],
        }
    ))
    fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', template='plotly_dark', height=280, margin=dict(l=20, r=20, t=20, b=10))
    st.plotly_chart(fig3, width='stretch', config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# LINHA 2
row2_col1, row2_col2 = st.columns([1, 2])

with row2_col1:
    st.markdown('<div class="chart-box"><div class="chart-title">4. Volumetria de Recomendações</div>', unsafe_allow_html=True)
    if not df_pot.empty and 'actiontype' in df_pot.columns:
        df_actions = df_pot['actiontype'].value_counts().reset_index(name='Qtd')
        fig4 = px.bar(df_actions, x='Qtd', y='actiontype', orientation='h', template='plotly_dark',
                      color='Qtd', color_continuous_scale=['#1E3A8A', '#00F0FF'])
    else:
        fig4 = go.Figure()
    fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False, height=300, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig4, width='stretch', config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with row2_col2:
    st.markdown('<div class="chart-box"><div class="chart-title">5. Impacto por Assinatura / Conta</div>', unsafe_allow_html=True)
    if not df_pot.empty and 'accountName' in df_pot.columns:
        df_stacked = df_pot.groupby(['accountName', 'category'])['valor_final'].sum().reset_index(name='Economia')
        top_accounts = df_pot['accountName'].value_counts().head(5).index
        df_stacked = df_stacked[df_stacked['accountName'].isin(top_accounts)]
        
        fig5 = px.bar(df_stacked, x='accountName', y='Economia', color='category', template='plotly_dark',
                      color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'])
    else:
        fig5 = go.Figure()
    fig5.update_layout(barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, 
                      margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2, x=0.0),
                      xaxis_title=None, yaxis_title="Impacto Mensal ($)")
    st.plotly_chart(fig5, width='stretch', config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# LINHA 3 (Ativos Críticos)
st.markdown('<div class="chart-box" style="margin-bottom: 5px;"><div class="chart-title">6. Detalhamento de Ativos Críticos</div>', unsafe_allow_html=True)
if not df_pot.empty:
    df_table = df_pot[['entityname', 'entitytype', 'actiontype', 'category', 'valor_final']].copy()
    df_table.columns = ['Nome do Ativo', 'Tipo', 'Ação Sugerida', 'Categoria', 'Impacto Mensal ($)']
    st.dataframe(
        df_table.sort_values(by='Impacto Mensal ($)', ascending=False).head(6),
        width='stretch',
        hide_index=True
    )
else:
    st.markdown("<p style='text-align:center; color:#94A3B8;'>Nenhum ativo crítico identificado.</p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 9. Sistema de Atualização em Background Sem Loop (NOC/TV mode)
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 180:
    st.session_state.last_refresh = time.time()
    st.rerun()
