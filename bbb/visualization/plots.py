"""
Модуль plots — построение научных графиков результатов симуляции ГЭБ.

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

_FONT_TITLE = 14
_FONT_LABEL = 12
_FONT_TICK = 10
_FONT_LEGEND = 11
_LINE_WIDTH = 2.2
_ALPHA_FILL = 0.12


def plot_concentrations(
    result: SimulationResult,
    substance_name: str = "Вещество",
    blood_color: str = "#E53935",
    brain_color: str = "#1E88E5",
    show_auc: bool = True,
) -> plt.Figure:
    """
    Построить график изменения концентраций в обоих компартментах.

    На график выводятся:
      - Концентрация в крови (апикальный компартмент)
      - Концентрация в мозге (базолатеральный компартмент)
      - Закрашенная область под кривой мозга (если show_auc=True)
      - Аннотация с Cmax и AUC в мозге

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
    fig, ax = plt.subplots(figsize=(9, 5))

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
        )

    # --- Маркер максимума в мозге ---
    idx_max = int(np.argmax(result.c_brain))
    t_max = result.t[idx_max]
    c_max = result.c_brain[idx_max]
    ax.annotate(
        f"Cmax = {c_max:.3f} мкМ\nt = {t_max:.1f} ч",
        xy=(t_max, c_max),
        xytext=(t_max + result.t[-1] * 0.05, c_max * 0.85),
        fontsize=9,
        color=brain_color,
        arrowprops=dict(arrowstyle="->", color=brain_color, lw=1.2),
    )

    # --- Оформление осей ---
    ax.set_xlabel("Время [ч]", fontsize=_FONT_LABEL)
    ax.set_ylabel("Концентрация [мкМ]", fontsize=_FONT_LABEL)
    ax.set_title(
        f"Транспорт «{substance_name}» через ГЭБ\n"
        "Двухкомпартментная модель: пассивная диффузия + P-gp эффлюкс",
        fontsize=_FONT_TITLE,
        pad=12,
    )

    ax.tick_params(labelsize=_FONT_TICK)
    ax.set_xlim(left=0.0)
    ax.set_ylim(bottom=0.0)
    ax.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.legend(fontsize=_FONT_LEGEND, framealpha=0.9)

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

    Возвращает
    ----------
    matplotlib.figure.Figure
        Готовый к отображению объект Figure.
    """
    fig, ax = plt.subplots(figsize=(9, 5))

    cmap = plt.get_cmap(colormap)
    n = len(results)

    for i, (res, val) in enumerate(zip(results, param_values)):
        color = cmap(i / max(n - 1, 1))
        y_data = res.c_brain if compartment == "brain" else res.c_blood
        label = f"{param_name} = {val:.3g} {param_unit}"
        ax.plot(res.t, y_data, color=color, linewidth=_LINE_WIDTH, label=label)

    compartment_label = "Мозг" if compartment == "brain" else "Кровь"
    ax.set_xlabel("Время [ч]", fontsize=_FONT_LABEL)
    ax.set_ylabel("Концентрация [мкМ]", fontsize=_FONT_LABEL)
    ax.set_title(
        f"Чувствительность к параметру «{param_name}» — {substance_name}\n"
        f"Компартмент: {compartment_label}",
        fontsize=_FONT_TITLE,
        pad=12,
    )
    ax.tick_params(labelsize=_FONT_TICK)
    ax.set_xlim(left=0.0)
    ax.set_ylim(bottom=0.0)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(fontsize=9, framealpha=0.9)

    fig.tight_layout()
    return fig
