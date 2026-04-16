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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from dataclasses import replace

from bbb.core.simulator import Simulator, SimulationParams
from bbb.data.substances import SUBSTANCES
from bbb.visualization.plots import plot_concentrations, plot_parameter_sensitivity

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
    /* Фон приложения */
    .stApp { background-color: #F8FAFC; }

    /* Метрики — карточки с тенью */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.07);
    }

    /* Боковая панель */
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #F1F5F9;
    }

    /* Убрать стандартный footer */
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def _render_conclusion(
    kp_uu: float,
    c_brain_max: float,
    params: SimulationParams,
) -> None:
    """
    Вывести стилизованную карточку заключения о проницаемости вещества.

    Классификация по Kp,uu (отношение концентраций мозг/кровь в равновесии):
      - Kp,uu ≥ 0.8 → высокая проницаемость
      - 0.3 ≤ Kp,uu < 0.8 → умеренная проницаемость
      - Kp,uu < 0.3 → низкая проницаемость (выраженный эффлюкс или барьер)

    Параметры
    ---------
    kp_uu : float
        Отношение концентраций мозг/кровь в квазиравновесии.
    c_brain_max : float
        Максимальная концентрация в мозге [мкМ].
    params : SimulationParams
        Параметры симуляции (для отображения в карточке).
    """
    if kp_uu >= 0.8:
        level        = "🟢 Высокая"
        border_color = "#2E7D32"
        verdict = (
            "Вещество хорошо проникает через ГЭБ. Концентрации в мозге "
            "и крови приближаются к равновесию. Активный эффлюкс слабый "
            "или отсутствует."
        )
    elif kp_uu >= 0.3:
        level        = "🟡 Умеренная"
        border_color = "#E65100"
        verdict = (
            "Вещество частично проникает через ГЭБ. Наблюдается умеренный "
            "P-gp эффлюкс, снижающий накопление в ткани мозга."
        )
    else:
        level        = "🔴 Низкая"
        border_color = "#B71C1C"
        verdict = (
            "Вещество плохо проникает через ГЭБ. Выраженный P-gp эффлюкс "
            "и/или низкая пассивная проницаемость существенно ограничивают "
            "концентрацию в ткани мозга."
        )

    st.markdown(
        f"""
        <div style="
            background: #FFFFFF;
            border-left: 5px solid {border_color};
            border-radius: 0 12px 12px 0;
            padding: 1.2rem 1.6rem;
            box-shadow: 0 1px 5px rgba(15,23,42,0.07);
            margin-top: 0.6rem;
        ">
          <table style="width:100%; border-collapse:collapse; margin-bottom:0.8rem">
            <tr>
              <td style="padding:5px 12px 5px 0; color:#546E7A;
                         font-size:0.82rem; width:50%">Уровень проницаемости</td>
              <td style="padding:5px 0; font-weight:700">{level}</td>
            </tr>
            <tr>
              <td style="padding:5px 12px 5px 0; color:#546E7A; font-size:0.82rem">
                Kp,uu (мозг/кровь)</td>
              <td style="padding:5px 0; font-weight:600; color:#0D47A1">
                {kp_uu:.3f}</td>
            </tr>
            <tr>
              <td style="padding:5px 12px 5px 0; color:#546E7A; font-size:0.82rem">
                Cmax в мозге</td>
              <td style="padding:5px 0; font-weight:600; color:#0D47A1">
                {c_brain_max:.4f} мкМ</td>
            </tr>
            <tr>
              <td style="padding:5px 12px 5px 0; color:#90A4AE; font-size:0.78rem">
                k_pass</td>
              <td style="padding:5px 0; color:#546E7A; font-size:0.82rem">
                {params.k_pass:.3f} 1/ч</td>
            </tr>
            <tr>
              <td style="padding:5px 12px 5px 0; color:#90A4AE; font-size:0.78rem">
                Vmax (P-gp)</td>
              <td style="padding:5px 0; color:#546E7A; font-size:0.82rem">
                {params.vmax:.2f} мкМ/ч</td>
            </tr>
            <tr>
              <td style="padding:5px 12px 5px 0; color:#90A4AE; font-size:0.78rem">
                Km (P-gp)</td>
              <td style="padding:5px 0; color:#546E7A; font-size:0.82rem">
                {params.km:.1f} мкМ</td>
            </tr>
          </table>
          <div style="border-top:1px solid #EEF2F7; padding-top:0.8rem;
                      color:#37474F; font-size:0.88rem; line-height:1.5">
            <b>Вывод:</b> {verdict}
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
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 55%, #00838F 100%);
        padding: 1.8rem 2.5rem 1.6rem;
        border-radius: 14px;
        margin-bottom: 1.4rem;
        color: white;
    ">
      <div style="font-size:1.9rem; font-weight:800; letter-spacing:-0.01em;
                  margin-bottom:0.35rem;">
        🧠 In Silico BBB
      </div>
      <div style="font-size:1rem; opacity:0.88; margin-bottom:1rem;">
        Цифровой двойник гематоэнцефалического барьера &nbsp;·&nbsp;
        Проект УМНИК
      </div>
      <div style="display:flex; gap:1.6rem; flex-wrap:wrap;
                  font-size:0.82rem; opacity:0.75;">
        <span>📐 2-компартментная ОДУ-модель</span>
        <span>🔬 7 верифицированных веществ</span>
        <span>📊 Анализ чувствительности</span>
        <span>⬇ Экспорт CSV</span>
        <span>✅ 17 автотестов</span>
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
        "<div style='font-size:1.05rem; font-weight:700; color:#0D47A1;"
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

    # --- Начальные условия ---
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

    run_button = st.button(
        "▶ Запустить расчёт",
        type="primary",
        use_container_width=True,
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
            )
            with st.spinner("Выполняется численное интегрирование..."):
                simulator = Simulator()
                result = simulator.run(params)

            st.session_state["last_result"]    = result
            st.session_state["last_params"]    = params
            st.session_state["last_substance"] = selected_name

        result              = st.session_state["last_result"]
        params              = st.session_state["last_params"]
        substance_name_used = st.session_state.get("last_substance", selected_name)

        if not result.success:
            st.error(f"Решатель завершился с ошибкой: {result.message}")
        else:
            # --- Метрики ---
            n_tail = max(int(len(result.t) * 0.05), 1)
            kp_uu = result.c_brain[-n_tail:].mean() / max(
                result.c_blood[-n_tail:].mean(), 1e-12
            )

            col1, col2, col3 = st.columns(3)
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
                    "в квазиравновесии. Kp,uu < 1 — активный эффлюкс."
                ),
            )

            st.markdown("")

            # --- График ---
            fig = plot_concentrations(
                result=result,
                substance_name=substance_name_used,
                blood_color="#E53935",
                brain_color="#1565C0",
                show_auc=True,
            )
            st.pyplot(fig)
            plt.close(fig)

            # --- Экспорт данных ---
            df_export = pd.DataFrame({
                "t [ч]":         result.t,
                "C_blood [мкМ]": result.c_blood,
                "C_brain [мкМ]": result.c_brain,
            })
            st.download_button(
                label="⬇ Скачать данные (CSV)",
                data=df_export.to_csv(index=False).encode("utf-8"),
                file_name=(
                    f"bbb_{substance_name_used.replace(' ', '_')}"
                    f"_{params.t_end:.0f}h.csv"
                ),
                mime="text/csv",
            )

            # --- Заключение ---
            st.markdown("#### 📋 Заключение о проницаемости")
            _render_conclusion(kp_uu, result.c_brain_max, params)

    else:
        st.markdown(
            """
            <div style="
                background: white;
                border: 2px dashed #CBD5E0;
                border-radius: 14px;
                padding: 3rem 2rem;
                text-align: center;
                color: #64748B;
                margin-top: 1rem;
            ">
              <div style="font-size:3rem; margin-bottom:0.8rem">🧪</div>
              <div style="font-size:1.05rem; font-weight:600;
                          margin-bottom:0.4rem; color:#334155">
                Симуляция ещё не запущена
              </div>
              <div style="font-size:0.88rem; margin-bottom:1.5rem; opacity:0.8">
                Выберите вещество в боковой панели и нажмите
                <b>▶ Запустить расчёт</b>
              </div>
              <div style="display:flex; justify-content:center; gap:1.2rem;
                          flex-wrap:wrap; font-size:0.82rem; opacity:0.65;">
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

with tab_sensitivity:
    st.markdown("#### Анализ чувствительности параметров модели")
    st.caption(
        "Варьируйте один параметр при фиксированных остальных, "
        "чтобы оценить его влияние на кинетику транспорта."
    )

    sv_c1, sv_c2, sv_c3 = st.columns(3)
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
        type="primary", use_container_width=True, key="btn_sv",
    )

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

        st.session_state["sv_results"]  = sv_results
        st.session_state["sv_values"]   = sv_values
        st.session_state["sv_field"]    = sv_field
        st.session_state["sv_unit"]     = sv_unit
        st.session_state["sv_sub_name"] = sv_substance_name

    if "sv_results" in st.session_state:
        fig_sv = plot_parameter_sensitivity(
            results=st.session_state["sv_results"],
            param_values=st.session_state["sv_values"],
            param_name=st.session_state["sv_field"],
            param_unit=st.session_state["sv_unit"],
            substance_name=st.session_state["sv_sub_name"],
            compartment="brain",
        )
        st.pyplot(fig_sv)
        plt.close(fig_sv)

        # Сводная таблица метрик
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
        st.dataframe(pd.DataFrame(sv_rows), use_container_width=True, hide_index=True)
    else:
        st.info(
            "Настройте параметры выше и нажмите "
            "**▶ Запустить анализ чувствительности**."
        )

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
    <hr style="border:none; border-top:1px solid #E2E8F0; margin-top:2.5rem">
    <p style="text-align:center; color:#94A3B8; font-size:0.78rem;
              margin-bottom:0.6rem; line-height:1.8">
      In Silico BBB &nbsp;·&nbsp; Проект УМНИК &nbsp;·&nbsp;
      Python 3.13 · scipy LSODA · Streamlit
    </p>
    """,
    unsafe_allow_html=True,
)
