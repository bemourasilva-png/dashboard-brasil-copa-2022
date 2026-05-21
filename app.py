# =============================================================================
# DASHBOARD v2.0: Conversão ou Desperdício? — Copa do Mundo 2022
# Engenharia de Analytics Sênior | Processo Seletivo — Ciência de Dados no Futebol
# =============================================================================
# Arquitetura: Streamlit + Plotly Go | Dark Mode Premium (identidade visual Seleção)
# Pipeline: Pandas com períodos customizados, remoção de pênaltis e nomes populares
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import os

# ─────────────────────────────────────────────
# CONFIGURAÇÃO GLOBAL DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Brasil · Análise Ofensiva Copa 2022",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# DESIGN SYSTEM — TOKENS DE COR (Seleção Brasileira · Dark Mode Premium)
# ─────────────────────────────────────────────
BG_APP      = "#0B111E"   # Azul Noturno Ultra Escuro — fundo da aplicação
BG_CARD     = "#162238"   # Azul de Berlim Fosco — fundo dos cards
BG_CARD2    = "#1C2D4A"   # Variante hover/detalhe
COLOR_XG    = "#00E676"   # Verde Esmeralda Vibrante — métrica teórica xG
COLOR_GOLS  = "#FFD700"   # Amarelo Ouro Seleção — fato real / gols
COLOR_TEXT  = "#FFFFFF"   # Branco Puro — texto principal
COLOR_MUTED = "#8A99AD"   # Azul Cinzento Claro — legendas e rótulos
COLOR_ALERT = "#FF4D4D"   # Vermelho Coral — sub-performance / déficit

# ─────────────────────────────────────────────
# MAPEAMENTO DE NOMES POPULARES
# Traduz nomes de registro civil para nomes de transmissão esportiva,
# garantindo legibilidade profissional nos gráficos.
# ─────────────────────────────────────────────
NOMES_POPULARES = {
    "Neymar da Silva Santos Junior":          "Neymar",
    "Carlos Henrique Casimiro":               "Casemiro",
    "Raphael Dias Belloli":                   "Raphinha",
    "Vinícius José Paixão de Oliveira Júnior":"Vinícius Jr.",
    "Thiago Emiliano da Silva":               "Thiago Silva",
    "Richarlison de Andrade":                 "Richarlison",
    "Danilo Luiz da Silva":                   "Danilo",
    "Alex Sandro Lobo Silva":                 "Alex Sandro",
    "Rodrygo Silva de Goes":                  "Rodrygo",
    "Frederico Rodrigues Santos":             "Fred",
    "Antony Matheus dos Santos":              "Antony",
    "Éder Gabriel Militão":                   "Militão",
    "Marcos Aoás Corrêa":                     "Marquinhos",
    "Bruno Guimarães Rodriguez Moura":        "Bruno Guimarães",
    "Lucas Tolentino Coelho de Lima":         "Lucas Paquetá",
    "Pedro Guilherme Abreu dos Santos":       "Pedro",
    "Daniel Alves da Silva":                  "Daniel Alves",
    "Gleison Bremer Silva Nascimento":        "Bremer",
    "Gabriel Teodoro Martinelli Silva":       "Martinelli",
    "Gabriel Fernando de Jesus":              "Gabriel Jesus",
}

