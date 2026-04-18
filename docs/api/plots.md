# Plots

Модуль `bbb.visualization.plots` содержит две группы функций визуализации:

| Группа | Функции | Назначение |
|---|---|---|
| **Matplotlib** | `plot_concentrations`, `plot_parameter_sensitivity` | Статичные PNG-графики для экспорта |
| **Plotly** | `plot_concentrations_interactive`, `plot_sensitivity_interactive` | Интерактивные графики в Streamlit UI |

**Семантические цвета проекта:**

```python
COLOR_BLOOD = "#DC2626"  # красный — апикальный компартмент (кровь)
COLOR_BRAIN = "#2563EB"  # синий   — базолатеральный компартмент (мозг)
```

!!! note "Google-style docstrings"
    Все публичные функции модуля имеют полные Google-style docstrings с секциями
    `Args`, `Returns`, `Raises` — они корректно парсятся mkdocstrings.

---

::: bbb.visualization.plots
    options:
      members:
        - plot_concentrations
        - plot_parameter_sensitivity
        - plot_concentrations_interactive
        - plot_sensitivity_interactive
        - COLOR_BLOOD
        - COLOR_BRAIN
