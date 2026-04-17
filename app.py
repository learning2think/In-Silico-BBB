"""
app.py — главная точка входа Streamlit-приложения In Silico BBB.

Запуск:
    streamlit run app.py

Вкладки приложения
------------------
  📊 Результаты       — симуляция транспорта, метрики, график, экспорт CSV.
  🔬 Чувствительность — веерный анализ влияния одного параметра на динамику.
  📐 Модель           — математическая постановка и численный метод.
  ℹ️ О проекте        — актуальность, новизна, планы развития УМНИК.

Реестр веществ (7 соединений):
  Диазепам, Верапамил, Декстран, Кофеин, Морфин, Донепезил, Леветирацетам.
"""

import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from dataclasses import replace

from bbb.core.simulator import Simulator, SimulationParams
from bbb.data.substances import SUBSTANCES
from bbb.visualization.plots import (
    plot_concentrations,
    plot_concentrations_interactive,
    plot_sensitivity_interactive,
)

# ---------------------------------------------------------------------------
# Конфигурация страницы
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="In Silico BBB — Цифровой двойник ГЭБ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Пользовательские стили
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ── App background ──────────────────────────────────────────── */
    .stApp { background-color: #ECF1FA; }

    /* ── Sidebar — deep navy ─────────────────────────────────────── */
    section[data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #1A2B4A 0%, #162340 100%);
        border-right: 1px solid #2A3F61;
    }
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #B8CCE0 !important;
        font-size: 0.85rem !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #2A3F61 !important;
        opacity: 1 !important;
    }

    /* ── Metric cards ────────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #C7D8F0;
        border-top: 3px solid #2563EB;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 3px 14px rgba(37, 99, 235, 0.11);
    }
    [data-testid="stMetricLabel"] > div {
        color: #374151 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stMetricValue"] > div {
        color: #1A2B4A !important;
        font-weight: 700 !important;
    }

    /* ── Tabs ────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 4px;
        gap: 2px;
        border: 1px solid #C7D8F0;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.07);
        margin-bottom: 0.6rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px;
        color: #374151 !important;
        font-weight: 500;
        padding: 0.4rem 1rem;
    }
    .stTabs [aria-selected="true"][data-baseweb="tab"] {
        background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.30) !important;
    }

    /* ── Primary buttons ─────────────────────────────────────────── */
    [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
        border: none !important;
        box-shadow: 0 3px 12px rgba(37, 99, 235, 0.38) !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        letter-spacing: 0.02em !important;
    }
    [data-testid="baseButton-primary"]:hover {
        box-shadow: 0 5px 18px rgba(37, 99, 235, 0.55) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Tab panel — white card ─────────────────────────────────── */
    [role="tabpanel"] {
        background: #FFFFFF;
        border-radius: 0 0 12px 12px;
        padding: 1.4rem 1.6rem 0.8rem;
        border: 1px solid #C7D8F0;
        border-top: none;
        margin-top: -3px;
    }

    /* ── Markdown text — main content ────────────────────────────── */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        color: #1E293B;
    }
    [data-testid="stMarkdownContainer"] td,
    [data-testid="stMarkdownContainer"] th {
        color: #1E293B !important;
    }
    [data-testid="stMarkdownContainer"] th {
        background: #EEF2FF !important;
        font-weight: 600 !important;
    }
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        color: #1A2B4A;
    }
    [data-testid="stMarkdownContainer"] strong {
        color: #1A2B4A;
    }
    [data-testid="stMarkdownContainer"] code {
        color: #1D4ED8;
        background: #EEF2FF;
        padding: 0.1em 0.35em;
        border-radius: 4px;
    }

    /* KaTeX math — dark text ────────────────────────────────────── */
    .katex { color: #1E293B !important; }

    /* ── Sidebar — restore light text (overrides global rules) ───── */
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #D1DCE8 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
        color: #F0F6FF !important;
    }

    /* ── Alert/info boxes ────────────────────────────────────────── */
    [data-testid="stAlertContainer"] p {
        color: #1E293B !important;
    }

    /* ── Caption ─────────────────────────────────────────────────── */
    [data-testid="stCaptionContainer"] p {
        color: #4B5563 !important;
    }

    /* ── Footer ──────────────────────────────────────────────────── */
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def _build_csv(
    result,
    params: SimulationParams,
    substance_name: str,
    kp_uu: float,
) -> bytes:
    """
    Сформировать читаемый CSV с метаданными в заголовке.
    BOM (\ufeff) обеспечивает корректное открытие в Excel без перекодировки.
    """
    import textwrap
    ratio = np.where(
        result.c_blood > 1e-12,
        result.c_brain / result.c_blood,
        np.nan,
    )
    kp_level = (
        "Высокая" if kp_uu >= 0.8
        else "Умеренная" if kp_uu >= 0.3
        else "Низкая"
    )
    header = textwrap.dedent(f"""\
        # ============================================================
        # In Silico BBB — результаты симуляции транспорта через ГЭБ
        # ============================================================
        # Вещество         : {substance_name}
        # ------------------------------------------------------------
        # Параметры модели
        #   k_pass          : {params.k_pass:.4f}  [1/ч]
        #   Vmax (P-gp)     : {params.vmax:.4f}  [мкМ/ч]
        #   Km   (P-gp)     : {params.km:.4f}   [мкМ]
        #   k_elim          : {params.k_elim:.4f}  [1/ч]
        #   C0 в крови      : {params.c0_blood:.4f}  [мкМ]
        #   Время симуляции : {params.t_end:.1f}    [ч]
        # ------------------------------------------------------------
        # Ключевые результаты
        #   Cmax мозг       : {result.c_brain_max:.6f}  [мкМ]
        #   t(Cmax) мозг    : {result.t_brain_max:.2f}      [ч]
        #   AUC мозг        : {result.auc_brain:.4f}   [мкМ·ч]
        #   Kp,uu           : {kp_uu:.4f}   [{kp_level} проницаемость]
        # ============================================================
        #
    """)
    df = pd.DataFrame({
        "t [ч]":                  np.round(result.t, 4),
        "C_blood [мкМ]":          np.round(result.c_blood, 6),
        "C_brain [мкМ]":          np.round(result.c_brain, 6),
        "C_brain / C_blood":      np.round(ratio, 4),
    })
    csv_body = df.to_csv(index=False)
    return ("\ufeff" + header + csv_body).encode("utf-8")