# ─────────────────────────────────────────────
# INJEÇÃO DE CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
    /* ── Reset e Fundo ── */
    .stApp, [data-testid="stAppViewContainer"] {{
        background-color: {BG_APP};
        color: {COLOR_TEXT};
    }}
    [data-testid="stHeader"] {{ background: transparent; }}
    section[data-testid="stSidebar"] {{ background-color: {BG_CARD}; }}

    /* ── Tipografia Global ── */
    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        color: {COLOR_TEXT};
    }}

    /* ── Header Hero ── */
    .hero-wrapper {{
        background: linear-gradient(135deg, #0d1a2e 0%, #0f2040 60%, #0B111E 100%);
        border-radius: 16px;
        padding: 36px 40px 30px 40px;
        margin-bottom: 28px;
        border: 1px solid rgba(255,215,0,0.10);
        position: relative;
        overflow: hidden;
    }}
    .hero-wrapper::before {{
        content: '';
        position: absolute;
        top: -80px; right: -80px;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(255,215,0,0.05) 0%, transparent 65%);
        border-radius: 50%;
    }}
    .hero-wrapper::after {{
        content: '';
        position: absolute;
        bottom: -40px; left: 40%;
        width: 200px; height: 200px;
        background: radial-gradient(circle, rgba(0,230,118,0.04) 0%, transparent 65%);
        border-radius: 50%;
    }}
    .hero-badge {{
        display: inline-block;
        background: rgba(255,215,0,0.10);
        color: {COLOR_GOLS};
        border: 1px solid rgba(255,215,0,0.30);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 14px;
    }}
    .hero-title {{
        font-size: 28px;
        font-weight: 900;
        letter-spacing: -0.8px;
        line-height: 1.15;
        color: {COLOR_TEXT};
        margin: 0 0 10px 0;
    }}
    .hero-title span {{
        color: {COLOR_GOLS};
    }}
    .hero-subtitle {{
        font-size: 14px;
        color: {COLOR_MUTED};
        margin: 0;
        line-height: 1.6;
        max-width: 680px;
    }}

    /* ── Cards de KPI ── */
    .kpi-card {{
        background: {BG_CARD};
        border-radius: 12px;
        padding: 20px 24px;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(255,215,0,0.07);
    }}
    .kpi-label {{
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: {COLOR_MUTED};
        margin-bottom: 10px;
    }}
    .kpi-value {{
        font-size: 40px;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 6px;
    }}
    .kpi-delta {{
        font-size: 12px;
        font-weight: 500;
        color: {COLOR_MUTED};
        margin-top: 6px;
    }}
    .kpi-delta.negative {{ color: {COLOR_ALERT}; font-weight: 700; }}
    .kpi-delta.positive {{ color: #48BB78; font-weight: 700; }}

    /* ── Section Titles ── */
    .section-title {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: {COLOR_MUTED};
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 18px;
    }}

    /* ── Alert Box ── */
    .alert-box {{
        background: rgba(255,77,77,0.07);
        border: 1px solid rgba(255,77,77,0.30);
        border-left: 4px solid {COLOR_ALERT};
        border-radius: 8px;
        padding: 12px 18px;
        margin-top: 10px;
        font-size: 13px;
        color: {COLOR_ALERT};
        font-weight: 600;
        line-height: 1.5;
    }}

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] > div > div {{
        background-color: {BG_CARD} !important;
        border: 1px solid rgba(255,215,0,0.20) !important;
        border-radius: 8px !important;
        color: {COLOR_TEXT} !important;
    }}
    [data-testid="stSelectbox"] label {{
        color: {COLOR_MUTED} !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }}

    /* ── File Uploader ── */
    [data-testid="stFileUploader"] {{
        background: {BG_CARD};
        border: 2px dashed rgba(255,215,0,0.20);
        border-radius: 12px;
        padding: 20px;
    }}
    [data-testid="stFileUploader"] label {{ color: {COLOR_MUTED} !important; }}

    /* ── Divisor ── */
    hr {{ border-color: rgba(255,255,255,0.05); }}

    /* ── Upload Screen ── */
    .upload-screen {{
        text-align: center;
        padding: 80px 20px;
    }}

    /* ── Plotly ── */
    [data-testid="stPlotlyChart"] {{
        border-radius: 12px;
        overflow: hidden;
    }}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# PIPELINE DE ENGENHARIA DE DADOS
# =============================================================================

