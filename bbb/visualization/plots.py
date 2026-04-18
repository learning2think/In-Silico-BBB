"""
plots.py — научные графики результатов симуляции ГЭБ.

Две группы функций:
  - Matplotlib (plot_concentrations, plot_parameter_sensitivity) —
    только для PNG-экспорта через st.download_button.
  - Plotly (plot_concentrations_interactive, plot_sensitivity_interactive) —
    основные интерактивные графики приложения.

Единый визуальный стиль задан через константы и helper-функции:
  _FONT_FAMILY, COLOR_BLOOD, COLOR_BRAIN, _base_layout(), _plotly_axis().
"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import plotly.colors as pc
import plotly.graph_objects as go

from bbb.core.simulator import SimulationResult

matplotlib.use("Agg")

# ---------------------------------------------------------------------------
# Стилевые константы
# ---------------------------------------------------------------------------

_FONT_TITLE = 14
_FONT_LABEL = 12
_FONT_TICK = 10
_LINE_WIDTH = 2.4
_ALPHA_FILL = 0.13

_FIG_W = 10.0
_FIG_H = 5.2

_COLOR_GRID = "#D1D9EC"
_COLOR_SPINE = "#9AABC7"

_FONT_FAMILY = "system-ui, -apple-system, 'Segoe UI', Arial, sans-serif"

# Семантические цвета проекта (используются и в app.py)
COLOR_BLOOD = "#DC2626"  # красный = апикальный / кровь
COLOR_BRAIN = "#2563EB"  # синий   = мозговой компартмент (цель)


# ---------------------------------------------------------------------------
# Вспомогательные функции — matplotlib
# ---------------------------------------------------------------------------


def _style_axes(ax: plt.Axes, fig: plt.Figure) -> None:
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#F5F8FF")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(_COLOR_SPINE)
    ax.spines["bottom"].set_color(_COLOR_SPINE)
    ax.grid(True, linestyle="-", linewidth=0.6, color=_COLOR_GRID, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(
        axis="both",
        which="both",
        labelsize=_FONT_TICK,
        color=_COLOR_SPINE,
        length=4,
    )


# ---------------------------------------------------------------------------
# Вспомогательные функции — Plotly
# ---------------------------------------------------------------------------


def _hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _plotly_axis(title: str) -> dict:
    return dict(
        title=title,
        title_font=dict(size=13, color="rgba(0,0,0,0.85)", family=_FONT_FAMILY),
        tickfont=dict(size=11, family=_FONT_FAMILY, color="rgba(0,0,0,0.80)"),
        gridcolor="rgba(0,0,0,0.06)",
        showgrid=True,
        showline=True,
        linecolor="#C7D4E8",
        linewidth=1,
        mirror=False,
        rangemode="tozero",
        zeroline=False,
    )


def _sensitivity_colors(n: int) -> list[str]:
    """Plasma colorscale средствами Plotly — без зависимости от matplotlib."""
    return pc.sample_colorscale("Plasma", [i / max(n - 1, 1) for i in range(n)])


def _base_layout(title_text: str, height: int = 430) -> dict:
    """Единый базовый layout для всех интерактивных Plotly-графиков."""
    return dict(
        title=dict(
            text=title_text,
            font=dict(size=16, color="#1A2B4A", family=_FONT_FAMILY),
            x=0.0,
            xanchor="left",
            pad=dict(l=0, b=6),
        ),
        font=dict(family=_FONT_FAMILY, size=13, color="rgba(0,0,0,0.85)"),
        xaxis=_plotly_axis("Время, ч"),
        yaxis=_plotly_axis("Концентрация, мкМ"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            y=-0.20,
            x=0,
            font=dict(size=11, family=_FONT_FAMILY, color="rgba(0,0,0,0.80)"),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
        margin=dict(l=40, r=20, t=50, b=70),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="rgba(0,0,0,0.15)",
            font=dict(size=13, color="rgba(0,0,0,0.85)", family=_FONT_FAMILY),
        ),
        height=height,
    )


# ---------------------------------------------------------------------------
# Matplotlib-графики (только для PNG-экспорта)
# ---------------------------------------------------------------------------


def plot_concentrations(
    result: SimulationResult,
    substance_name: str = "Вещество",
    blood_color: str = "#E53935",
    brain_color: str = "#1565C0",
    show_auc: bool = True,
) -> plt.Figure:
    """Строит статичный matplotlib-график концентраций кровь/мозг для PNG-экспорта.

    Args:
        result: Результат симуляции — поля t, c_blood, c_brain, auc_brain.
        substance_name: Название вещества для заголовка графика.
        blood_color: HEX-цвет кривой крови (апикальный компартмент).
        brain_color: HEX-цвет кривой мозга (базолатеральный компартмент).
        show_auc: Если True, закрашивает AUC-область под кривой мозга.

    Returns:
        matplotlib Figure готовый к `fig.savefig()` или `st.download_button`.

    Raises:
        ValueError: если result.t пустой или длины массивов не совпадают.
    """
    fig, ax = plt.subplots(figsize=(_FIG_W, _FIG_H))
    _style_axes(ax, fig)

    ax.plot(
        result.t,
        result.c_blood,
        color=blood_color,
        linewidth=_LINE_WIDTH,
        label="Кровь (апикальный компартмент)",
        zorder=3,
    )
    ax.plot(
        result.t,
        result.c_brain,
        color=brain_color,
        linewidth=_LINE_WIDTH,
        label="Мозг (базолатеральный компартмент)",
        zorder=3,
    )

    if show_auc:
        ax.fill_between(
            result.t,
            result.c_brain,
            alpha=_ALPHA_FILL,
            color=brain_color,
            label=f"AUC (мозг) = {result.auc_brain:.2f} мкМ·ч",
            zorder=2,
        )

    idx_max = int(np.argmax(result.c_brain))
    t_max = result.t[idx_max]
    c_max = result.c_brain[idx_max]
    t_range = result.t[-1]
    t_offset = t_range * 0.06
    xt = t_max - t_offset * 2 if t_max + t_offset > t_range * 0.85 else t_max + t_offset

    ax.annotate(
        f"  Cmax = {c_max:.3f} мкМ\n  t = {t_max:.1f} ч",
        xy=(t_max, c_max),
        xytext=(xt, c_max * 0.83),
        fontsize=9,
        color=brain_color,
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="white",
            edgecolor=brain_color,
            alpha=0.85,
            linewidth=0.8,
        ),
        arrowprops=dict(arrowstyle="->", color=brain_color, lw=1.2),
    )

    ax.set_xlabel("Время, ч", fontsize=_FONT_LABEL, color="#37474F")
    ax.set_ylabel("Концентрация, мкМ", fontsize=_FONT_LABEL, color="#37474F")
    ax.set_title(
        f"Транспорт «{substance_name}» через ГЭБ",
        fontsize=_FONT_TITLE,
        fontweight="bold",
        color="#1A2B4A",
        pad=14,
    )
    ax.set_xlim(left=0.0)
    ax.set_ylim(bottom=0.0)
    ax.legend(
        fontsize=10,
        framealpha=0.95,
        edgecolor="#E2E8F0",
        fancybox=True,
        loc="upper right",
    )
    fig.tight_layout()
    return fig


def plot_parameter_sensitivity(
    results: list[SimulationResult],
    param_values: list[float],
    param_name: str,
    param_unit: str,
    substance_name: str = "Вещество",
    compartment: str = "brain",
    colormap: str = "plasma",
) -> plt.Figure:
    """Строит статичный matplotlib веерный график анализа чувствительности для PNG-экспорта.

    Args:
        results: Список результатов симуляции — по одному на каждое значение параметра.
        param_values: Значения варьируемого параметра (одна кривая на значение).
        param_name: Имя параметра (используется в легенде и заголовке).
        param_unit: Единица измерения параметра.
        substance_name: Название вещества для заголовка.
        compartment: ``"brain"`` или ``"blood"`` — какой компартмент отображать.
        colormap: Имя matplotlib colormap (по умолчанию ``"plasma"``).

    Returns:
        matplotlib Figure готовый к `fig.savefig()` или `st.download_button`.

    Raises:
        ValueError: если `results` и `param_values` имеют разную длину.
    """
    fig, ax = plt.subplots(figsize=(_FIG_W, _FIG_H))
    _style_axes(ax, fig)
    cmap = matplotlib.colormaps[colormap]
    n = len(results)

    for i, (res, val) in enumerate(zip(results, param_values, strict=False)):
        color = cmap(i / max(n - 1, 1))
        y_data = res.c_brain if compartment == "brain" else res.c_blood
        ax.plot(
            res.t,
            y_data,
            color=color,
            linewidth=_LINE_WIDTH,
            label=f"{param_name} = {val:.3g} {param_unit}",
        )

    compartment_label = "Мозг" if compartment == "brain" else "Кровь"
    ax.set_xlabel("Время, ч", fontsize=_FONT_LABEL, color="#37474F")
    ax.set_ylabel("Концентрация, мкМ", fontsize=_FONT_LABEL, color="#37474F")
    ax.set_title(
        f"Чувствительность к «{param_name}» — {substance_name}  |  {compartment_label}",
        fontsize=_FONT_TITLE,
        fontweight="bold",
        color="#1A2B4A",
        pad=14,
    )
    ax.set_xlim(left=0.0)
    ax.set_ylim(bottom=0.0)
    ax.legend(fontsize=9, framealpha=0.95, edgecolor="#E2E8F0", fancybox=True)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Интерактивные Plotly-графики
# ---------------------------------------------------------------------------

_CHART_MARKER = dict(size=5, opacity=0.75, maxdisplayed=40)


def plot_concentrations_interactive(
    result: SimulationResult,
    substance_name: str = "Вещество",
    blood_color: str = COLOR_BLOOD,
    brain_color: str = COLOR_BRAIN,
    show_auc: bool = True,
) -> go.Figure:
    """Строит интерактивный Plotly-график концентраций в обоих компартментах.

    Args:
        result: Результат симуляции — поля t, c_blood, c_brain, auc_brain.
        substance_name: Название вещества для заголовка графика.
        blood_color: HEX-цвет кривой крови (по умолчанию ``COLOR_BLOOD``).
        brain_color: HEX-цвет кривой мозга (по умолчанию ``COLOR_BRAIN``).
        show_auc: Если True, добавляет полупрозрачную AUC-заливку и метку в легенде.

    Returns:
        Plotly Figure готовый к ``st.plotly_chart(fig, config=_CHART_CONFIG)``.

    Raises:
        ValueError: если result.t пустой или c_brain/c_blood имеют несовпадающую длину.
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=result.t,
            y=result.c_blood,
            name="Кровь",
            line=dict(color=blood_color, width=2),
            marker=dict(**_CHART_MARKER, color=blood_color),
            mode="lines+markers",
            hovertemplate="<b>Кровь</b>  %{y:.4f} мкМ<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=result.t,
            y=result.c_brain,
            name="Мозг",
            line=dict(color=brain_color, width=2),
            marker=dict(**_CHART_MARKER, color=brain_color),
            mode="lines+markers",
            hovertemplate="<b>Мозг</b>  %{y:.4f} мкМ<extra></extra>",
        )
    )

    if show_auc:
        fig.add_trace(
            go.Scatter(
                x=result.t,
                y=result.c_brain,
                fill="tozeroy",
                fillcolor=_hex_to_rgba(brain_color, 0.10),
                line=dict(color="rgba(0,0,0,0)"),
                name=f"AUC = {result.auc_brain:.2f} мкМ·ч",
                hoverinfo="skip",
                showlegend=True,
            )
        )

    idx_max = int(np.argmax(result.c_brain))
    t_max = result.t[idx_max]
    c_max = result.c_brain[idx_max]

    fig.add_annotation(
        x=t_max,
        y=c_max,
        text=f"Cmax = {c_max:.3f} мкМ<br>t = {t_max:.1f} ч",
        showarrow=True,
        arrowhead=2,
        arrowcolor=brain_color,
        arrowwidth=1.5,
        bgcolor="white",
        bordercolor=brain_color,
        borderwidth=1,
        font=dict(size=10, color=brain_color, family=_FONT_FAMILY),
        ax=50,
        ay=-45,
    )

    fig.update_layout(**_base_layout(f"Транспорт «{substance_name}» через ГЭБ"))
    return fig


