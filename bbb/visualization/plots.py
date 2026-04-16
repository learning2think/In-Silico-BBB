"""
Модуль plots — построение научных графиков результатов симуляции ГЭБ.

Визуальный стиль
----------------
Все графики используют единую научную палитру: белый фон, скрытые верхняя
и правая оси, светло-серая сетка. Стиль применяется через вспомогательную
функцию _style_axes(), чтобы каждая функция создавала согласованное
оформление без глобального изменения rcParams.

Все функции возвращают объекты matplotlib Figure, готовые к отображению
в Streamlit через st.pyplot() или к сохранению в файл.
"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from bbb.core.simulator import SimulationResult

# Использовать бэкенд без GUI (обязательно для Streamlit)
matplotlib.use("Agg")

# ---------------------------------------------------------------------------
# Стилевые константы
# ---------------------------------------------------------------------------

_FONT_TITLE  = 14
_FONT_LABEL  = 12
_FONT_TICK   = 10
_FONT_LEGEND = 10
_LINE_WIDTH  = 2.4
_ALPHA_FILL  = 0.13

_FIG_W = 10.0   # ширина фигуры [дюймы]
_FIG_H = 5.2    # высота фигуры [дюймы]

_COLOR_GRID  = "#E8ECEF"   # цвет линий сетки
_COLOR_SPINE = "#B0BEC5"   # цвет осей


# ---------------------------------------------------------------------------
# Вспомогательная функция оформления
# ---------------------------------------------------------------------------

def _style_axes(ax: plt.Axes, fig: plt.Figure) -> None:
    """
    Применить единый научный стиль к осям matplotlib.

    Скрывает верхнюю и правую рамки, делает оставшиеся рамки светлее,
    устанавливает белый фон области графика и мягкую серую сетку.

    Параметры
    ---------
    ax : plt.Axes
        Объект осей для стилизации.
    fig : plt.Figure
        Родительская фигура (устанавливается белый фон).
    """
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFBFC")

    # Убрать верхнюю и правую рамки
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(_COLOR_SPINE)
    ax.spines["bottom"].set_color(_COLOR_SPINE)

    # Мягкая сетка
    ax.grid(True, linestyle="-", linewidth=0.6, color=_COLOR_GRID, zorder=0)
    ax.set_axisbelow(True)

    # Тики — только снизу и слева
    ax.tick_params(
        axis="both", which="both",
        labelsize=_FONT_TICK,
        color=_COLOR_SPINE,
        length=4,
    )


# ---------------------------------------------------------------------------
# Основной график концентраций
# ---------------------------------------------------------------------------

def plot_concentrations(
    result: SimulationResult,
    substance_name: str = "Вещество",
    blood_color: str = "#E53935",
    brain_color: str = "#1565C0",
    show_auc: bool = True,
) -> plt.Figure:
    """
    Построить график изменения концентраций в обоих компартментах.

    На график выводятся:
      - Концентрация в крови (апикальный компартмент)
      - Концентрация в мозге (базолатеральный компартмент)
      - Закрашенная область под кривой мозга (если show_auc=True)
      - Аннотация с Cmax и временем достижения максимума

    Параметры
    ---------
    result : SimulationResult
        Результат симуляции, полученный от Simulator.run().
    substance_name : str
        Название вещества для заголовка графика.
    blood_color : str
        Цвет линии концентрации в крови (HEX).
    brain_color : str
        Цвет линии концентрации в мозге (HEX).
    show_auc : bool
        Показывать ли закрашенную область AUC под кривой мозга.

    Возвращает
    ----------
    matplotlib.figure.Figure
        Готовый к отображению объект Figure.
    """
    fig, ax = plt.subplots(figsize=(_FIG_W, _FIG_H))
    _style_axes(ax, fig)

    # --- Основные линии ---
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

    # --- Закраска области под кривой мозга (AUC) ---
    if show_auc:
        ax.fill_between(
            result.t,
            result.c_brain,
            alpha=_ALPHA_FILL,
            color=brain_color,
            label=f"AUC (мозг) = {result.auc_brain:.2f} мкМ·ч",
            zorder=2,
        )

    # --- Маркер максимума в мозге ---
    idx_max = int(np.argmax(result.c_brain))
    t_max   = result.t[idx_max]
    c_max   = result.c_brain[idx_max]

    # Сдвигаем текст вправо, но если Cmax у правого края — влево,
    # чтобы аннотация не выходила за пределы графика.
    t_range  = result.t[-1]
    t_offset = t_range * 0.06
    xt = t_max - t_offset * 2 if t_max + t_offset > t_range * 0.85 else t_max + t_offset

    ax.annotate(
        f"  Cmax = {c_max:.3f} мкМ\n  t = {t_max:.1f} ч",
        xy=(t_max, c_max),
        xytext=(xt, c_max * 0.83),
        fontsize=9,
        color=brain_color,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor=brain_color, alpha=0.85, linewidth=0.8),
        arrowprops=dict(arrowstyle="->", color=brain_color, lw=1.2),
    )

    # --- Оформление осей ---
    ax.set_xlabel("Время, ч", fontsize=_FONT_LABEL, color="#37474F")
    ax.set_ylabel("Концентрация, мкМ", fontsize=_FONT_LABEL, color="#37474F")
    ax.set_title(
        f"Транспорт «{substance_name}» через ГЭБ",
        fontsize=_FONT_TITLE,
        fontweight="bold",
        color="#0D47A1",
        pad=14,
    )
    ax.set_xlim(left=0.0)
    ax.set_ylim(bottom=0.0)
    ax.legend(
        fontsize=_FONT_LEGEND,
        framealpha=0.95,
        edgecolor="#E2E8F0",
        fancybox=True,
        loc="upper right",
    )

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Веерный график анализа чувствительности
# ---------------------------------------------------------------------------

def plot_parameter_sensitivity(
    results: list[SimulationResult],
    param_values: list[float],
    param_name: str,
    param_unit: str,
    substance_name: str = "Вещество",
    compartment: str = "brain",
    colormap: str = "plasma",
) -> plt.Figure:
    """
    Построить веерный график чувствительности к одному параметру модели.

    Отображает несколько кривых концентрации (в мозге или крови) при
    различных значениях выбранного параметра — позволяет наглядно оценить
    влияние параметра на динамику.

    Параметры
    ---------
    results : list[SimulationResult]
        Список результатов симуляции для каждого значения параметра.
    param_values : list[float]
        Значения параметра, соответствующие каждому результату.
    param_name : str
        Название параметра для легенды (напр. "k_pass").
    param_unit : str
        Единицы измерения параметра (напр. "1/ч").
    substance_name : str
        Название вещества для заголовка.
    compartment : str
        Компартмент для отображения: "brain" или "blood".
    colormap : str
        Название colormap matplotlib для раскраски кривых.
        plt.get_cmap удалён в matplotlib 3.9; используем matplotlib.colormaps.

    Возвращает
    ----------
    matplotlib.figure.Figure
        Готовый к отображению объект Figure.
    """
    fig, ax = plt.subplots(figsize=(_FIG_W, _FIG_H))
    _style_axes(ax, fig)

    # matplotlib.colormaps вместо устаревшего plt.get_cmap (удалён в 3.9)
    cmap = matplotlib.colormaps[colormap]
    n = len(results)

    for i, (res, val) in enumerate(zip(results, param_values)):
        color  = cmap(i / max(n - 1, 1))
        y_data = res.c_brain if compartment == "brain" else res.c_blood
        label  = f"{param_name} = {val:.3g} {param_unit}"
        ax.plot(res.t, y_data, color=color, linewidth=_LINE_WIDTH, label=label)

    compartment_label = "Мозг" if compartment == "brain" else "Кровь"
    ax.set_xlabel("Время, ч", fontsize=_FONT_LABEL, color="#37474F")
    ax.set_ylabel("Концентрация, мкМ", fontsize=_FONT_LABEL, color="#37474F")
    ax.set_title(
        f"Чувствительность к «{param_name}» — {substance_name}  |  {compartment_label}",
        fontsize=_FONT_TITLE,
        fontweight="bold",
        color="#0D47A1",
        pad=14,
    )
    ax.set_xlim(left=0.0)
    ax.set_ylim(bottom=0.0)
    ax.legend(fontsize=9, framealpha=0.95, edgecolor="#E2E8F0", fancybox=True)

    fig.tight_layout()
    return fig