@st.cache_data(show_spinner=False)
def load_and_process(file_bytes: bytes) -> pd.DataFrame:
    """
    Pipeline principal de tratamento de dados.
    Ordem: leitura → parsing de tempo → períodos → remoção pênaltis → nomes → labels.
    """

    # ── 1. LEITURA ──────────────────────────────────────────────────────────
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name="Dados", header=0)

    # ── 2. PARSING DO CRONÔMETRO ─────────────────────────────────────────────
    # Converte 'HH:MM:SS.mmm' → timedelta → total_seconds() para comparações ordinais.
    df["tempo_td"]  = pd.to_timedelta(df["tempo_de_jogo"])
    df["tempo_sec"] = df["tempo_td"].dt.total_seconds()

    # ── 3. ALGORITMO DE PERÍODOS DE JOGO (Feature Engineering Customizado) ──
    #
    # O cronômetro reinicia em 00:00:00 no início do 2º Tempo e da Prorrogação.
    # Detectamos "quebras cronológicas" comparando cada linha com a anterior DENTRO
    # do mesmo jogo (group por time_01 + time_02).
    # Quando tempo_atual < tempo_anterior → reset → novo bloco cronológico.
    #
    # Bloco 0 → '1º Tempo' | Bloco 1 → '2º Tempo' | Bloco 2/3 → 'Prorrogação'

    def assign_period(group: pd.DataFrame) -> pd.Series:
        """
        Usa cumsum() sobre flags de reset para criar índices de bloco por partida.
        Robusto para qualquer número de reinícios (regular + prorrogação).
        """
        reset_flag = group["tempo_sec"] < group["tempo_sec"].shift(1).fillna(0)
        block_idx  = reset_flag.cumsum()
        return block_idx.map({
            0: "1º Tempo",
            1: "2º Tempo",
            2: "Prorrogação",
            3: "Prorrogação",
        }).fillna("Prorrogação")

    df["periodo_jogo"] = df.groupby(
        ["time_01", "time_02"], group_keys=False
    ).apply(assign_period)

    # ── 4. REMOÇÃO DA DISPUTA DE PÊNALTIS DA CROÁCIA ─────────────────────────
    #
    # xG = 0.7835 é o marcador canônico StatsBomb para qualquer cobrança de pênalti.
    # MANTER: pênalti do Neymar vs Coreia do Sul (~12min) — gol válido em jogo.
    # REMOVER: disputa pós-prorrogação vs Croácia — não compõe o tempo de jogo.
    #
    # Estratégia: interseção de 3 condições precisas:
    #   1. Jogo = Croácia vs Brasil
    #   2. xG == 0.7835 (pênalti canônico)
    #   3. tempo_sec < 360s — pênaltis da disputa ocorrem nos primeiros minutos
    #      após o reset do árbitro; nenhum pênalti em jogo ocorreu < 6min nesta partida.

    mask_shootout = (
        (df["time_01"] == "Croatia") &
        (df["time_02"] == "Brazil") &
        (df["finalizacao_xg_statsbomb"].round(4) == 0.7835) &
        (df["tempo_sec"] < 360)
    )
    df = df[~mask_shootout].copy()

    # ── 5. PADRONIZAÇÃO DOS NOMES POPULARES ─────────────────────────────────
    # Substitui nomes de registro civil pelos nomes de transmissão esportiva.
    # Garante legibilidade profissional nos eixos dos gráficos.
    df["jogador"] = df["jogador"].replace(NOMES_POPULARES)

    # ── 6. LABEL DE PARTIDA (filtros e eixos) ───────────────────────────────
    def build_match_label(row):
        if row["time_01"] == "Brazil":
            return f"Brasil vs {row['time_02']}"
        adversario = row["time_01"]
        traducoes  = {"Croatia": "Croácia", "Cameroon": "Camarões",
                      "Serbia": "Sérvia", "South Korea": "Coreia do Sul",
                      "Switzerland": "Suíça"}
        return f"{traducoes.get(adversario, adversario)} vs Brasil"

    df["partida"] = df.apply(build_match_label, axis=1)

    return df


# =============================================================================
# COMPONENTES DE VISUALIZAÇÃO
# =============================================================================

def plotly_base_layout(title: str = "", height: int = 400) -> dict:
    """Layout padrão do design system dark mode da Seleção."""
    return dict(
        title=dict(
            text=title,
            font=dict(color=COLOR_TEXT, size=13, family="Inter"),
            x=0.01, xanchor="left",
        ),
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        font=dict(color=COLOR_TEXT, family="Inter"),
        height=height,
        margin=dict(l=16, r=16, t=48, b=16),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLOR_MUTED, size=12),
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
        ),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(color=COLOR_MUTED, size=11)),
        yaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(color=COLOR_MUTED, size=11)),
        hoverlabel=dict(
            bgcolor=BG_CARD2,
            bordercolor=COLOR_GOLS,
            font=dict(color=COLOR_TEXT, size=13),
        ),
    )