def plot_sensitivity_interactive(
    results: list[SimulationResult],
    param_values: list[float],
    param_name: str,
    param_unit: str,
    substance_name: str = "Вещество",
    compartment: str = "brain",
) -> go.Figure:
    """Строит интерактивный Plotly веерный график анализа чувствительности.

    Каждая кривая соответствует одному значению варьируемого параметра.
    Цвета из Plasma colorscale через `plotly.colors` (без зависимости от matplotlib).
    Легенда вертикальная справа — не перекрывает кривые при 3–9 трассах.

    Args:
        results: Список результатов симуляции — по одному на значение параметра.
        param_values: Значения варьируемого параметра (len == len(results)).
        param_name: Имя параметра для меток легенды и заголовка.
        param_unit: Единица измерения параметра (например, ``"1/ч"``).
        substance_name: Название вещества для заголовка.
        compartment: ``"brain"`` или ``"blood"`` — какой компартмент отображать.

    Returns:
        Plotly Figure готовый к ``st.plotly_chart(fig, config=_CHART_CONFIG)``.

    Raises:
        ValueError: если `results` и `param_values` имеют разную длину.
    """
    fig = go.Figure()
    n = len(results)
    colors = _sensitivity_colors(n)
    _sv_marker = dict(size=4, opacity=0.65, maxdisplayed=20)

    for i, (res, val) in enumerate(zip(results, param_values, strict=False)):
        y_data = res.c_brain if compartment == "brain" else res.c_blood
        label = f"{param_name} = {val:.3g} {param_unit}"

        fig.add_trace(
            go.Scatter(
                x=res.t,
                y=y_data,
                name=label,
                line=dict(color=colors[i], width=2),
                marker=dict(**_sv_marker, color=colors[i]),
                mode="lines+markers",
                hovertemplate=f"<b>{label}</b>  %{{y:.4f}} мкМ<extra></extra>",
            )
        )

    compartment_label = "Мозг" if compartment == "brain" else "Кровь"
    title = (
        f"Чувствительность к «{param_name}» — "
        f"{substance_name}  ·  {compartment_label}"
    )
    layout = _base_layout(title, height=460)
    # Вертикальная легенда справа: кривые могут быть близко, метки длинные
    layout["legend"] = dict(
        orientation="v",
        font=dict(size=10, family=_FONT_FAMILY, color="rgba(0,0,0,0.80)"),
        bgcolor="rgba(255,255,255,0.88)",
        bordercolor="#E2E8F0",
        borderwidth=1,
        x=1.01,
        xanchor="left",
        y=1.0,
        yanchor="top",
    )
    layout["margin"]["r"] = 160  # место для вертикальной легенды
    fig.update_layout(**layout)
    return fig