def _render_conclusion(
    kp_uu: float,
    c_brain_max: float,
    auc_brain: float,
    t_brain_max: float,
    params: SimulationParams,
) -> None:
    """
    Вывести компактную карточку заключения о проницаемости вещества.

    Классификация по Kp,uu:
      - Kp,uu ≥ 0.8 → высокая проницаемость
      - 0.3 ≤ Kp,uu < 0.8 → умеренная проницаемость
      - Kp,uu < 0.3 → низкая проницаемость
    """
    if kp_uu >= 0.8:
        level        = "🟢 Высокая проницаемость"
        border_color = "#16A34A"
        bg_gradient  = "linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)"
        shadow_color = "rgba(22, 163, 74, 0.15)"
        pgp_note     = "P-gp эффлюкс минимален или отсутствует."
        verdict = (
            "Вещество свободно проникает через ГЭБ — концентрации "
            "в мозге и крови близки к равновесию. "
            "Пассивная диффузия доминирует над активным выведением. "
            "Ожидается хорошая ЦНС-активность при терапевтических дозах."
        )
    elif kp_uu >= 0.3:
        level        = "🟡 Умеренная проницаемость"
        border_color = "#EA580C"
        bg_gradient  = "linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%)"
        shadow_color = "rgba(234, 88, 12, 0.15)"
        pgp_note     = "P-gp эффлюкс частично ограничивает накопление."
        verdict = (
            "Вещество проникает через ГЭБ с ограничениями. "
            "Умеренный P-gp эффлюкс снижает равновесное накопление в мозге. "
            "ЦНС-активность возможна при достаточной дозе. "
            "Ингибирование P-gp может существенно повысить экспозицию."
        )
    else:
        level        = "🔴 Низкая проницаемость"
        border_color = "#DC2626"
        bg_gradient  = "linear-gradient(135deg, #FFF1F2 0%, #FFE4E6 100%)"
        shadow_color = "rgba(220, 38, 38, 0.15)"
        pgp_note     = "Выраженный P-gp эффлюкс и/или барьерный эффект."
        verdict = (
            "Вещество практически не проникает через ГЭБ. "
            "Выраженный P-gp эффлюкс и/или низкая пассивная проницаемость "
            "критически ограничивают накопление в ткани мозга. "
            "ЦНС-мишени недостижимы при стандартных режимах дозирования."
        )

    pgp_sat = ""
    if params.vmax > 0:
        sat_pct = c_brain_max / (params.km + c_brain_max) * 100
        pgp_sat = f"насыщение P-gp при Cmax ≈ {sat_pct:.0f}%"

    st.markdown(
        f"""
        <div style="
            background: {bg_gradient};
            border-left: 5px solid {border_color};
            border-radius: 0 12px 12px 0;
            padding: 1rem 1.2rem 0.9rem;
            box-shadow: 0 3px 12px {shadow_color};
            height: 100%;
            box-sizing: border-box;
        ">
          <!-- Заголовок уровня -->
          <div style="font-size:1rem; font-weight:700; color:#1A2B4A;
                      margin-bottom:0.55rem">{level}</div>

          <!-- Ключевые метрики в сетке 2×2 -->
          <div style="display:grid; grid-template-columns:1fr 1fr;
                      gap:0.35rem 0.8rem; margin-bottom:0.6rem">
            <div style="background:rgba(255,255,255,0.65); border-radius:7px;
                        padding:0.3rem 0.55rem">
              <div style="font-size:0.72rem; color:#6B7280">Kp,uu (мозг/кровь)</div>
              <div style="font-size:1.05rem; font-weight:700;
                          color:#1A2B4A">{kp_uu:.3f}</div>
            </div>
            <div style="background:rgba(255,255,255,0.65); border-radius:7px;
                        padding:0.3rem 0.55rem">
              <div style="font-size:0.72rem; color:#6B7280">Cmax мозг</div>
              <div style="font-size:1.05rem; font-weight:700;
                          color:#1A2B4A">{c_brain_max:.4f} мкМ</div>
            </div>
            <div style="background:rgba(255,255,255,0.65); border-radius:7px;
                        padding:0.3rem 0.55rem">
              <div style="font-size:0.72rem; color:#6B7280">AUC мозг</div>
              <div style="font-size:1.05rem; font-weight:700;
                          color:#1A2B4A">{auc_brain:.2f} мкМ·ч</div>
            </div>
            <div style="background:rgba(255,255,255,0.65); border-radius:7px;
                        padding:0.3rem 0.55rem">
              <div style="font-size:0.72rem; color:#6B7280">t(Cmax)</div>
              <div style="font-size:1.05rem; font-weight:700;
                          color:#1A2B4A">{t_brain_max:.1f} ч</div>
            </div>
          </div>

          <!-- Параметры модели в одну строку -->
          <div style="font-size:0.76rem; color:#6B7280; margin-bottom:0.55rem;
                      background:rgba(255,255,255,0.5); border-radius:7px;
                      padding:0.25rem 0.55rem; line-height:1.7">
            k<sub>pass</sub>&nbsp;<b style="color:#374151">{params.k_pass:.3f}</b>&ensp;
            V<sub>max</sub>&nbsp;<b style="color:#374151">{params.vmax:.2f}</b>&ensp;
            K<sub>m</sub>&nbsp;<b style="color:#374151">{params.km:.1f}</b>&ensp;
            k<sub>elim</sub>&nbsp;<b style="color:#374151">{params.k_elim:.2f}</b>
            {("&ensp;·&ensp;" + pgp_sat) if pgp_sat else ""}
          </div>

          <!-- Вывод -->
          <div style="border-top:1px solid rgba(0,0,0,0.09);
                      padding-top:0.5rem; color:#1A202C;
                      font-size:0.82rem; line-height:1.55">
            <span style="font-weight:600">Вывод:&nbsp;</span>{verdict}
          </div>
          <div style="margin-top:0.35rem; font-size:0.76rem; color:#6B7280">
            ⚡ {pgp_note}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Заголовок — Hero-баннер
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #1A237E 0%, #1565C0 45%, #0097A7 100%);
        padding: 2.2rem 2.8rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.6rem;
        color: white;
        box-shadow: 0 8px 32px rgba(26, 35, 126, 0.28);
    ">
      <div style="font-size:2.1rem; font-weight:800; letter-spacing:-0.02em;
                  margin-bottom:0.4rem; text-shadow: 0 2px 8px rgba(0,0,0,0.2);">
        🧠 In Silico BBB
      </div>
      <div style="font-size:1.05rem; opacity:0.93; margin-bottom:1.2rem;
                  font-weight:500; letter-spacing:0.01em;">
        Цифровой двойник гематоэнцефалического барьера &nbsp;·&nbsp;
        Проект УМНИК
      </div>
      <div style="display:flex; gap:0.8rem; flex-wrap:wrap; font-size:0.83rem;">
        <span style="background:rgba(255,255,255,0.18); padding:0.25rem 0.75rem;
                     border-radius:20px;">📐 2-компартментная ОДУ-модель</span>
        <span style="background:rgba(255,255,255,0.18); padding:0.25rem 0.75rem;
                     border-radius:20px;">🔬 7 верифицированных веществ</span>
        <span style="background:rgba(255,255,255,0.18); padding:0.25rem 0.75rem;
                     border-radius:20px;">📊 Анализ чувствительности</span>
        <span style="background:rgba(255,255,255,0.18); padding:0.25rem 0.75rem;
                     border-radius:20px;">⬇ Экспорт CSV</span>
        <span style="background:rgba(255,255,255,0.18); padding:0.25rem 0.75rem;
                     border-radius:20px;">✅ 17 автотестов</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Боковая панель управления
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        "<div style='font-size:1.05rem; font-weight:700; color:#FFFFFF;"
        "margin-bottom:0.3rem'>⚙️ Параметры симуляции</div>",
        unsafe_allow_html=True,
    )

    # --- Выбор вещества ---
    st.markdown("**Вещество**")
    substance_names = list(SUBSTANCES.keys())
    selected_name = st.selectbox(
        "Выберите из реестра:",
        options=substance_names,
        index=0,
        label_visibility="collapsed",
    )
    substance = SUBSTANCES[selected_name]

    st.info(
        f"**{substance.name}**\n\n"
        f"{substance.description}\n\n"
        f"*Источник: {substance.reference}*"
    )

    st.divider()

    # --- Параметры транспорта ---
    st.markdown("**Параметры транспорта**")

    k_pass = st.slider(
        "k_pass — пассивная проницаемость [1/ч]",
        min_value=0.001, max_value=2.0,
        value=float(substance.k_pass),
        step=0.001, format="%.3f",
        help=(
            "Коэффициент пассивной диффузии через мембрану ГЭБ. "
            "Высокие значения характерны для липофильных молекул."
        ),
    )

    vmax = st.slider(
        "Vmax — максимальная скорость P-gp [мкМ/ч]",
        min_value=0.0, max_value=10.0,
        value=float(substance.vmax),
        step=0.05, format="%.2f",
        help=(
            "Максимальная скорость эффлюкса P-гликопротеина. "
            "0 = вещество не является субстратом P-gp."
        ),
    )

    km = st.slider(
        "Km — константа Михаэлиса [мкМ]",
        min_value=0.1, max_value=100.0,
        value=float(substance.km),
        step=0.1, format="%.1f",
        help=(
            "Концентрация в мозге, при которой скорость P-gp = Vmax/2. "
            "Малые Km означают высокое сродство транспортёра."
        ),
    )

    st.divider()

    # --- Начальные условия и системный клиренс ---
    st.markdown("**Начальные условия**")

    c0_blood = st.number_input(
        "C₀ в крови [мкМ]",
        min_value=0.01, max_value=100.0,
        value=1.0, step=0.1, format="%.2f",
        help="Начальная концентрация вещества в кровяном компартменте.",
    )

    t_end = st.slider(
        "Время симуляции [ч]",
        min_value=1, max_value=72, value=24, step=1,
        help="Длительность моделирования.",
    )

    st.divider()

    # --- Системный клиренс (in vivo режим) ---
    st.markdown("**Фармакокинетика крови**")

    k_elim = st.slider(
        "k_elim — системный клиренс [1/ч]",
        min_value=0.0, max_value=2.0,
        value=0.0, step=0.01, format="%.2f",
        help=(
            "Константа элиминации из крови (k_elim = CL / V_blood): "
            "моделирует печёночный и почечный клиренс. "
            "0 = закрытая система (режим in vitro)."
        ),
    )

    st.divider()

    # --- Поправка на связывание с белками ---
    with st.expander("🔗 Связывание с белками (fu)"):
        st.caption(
            "Свободные (несвязанные) фракции для расчёта истинного Kp,uu. "
            "Значения по умолчанию — литературные данные для выбранного вещества."
        )
        fu_plasma = st.slider(
            "fu_plasma — своб. фракция в плазме",
            min_value=0.01, max_value=1.0,
            value=float(substance.fu_plasma),
            step=0.01, format="%.2f",
            help="Доля несвязанного вещества в плазме крови (1.0 = нет связывания).",
        )
        fu_brain = st.slider(
            "fu_brain — своб. фракция в мозге",
            min_value=0.01, max_value=1.0,
            value=float(substance.fu_brain),
            step=0.01, format="%.2f",
            help="Доля несвязанного вещества в ткани мозга (1.0 = нет связывания).",
        )

    st.divider()

    run_button = st.button(
        "▶ Запустить расчёт",
        type="primary",
        width="stretch",
    )

# ---------------------------------------------------------------------------
# Вкладки основного контента
# ---------------------------------------------------------------------------

tab_results, tab_sensitivity, tab_model, tab_about = st.tabs(
    ["📊 Результаты", "🔬 Чувствительность", "📐 Модель", "ℹ️ О проекте"]
)

# ---- Вкладка «Результаты» -------------------------------------------------

with tab_results:
    if run_button or "last_result" in st.session_state:
        if run_button:
            params = SimulationParams(
                k_pass=k_pass,
                vmax=vmax,
                km=km,
                c0_blood=c0_blood,
                c0_brain=0.0,
                t_end=float(t_end),
                v_blood=1.0,
                v_brain=0.3,
                n_points=600,
                k_elim=k_elim,
            )
            with st.spinner("Выполняется численное интегрирование..."):
                simulator = Simulator()
                result = simulator.run(params)

            st.session_state["last_result"]    = result
            st.session_state["last_params"]    = params
            st.session_state["last_substance"] = selected_name
            st.session_state["last_fu_plasma"] = fu_plasma
            st.session_state["last_fu_brain"]  = fu_brain

        result              = st.session_state["last_result"]
        params              = st.session_state["last_params"]
        substance_name_used = st.session_state.get("last_substance", selected_name)
        _fu_plasma          = st.session_state.get("last_fu_plasma", fu_plasma)
        _fu_brain           = st.session_state.get("last_fu_brain",  fu_brain)

        if not result.success:
            st.error(f"Решатель завершился с ошибкой: {result.message}")
        else:
            # --- Метрики ---
            n_tail = max(int(len(result.t) * 0.05), 1)
            c_blood_tail = result.c_blood[-n_tail:].mean()
            c_brain_tail = result.c_brain[-n_tail:].mean()
            # Kp,uu с поправкой на несвязанные фракции (истинное равновесие)
            kp_uu = (c_brain_tail * _fu_brain) / max(
                c_blood_tail * _fu_plasma, 1e-12
            )

            col1, col2, col3, col4 = st.columns(4)
            col1.metric(
                "Cmax в мозге",
                f"{result.c_brain_max:.4f} мкМ",
                help="Максимальная концентрация в мозговом компартменте.",
            )
            col2.metric(
                "AUC в мозге",
                f"{result.auc_brain:.2f} мкМ·ч",
                help="Площадь под кривой концентрация-время в мозге.",
            )
            col3.metric(
                "Kp,uu",
                f"{kp_uu:.3f}",
                help=(
                    "Отношение несвязанных концентраций мозг/кровь "
                    "в квазиравновесии (скорр. на fu_brain/fu_plasma). "
                    "Kp,uu < 1 — активный эффлюкс или барьерный эффект."
                ),
            )
            col4.metric(
                "t(Cmax)",
                f"{result.t_brain_max:.1f} ч",
                help="Время достижения максимальной концентрации в мозге.",
            )

            # --- График + Заключение рядом ---
            _slug = substance_name_used.replace(" ", "_")
            _time = f"{params.t_end:.0f}h"

            fig_interactive = plot_concentrations_interactive(
                result=result,
                substance_name=substance_name_used,
                blood_color="#DC2626",
                brain_color="#2563EB",
                show_auc=True,
            )
            # matplotlib fig used only for PNG export
            fig = plot_concentrations(
                result=result,
                substance_name=substance_name_used,
                blood_color="#DC2626",
                brain_color="#2563EB",
                show_auc=True,
            )

            col_plot, col_conc = st.columns([3, 2], gap="medium")

            with col_plot:
                st.plotly_chart(fig_interactive, width="stretch")
                # Кнопки экспорта под графиком
                exp_c1, exp_c2 = st.columns(2)
                with exp_c1:
                    st.download_button(
                        label="⬇ CSV",
                        data=_build_csv(result, params, substance_name_used, kp_uu),
                        file_name=f"bbb_{_slug}_{_time}.csv",
                        mime="text/csv",
                        width="stretch",
                    )
                with exp_c2:
                    _png_buf = io.BytesIO()
                    fig.savefig(_png_buf, format="png", dpi=150, bbox_inches="tight")
                    _png_buf.seek(0)
                    st.download_button(
                        label="🖼 PNG",
                        data=_png_buf,
                        file_name=f"bbb_{_slug}_{_time}.png",
                        mime="image/png",
                        width="stretch",
                    )

            with col_conc:
                st.markdown(
                    "<div style='font-size:0.9rem; font-weight:700; color:#1A2B4A;"
                    " margin-bottom:0.4rem'>📋 Заключение о проницаемости</div>",
                    unsafe_allow_html=True,
                )
                _render_conclusion(
                    kp_uu,
                    result.c_brain_max,
                    result.auc_brain,
                    result.t_brain_max,
                    params,
                )

            plt.close(fig)

            # --- Сравнение всех веществ ---
            with st.expander("📊 Сравнить все вещества при текущих условиях"):
                st.caption(
                    f"Каждое вещество запускается с собственными параметрами "
                    f"транспорта, но при C₀ = {c0_blood:.2f} мкМ, "
                    f"t = {t_end} ч, k_elim = {k_elim:.2f} 1/ч."
                )
                _cmp_sim = Simulator()
                _cmp_rows = []
                for _sname, _sub in SUBSTANCES.items():
                    _p = SimulationParams(
                        k_pass=_sub.k_pass, vmax=_sub.vmax, km=_sub.km,
                        c0_blood=c0_blood, t_end=float(t_end),
                        v_blood=1.0, v_brain=0.3, n_points=300,
                        k_elim=k_elim,
                    )
                    _r = _cmp_sim.run(_p)
                    if _r.success:
                        _nt = max(int(len(_r.t) * 0.05), 1)
                        _kp = (_r.c_brain[-_nt:].mean() * _sub.fu_brain) / max(
                            _r.c_blood[-_nt:].mean() * _sub.fu_plasma, 1e-12
                        )
                        _cmp_rows.append({
                            "Вещество": _sname,
                            "Cmax мозг [мкМ]": f"{_r.c_brain_max:.4f}",
                            "AUC мозг [мкМ·ч]": f"{_r.auc_brain:.2f}",
                            "Kp,uu": f"{_kp:.3f}",
                            "t(Cmax) [ч]": f"{_r.t_brain_max:.1f}",
                        })
                _df_cmp = pd.DataFrame(_cmp_rows)
                _df_cmp = _df_cmp.sort_values("Kp,uu", ascending=False).reset_index(drop=True)
                st.dataframe(_df_cmp, width="stretch", hide_index=True)

    else:
        st.markdown(
            """
            <div style="
                background: white;
                border: 2px dashed #93C5FD;
                border-radius: 16px;
                padding: 3.5rem 2rem;
                text-align: center;
                margin-top: 1rem;
                box-shadow: 0 2px 12px rgba(37, 99, 235, 0.07);
            ">
              <div style="font-size:3.5rem; margin-bottom:0.8rem">🧪</div>
              <div style="font-size:1.1rem; font-weight:700;
                          margin-bottom:0.5rem; color:#1A2B4A">
                Симуляция ещё не запущена
              </div>
              <div style="font-size:0.9rem; margin-bottom:1.5rem; color:#6B7280">
                Выберите вещество в боковой панели и нажмите
                <b style="color:#2563EB">▶ Запустить расчёт</b>
              </div>
              <div style="display:flex; justify-content:center; gap:1.2rem;
                          flex-wrap:wrap; font-size:0.84rem; color:#9CA3AF;">
                <span>① Выберите вещество</span>
                <span>→</span>
                <span>② Настройте параметры</span>
                <span>→</span>
                <span>③ Нажмите ▶ Запустить расчёт</span>
                <span>→</span>
                <span>④ Изучите результаты</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---- Вкладка «Чувствительность» ------------------------------------------

@st.fragment
def _sensitivity_tab() -> None:
    st.markdown("#### Анализ чувствительности параметров модели")
    st.caption(
        "Варьируйте один параметр при фиксированных остальных, "
        "чтобы оценить его влияние на кинетику транспорта."
    )

    sv_c1, sv_c2, sv_c3, sv_c4 = st.columns(4)
    with sv_c1:
        sv_substance_name = st.selectbox(
            "Вещество", list(SUBSTANCES.keys()), key="sv_sub"
        )
        sv_sub = SUBSTANCES[sv_substance_name]
    with sv_c2:
        sv_param_label = st.selectbox(
            "Варьируемый параметр",
            ["k_pass [1/ч]", "Vmax [мкМ/ч]", "Km [мкМ]"],
            key="sv_par",
        )
    with sv_c3:
        sv_compartment = st.selectbox(
            "Компартмент",
            ["Мозг", "Кровь"],
            key="sv_comp",
        )
    with sv_c4:
        sv_n = st.slider("Число кривых", 3, 9, 5, key="sv_n")

    _sv_map = {
        "k_pass [1/ч]": ("k_pass", "1/ч",   sv_sub.k_pass, 0.001, 2.0),
        "Vmax [мкМ/ч]": ("vmax",   "мкМ/ч", sv_sub.vmax,   0.0,   10.0),
        "Km [мкМ]":     ("km",     "мкМ",   sv_sub.km,     0.1,   100.0),
    }
    sv_field, sv_unit, sv_base, sv_min_abs, sv_max_abs = _sv_map[sv_param_label]

    sv_def_min = float(round(max(sv_base * 0.1, sv_min_abs), 4)) if sv_base > 0 else sv_min_abs
    sv_def_max = float(round(min(sv_base * 5.0, sv_max_abs), 4)) if sv_base > 0 else sv_max_abs * 0.3

    sv_r1, sv_r2, sv_r3, sv_r4 = st.columns(4)
    with sv_r1:
        sv_min = st.number_input(
            f"Мин. {sv_unit}", value=sv_def_min,
            min_value=sv_min_abs, max_value=sv_max_abs,
            format="%.4f", key="sv_min",
        )
    with sv_r2:
        sv_max_val = st.number_input(
            f"Макс. {sv_unit}", value=sv_def_max,
            min_value=sv_min_abs, max_value=sv_max_abs,
            format="%.4f", key="sv_max",
        )
    with sv_r3:
        sv_c0 = st.number_input(
            "C₀ в крови [мкМ]", value=1.0,
            min_value=0.01, max_value=100.0, format="%.2f", key="sv_c0",
        )
    with sv_r4:
        sv_tend = st.slider("Время [ч]", 1, 72, 24, key="sv_tend")

    run_sv = st.button(
        "▶ Запустить анализ чувствительности",
        type="primary", width="stretch", key="btn_sv",
    )

    # Зона результатов — всегда занимает место, чтобы избежать прыжка страницы
    results_area = st.container()

    if run_sv:
        sv_values = np.linspace(sv_min, sv_max_val, sv_n).tolist()
        sv_base_params = SimulationParams(
            k_pass=sv_sub.k_pass,
            vmax=sv_sub.vmax,
            km=sv_sub.km,
            c0_blood=sv_c0,
            t_end=float(sv_tend),
            v_blood=1.0,
            v_brain=0.3,
            n_points=400,
        )
        sv_simulator = Simulator()
        sv_results   = []
        sv_progress  = st.progress(0, text="Запуск симуляций...")
        for i, val in enumerate(sv_values):
            sv_p = replace(sv_base_params, **{sv_field: val})
            sv_results.append(sv_simulator.run(sv_p))
            sv_progress.progress(
                (i + 1) / sv_n,
                text=f"Симуляция {i + 1} / {sv_n}",
            )
        sv_progress.empty()

        st.session_state["sv_results"]     = sv_results
        st.session_state["sv_values"]      = sv_values
        st.session_state["sv_field"]       = sv_field
        st.session_state["sv_unit"]        = sv_unit
        st.session_state["sv_sub_name"]    = sv_substance_name
        st.session_state["sv_compartment"] = sv_compartment

    with results_area:
        if "sv_results" in st.session_state:
            _sv_comp_key = st.session_state.get("sv_compartment", "Мозг")
            _sv_comp_arg = "brain" if _sv_comp_key == "Мозг" else "blood"
            fig_sv = plot_sensitivity_interactive(
                results=st.session_state["sv_results"],
                param_values=st.session_state["sv_values"],
                param_name=st.session_state["sv_field"],
                param_unit=st.session_state["sv_unit"],
                substance_name=st.session_state["sv_sub_name"],
                compartment=_sv_comp_arg,
            )
            st.plotly_chart(fig_sv, width="stretch")

            sv_rows = []
            for val, res in zip(
                st.session_state["sv_values"], st.session_state["sv_results"]
            ):
                n_t = max(int(len(res.t) * 0.05), 1)
                kp  = res.c_brain[-n_t:].mean() / max(
                    res.c_blood[-n_t:].mean(), 1e-12
                )
                sv_rows.append({
                    f"{st.session_state['sv_field']}"
                    f" [{st.session_state['sv_unit']}]": f"{val:.4g}",
                    "Cmax мозг [мкМ]":   f"{res.c_brain_max:.4f}",
                    "AUC мозг [мкМ·ч]":  f"{res.auc_brain:.2f}",
                    "Kp,uu":             f"{kp:.3f}",
                })
            st.dataframe(pd.DataFrame(sv_rows), width="stretch", hide_index=True)
        else:
            st.info(
                "Настройте параметры выше и нажмите "
                "**▶ Запустить анализ чувствительности**."
            )


with tab_sensitivity:
    _sensitivity_tab()

# ---- Вкладка «Модель» ----------------------------------------------------

with tab_model:
    st.markdown(
        r"""
        ## Математическая модель

        ### Компартменты

        Система состоит из двух хорошо перемешанных компартментов:

        | Компартмент | Обозначение | Объём (усл. ед.) |
        |---|---|---|
        | Кровь (апикальный) | $C_\text{blood}$ | $V_\text{blood} = 1.0$ |
        | Мозг (базолатеральный) | $C_\text{brain}$ | $V_\text{brain} = 0.3$ |

        ### Транспортные потоки

        **1. Пассивная диффузия** (закон Фика):
        $$J_\text{diff} = k_\text{pass} \cdot (C_\text{blood} - C_\text{brain})$$

        **2. Активный эффлюкс P-gp** (Михаэлис–Ментен):
        $$J_\text{P-gp} = \frac{V_\text{max} \cdot C_\text{brain}}{K_m + C_\text{brain}}$$

        ### Система ОДУ

        $$\frac{dC_\text{blood}}{dt} = -J_\text{diff} + \frac{V_\text{brain}}{V_\text{blood}} \cdot J_\text{P-gp}$$

        $$\frac{dC_\text{brain}}{dt} = \frac{V_\text{blood}}{V_\text{brain}} \cdot J_\text{diff} - J_\text{P-gp}$$

        Коэффициенты объёмов обеспечивают **закон сохранения вещества**:
        количество молекул, покидающих один компартмент, в точности равно
        числу молекул, поступающих в другой.

        ### Численный метод

        Система решается методом **LSODA** (`scipy.integrate.solve_ivp`).
        LSODA автоматически переключается между схемами Adams (нежёсткие участки)
        и BDF (жёсткие участки) — оптимальный выбор при неизвестной жёсткости,
        характерной при малых значениях $K_m$ и высоких концентрациях.
        Точность: `rtol=1e-8`, `atol=1e-10`.

        ### Параметры модели

        | Параметр | Обозначение | Единицы | Диапазон |
        |---|---|---|---|
        | Пассивная проницаемость | $k_\text{pass}$ | 1/ч | 0.001 – 2.0 |
        | Макс. скорость P-gp | $V_\text{max}$ | мкМ/ч | 0.0 – 10.0 |
        | Константа Михаэлиса | $K_m$ | мкМ | 0.1 – 100 |

        ### Выходные показатели

        | Показатель | Описание |
        |---|---|
        | **C_brain(t)** | Кинетика концентрации в мозге [мкМ] |
        | **Cmax** | Максимальная концентрация в мозге [мкМ] |
        | **AUC** | Площадь под кривой в мозге (метод трапеций) [мкМ·ч] |
        | **Kp,uu** | Среднее C_brain / C_blood за последние 5 % времени |
        """
    )

# ---- Вкладка «О проекте» -------------------------------------------------

with tab_about:
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown(
            """
            ## О проекте «In Silico BBB»

            **In Silico BBB** — вычислительная платформа с открытым исходным кодом
            для механистического моделирования транспорта лекарственных веществ через
            гематоэнцефалический барьер (ГЭБ).

            **Программа:** УМНИК (Фонд содействия инновациям)

            ---

            ### Актуальность

            Разработка препаратов для лечения заболеваний ЦНС — одна из наиболее
            сложных задач фармацевтики: около **98% малых молекул** не проникают
            через ГЭБ в терапевтических концентрациях.

            Экспериментальные методы оценки проницаемости (PAMPA-BBB, клеточные
            монослои MDCK-MDR1) трудоёмки и дорогостоящи.
            Вычислительные модели позволяют предварительно ранжировать соединения
            и сократить число неинформативных экспериментов.

            ---

            ### Научная новизна

            * **Механистическая кинетика** — временна́я динамика, а не только
              бинарный прогноз «проникает / не проникает».
            * **Активный транспорт** — явный учёт P-gp (Михаэлис–Ментен).
            * **Клинические метрики** — Kp,uu, Cmax, AUC.
            * **Открытая архитектура** — лёгкое добавление новых транспортёров
              (BCRP, MRP4) и компартментов.
            """
        )

    with col_r:
        st.markdown(
            """
            ### Планы развития

            **Этап 1 — год 1**
            - QSAR-блок: предсказание k_pass из структуры молекулы
              (RDKit-дескрипторы, случайный лес).
            - Транспортёры BCRP и MRP4.
            - Реестр 50+ верифицированных веществ.

            **Этап 2 — год 2**
            - Трёхкомпартментная модель (Transwell / PAMPA).
            - REST API для пакетного скрининга.
            - Валидация на PET-данных.

            **Долгосрочная перспектива**
            - Интеграция с молекулярным докингом (AutoDock, Glide).
            - Персонализированная PBPK-модель.

            ---

            ### Стек

            | Слой | Технология |
            |---|---|
            | UI | Streamlit 1.56 |
            | ОДУ-решатель | scipy LSODA |
            | Графики | matplotlib 3.10 |
            | Данные | numpy · pandas |
            | Тесты | pytest 9 |
            | Python | 3.13 |
            """
        )

# ---------------------------------------------------------------------------
# Подвал
# ---------------------------------------------------------------------------

st.markdown(
    """
    <hr style="border:none; border-top:1px solid #C7D8F0; margin-top:2.5rem">
    <p style="text-align:center; color:#6B7280; font-size:0.8rem;
              margin-bottom:0.6rem; line-height:1.8">
      In Silico BBB &nbsp;·&nbsp; Проект УМНИК &nbsp;·&nbsp;
      Python 3.13 · scipy LSODA · Streamlit
    </p>
    """,
    unsafe_allow_html=True,
)