def grafico_A_contundencia_por_partida(df_brazil: pd.DataFrame) -> go.Figure:
    """
    Gráfico A — Colunas Agrupadas: xG Acumulado vs Gols Reais por Partida.
    Narrativa central: o gap de contundência jogo a jogo.
    """
    agg = df_brazil.groupby("partida").agg(
        xg_total=("finalizacao_xg_statsbomb", "sum"),
        gols=("resultado_finalizacao", lambda x: (x == "Gol").sum()),
    ).reset_index()
    agg = agg.sort_values("xg_total", ascending=False)

    fig = go.Figure()

    # xG — Verde Esmeralda (métrica teórica)
    fig.add_trace(go.Bar(
        name="xG Acumulado",
        x=agg["partida"],
        y=agg["xg_total"].round(2),
        marker=dict(color=COLOR_XG, opacity=0.82, line=dict(width=0)),
        text=agg["xg_total"].round(2),
        textposition="outside",
        textfont=dict(color=COLOR_XG, size=12, family="Inter"),
        hovertemplate="<b>%{x}</b><br>xG: <b>%{y:.2f}</b><extra></extra>",
        width=0.35, offset=-0.2,
    ))

    # Gols — Amarelo Ouro (fato real)
    fig.add_trace(go.Bar(
        name="Gols Marcados",
        x=agg["partida"],
        y=agg["gols"],
        marker=dict(color=COLOR_GOLS, opacity=0.90, line=dict(width=0)),
        text=agg["gols"],
        textposition="outside",
        textfont=dict(color=COLOR_GOLS, size=12, family="Inter"),
        hovertemplate="<b>%{x}</b><br>Gols: <b>%{y}</b><extra></extra>",
        width=0.35, offset=0.2,
    ))

    layout = plotly_base_layout("Contundência por Partida — xG vs Gols Reais", height=400)
    layout["barmode"]           = "overlay"
    layout["xaxis"]["tickangle"] = -18
    layout["yaxis"]["title"]    = dict(text="Valor", font=dict(color=COLOR_MUTED, size=11))

    # Anotação de destaque para Camarões
    cam = agg[agg["partida"].str.contains("Camar")]
    if not cam.empty:
        cam_xg = cam["xg_total"].values[0]
        fig.add_annotation(
            x=cam["partida"].values[0], y=cam_xg + 0.22,
            text=f"⚠ {cam_xg:.2f} xG · 0 gols",
            showarrow=True, arrowhead=2, arrowcolor=COLOR_ALERT,
            ax=0, ay=-44,
            font=dict(color=COLOR_ALERT, size=11, family="Inter"),
            bgcolor="rgba(255,77,77,0.10)",
            bordercolor=COLOR_ALERT, borderwidth=1, borderpad=4,
        )

    fig.update_layout(**layout)
    return fig


def grafico_B_eficiencia_individual(df_brazil: pd.DataFrame) -> go.Figure:
    """
    Gráfico B — Barras Horizontais: saldo (Gols − xG) dos Top 8 finalizadores.
    Formatação condicional: Amarelo Ouro ≥ 0, Vermelho Coral < 0.
    """
    agg = df_brazil.groupby("jogador").agg(
        xg=("finalizacao_xg_statsbomb", "sum"),
        gols=("resultado_finalizacao", lambda x: (x == "Gol").sum()),
        chutes=("resultado_finalizacao", "count"),
    ).reset_index()
    agg["saldo"] = agg["gols"] - agg["xg"]
    top8 = agg.nlargest(8, "chutes").sort_values("saldo")

    colors = [COLOR_GOLS if s >= 0 else COLOR_ALERT for s in top8["saldo"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top8["saldo"].round(2),
        y=top8["jogador"],
        orientation="h",
        marker=dict(color=colors, opacity=0.88, line=dict(width=0)),
        text=top8["saldo"].apply(lambda v: f"{v:+.2f}"),
        textposition="outside",
        textfont=dict(size=12, family="Inter"),
        hovertemplate="<b>%{y}</b><br>Saldo: <b>%{x:.2f}</b><extra></extra>",
    ))

    fig.add_vline(x=0, line_dash="dot",
                  line_color="rgba(255,255,255,0.20)", line_width=1.5)

    layout = plotly_base_layout("Eficiência Individual — Saldo (Gols − xG)", height=420)
    layout["xaxis"]["title"]  = dict(text="Saldo (Gols − xG)",
                                     font=dict(color=COLOR_MUTED, size=11))
    layout["yaxis"]["tickfont"] = dict(color=COLOR_TEXT, size=12, family="Inter")
    layout["showlegend"]       = False
    layout["margin"]           = dict(l=110, r=60, t=48, b=16)
    fig.update_layout(**layout)
    return fig


def grafico_D_lideres_finalizacao(df_brazil: pd.DataFrame) -> go.Figure:
    """
    Gráfico D — Barras Horizontais: volume absoluto de chutes por jogador (Top 8).
    Verde Esmeralda sólido. Permite comparação imediata com o Gráfico B:
    quem mais chuta vs quem é mais eficiente.
    """
    agg = df_brazil.groupby("jogador").agg(
        chutes=("resultado_finalizacao", "count"),
    ).reset_index()
    top8 = agg.nlargest(8, "chutes").sort_values("chutes")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top8["chutes"],
        y=top8["jogador"],
        orientation="h",
        marker=dict(color=COLOR_XG, opacity=0.82, line=dict(width=0)),
        text=top8["chutes"],
        textposition="outside",
        textfont=dict(color=COLOR_XG, size=12, family="Inter"),
        hovertemplate="<b>%{y}</b><br>Chutes: <b>%{x}</b><extra></extra>",
    ))

    layout = plotly_base_layout("Líderes de Finalizações — Volume Absoluto", height=420)
    layout["xaxis"]["title"]    = dict(text="Total de Chutes",
                                       font=dict(color=COLOR_MUTED, size=11))
    layout["yaxis"]["tickfont"] = dict(color=COLOR_TEXT, size=12, family="Inter")
    layout["showlegend"]        = False
    layout["margin"]            = dict(l=110, r=50, t=48, b=16)
    fig.update_layout(**layout)
    return fig


def grafico_C_volume_temporal(df_brazil: pd.DataFrame) -> go.Figure:
    """
    Gráfico C — Colunas por Período de Jogo.
    Prova a tendência do Brasil de concentrar o volume ofensivo no 2º Tempo.
    """
    ordem = ["1º Tempo", "2º Tempo", "Prorrogação"]
    agg = (df_brazil.groupby("periodo_jogo").size()
           .reindex(ordem).fillna(0).reset_index())
    agg.columns = ["periodo", "finalizacoes"]
    agg = agg[agg["finalizacoes"] > 0]

    pct = agg["finalizacoes"] / agg["finalizacoes"].sum() * 100
    cores_periodo = [COLOR_XG, COLOR_GOLS, COLOR_ALERT][:len(agg)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["periodo"],
        y=agg["finalizacoes"],
        marker=dict(color=cores_periodo, opacity=0.85, line=dict(width=0)),
        text=[f"{int(v)}  ({p:.0f}%)" for v, p in zip(agg["finalizacoes"], pct)],
        textposition="outside",
        textfont=dict(color=COLOR_TEXT, size=12, family="Inter"),
        hovertemplate="<b>%{x}</b><br>Finalizações: <b>%{y}</b><extra></extra>",
        width=0.45,
    ))

    layout = plotly_base_layout("Volume Ofensivo por Período de Jogo", height=360)
    layout["yaxis"]["title"] = dict(text="Nº de Finalizações",
                                    font=dict(color=COLOR_MUTED, size=11))
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


def render_kpi_card(label: str, value: str, color: str,
                    delta: str = "", delta_type: str = "neutral"):
    """Renderiza um card de KPI estilizado em HTML puro."""
    delta_class = {"negative": "negative", "positive": "positive"}.get(delta_type, "")
    delta_html  = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color:{color}">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# APLICAÇÃO PRINCIPAL
# =============================================================================

def main():

    # ── SIDEBAR: Upload ou carregamento automático ───────────────────────────
    with st.sidebar:
        st.markdown(
            f"<div style='color:{COLOR_GOLS};font-weight:700;font-size:11px;"
            f"letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;'>"
            f"⚙ Fonte de Dados</div>",
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "CARREGAR ARQUIVO",
            type=["xlsx", "xls"],
            help="Arquivo Excel com aba 'Dados' no schema StatsBomb",
        )
        st.markdown(
            f"<div style='color:{COLOR_MUTED};font-size:11px;margin-top:10px;"
            f"line-height:1.7'>Aba esperada: <b>Dados</b><br>"
            f"Colunas: time_01, time_02, tempo_de_jogo,<br>"
            f"time_evento, jogador, finalizacao_xg_statsbomb,<br>"
            f"resultado_finalizacao</div>",
            unsafe_allow_html=True,
        )

    # ── RESOLUÇÃO DA FONTE DE DADOS ──────────────────────────────────────────
    # Prioridade 1: arquivo carregado pelo usuário via uploader
    # Prioridade 2: arquivo na mesma pasta do script (modo apresentação offline)
    file_bytes = None

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
    else:
        # Tenta carregar automaticamente o arquivo da mesma pasta do app.py
        script_dir    = os.path.dirname(os.path.abspath(__file__))
        auto_path     = os.path.join(script_dir,
                            "Processo_Seletivo_-_Visualização_de_Dados.xlsx")
        if os.path.exists(auto_path):
            with open(auto_path, "rb") as f:
                file_bytes = f.read()

    # ── TELA DE BOAS-VINDAS (nenhuma fonte disponível) ───────────────────────
    if file_bytes is None:
        _, col_c, _ = st.columns([1, 2, 1])
        with col_c:
            st.markdown(f"""
            <div class="upload-screen">
                <div style="font-size:64px;margin-bottom:16px;">🇧🇷</div>
                <div style="display:inline-block;background:rgba(255,215,0,0.10);
                    color:{COLOR_GOLS};border:1px solid rgba(255,215,0,0.30);
                    border-radius:20px;padding:4px 14px;font-size:10px;font-weight:700;
                    letter-spacing:2px;text-transform:uppercase;margin-bottom:14px;">
                    Copa do Mundo · Qatar 2022
                </div>
                <div style="font-size:22px;font-weight:800;color:{COLOR_TEXT};
                    margin-bottom:10px;">Análise Ofensiva — Seleção Brasileira</div>
                <div style="font-size:14px;color:{COLOR_MUTED};max-width:380px;
                    margin:0 auto 28px auto;line-height:1.7;">
                    Faça upload do arquivo <strong>.xlsx</strong> no painel lateral
                    para carregar o dashboard completo.
                </div>
            </div>
            """, unsafe_allow_html=True)
        return

    # ── PROCESSAMENTO ────────────────────────────────────────────────────────
    try:
        df = load_and_process(file_bytes)
    except Exception as e:
        st.error(
            f"**Erro ao processar o arquivo.**\n\n"
            f"Verifique se o Excel contém a aba `Dados` com o schema correto.\n\n"
            f"Detalhe: `{e}`"
        )
        return

    # ── ESCOPO: apenas finalizações do Brasil ────────────────────────────────
    df_brazil = df[df["time_evento"] == "Brazil"].copy()

    # ── HEADER HERO ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-wrapper">
        <div class="hero-badge">🏆 Copa do Mundo · Qatar 2022</div>
        <div class="hero-title">
            CONVERSÃO OU <span>DESPERDÍCIO?</span><br>
            O DIAGNÓSTICO DO ATAQUE DO BRASIL NA COPA
        </div>
        <div class="hero-subtitle">
            Uma análise baseada em Gols Esperados (xG) sobre a falta de contundência
            que custou o Hexa. · Métricas StatsBomb · Engenharia de Períodos Customizada
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── FILTRO DE PARTIDA ────────────────────────────────────────────────────
    col_f, _ = st.columns([2, 5])
    with col_f:
        all_matches    = sorted(df_brazil["partida"].unique().tolist())
        match_options  = ["Todas as Partidas"] + all_matches
        selected_match = st.selectbox(
            "SELECIONAR PARTIDA",
            options=match_options,
            index=0,
            help="Filtra todos os KPIs e gráficos para a partida selecionada",
        )

    # ── APLICAÇÃO DO FILTRO ──────────────────────────────────────────────────
    if selected_match != "Todas as Partidas":
        df_view = df_brazil[df_brazil["partida"] == selected_match].copy()
    else:
        df_view = df_brazil.copy()

    # ── ZONA 1: KPIs ─────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>▸ Indicadores de Desempenho Ofensivo</div>",
                unsafe_allow_html=True)

    finalizacoes     = len(df_view)
    xg_acumulado     = df_view["finalizacao_xg_statsbomb"].sum()
    gols_marcados    = (df_view["resultado_finalizacao"] == "Gol").sum()
    saldo_eficiencia = gols_marcados - xg_acumulado
    n_jogos          = max(df_view["partida"].nunique(), 1)

    col1, col2, col3, col4 = st.columns(4, gap="small")

    with col1:
        render_kpi_card(
            label="Finalizações",
            value=str(finalizacoes),
            color=COLOR_XG,
            delta=f"Média: {finalizacoes / n_jogos:.1f} por jogo",
        )
    with col2:
        render_kpi_card(
            label="xG Acumulado",
            value=f"{xg_acumulado:.2f}",
            color=COLOR_XG,
            delta=f"xG médio/chute: {xg_acumulado / max(finalizacoes, 1):.3f}",
        )
    with col3:
        render_kpi_card(
            label="Gols Marcados",
            value=str(gols_marcados),
            color=COLOR_GOLS,
            delta=f"Taxa de conversão: {gols_marcados / max(finalizacoes, 1) * 100:.1f}%",
        )
    with col4:
        s_color = COLOR_ALERT if saldo_eficiencia < 0 else "#48BB78"
        s_type  = "negative" if saldo_eficiencia < 0 else "positive"
        s_delta = (
            f"⚠ Déficit de contundência: {saldo_eficiencia:.2f}"
            if saldo_eficiencia < 0
            else f"✓ Superávit ofensivo: +{saldo_eficiencia:.2f}"
        )
        render_kpi_card(
            label="Saldo de Eficiência",
            value=f"{saldo_eficiencia:+.2f}",
            color=s_color,
            delta=s_delta,
            delta_type=s_type,
        )

    if saldo_eficiencia < 0:
        campanha = " O valor consolidado da campanha completa é de −2.50." \
                   if selected_match == "Todas as Partidas" else ""
        st.markdown(f"""
        <div class="alert-box">
            ⚠ O Brasil produziu <strong>{xg_acumulado:.2f} xG</strong> mas converteu
            apenas <strong>{gols_marcados} gol(s)</strong> — um déficit de contundência de
            <strong>{abs(saldo_eficiencia):.2f} gols</strong> abaixo da expectativa
            estatística.{campanha}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ZONA 2: GRÁFICOS ─────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>▸ Análise Visual Tática</div>",
                unsafe_allow_html=True)

    # Gráfico A — linha inteira
    fig_a = grafico_A_contundencia_por_partida(df_view)
    st.plotly_chart(fig_a, use_container_width=True,
                    config={"displayModeBar": False})

    # Gráficos B e D — lado a lado
    col_b, col_d = st.columns(2, gap="medium")
    with col_b:
        fig_b = grafico_B_eficiencia_individual(df_view)
        st.plotly_chart(fig_b, use_container_width=True,
                        config={"displayModeBar": False})
    with col_d:
        fig_d = grafico_D_lideres_finalizacao(df_view)
        st.plotly_chart(fig_d, use_container_width=True,
                        config={"displayModeBar": False})

    # Gráfico C — linha inteira
    fig_c = grafico_C_volume_temporal(df_view)
    st.plotly_chart(fig_c, use_container_width=True,
                    config={"displayModeBar": False})

    # ── ZONA 3: TABELA DE DADOS ───────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋  Explorar Dados Brutos", expanded=False):
        cols_show = ["partida", "periodo_jogo", "tempo_de_jogo", "jogador",
                     "finalizacao_xg_statsbomb", "resultado_finalizacao"]
        st.dataframe(
            df_view[cols_show].rename(columns={
                "partida": "Partida", "periodo_jogo": "Período",
                "tempo_de_jogo": "Tempo", "jogador": "Jogador",
                "finalizacao_xg_statsbomb": "xG",
                "resultado_finalizacao": "Resultado",
            }).style.format({"xG": "{:.4f}"}),
            use_container_width=True,
            height=340,
        )

    # ── RODAPÉ ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <hr style="margin-top:40px;margin-bottom:16px;">
    <div style="display:flex;justify-content:space-between;align-items:center;
                flex-wrap:wrap;gap:8px;">
        <div style="color:{COLOR_MUTED};font-size:11px;">
            Métricas xG: <strong style="color:{COLOR_XG}">StatsBomb Open Data</strong> ·
            Desenvolvido com <strong style="color:{COLOR_XG}">
            Python · Pandas · Plotly · Streamlit</strong>
        </div>
        <div style="color:{COLOR_MUTED};font-size:11px;">
            Processo Seletivo · Analista de Dados no Futebol · 2025
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
