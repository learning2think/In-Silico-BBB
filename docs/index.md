# BBB Visualizer

**In Silico BBB** — механистический двухкомпартментный симулятор транспорта лекарств через гематоэнцефалический барьер (ГЭБ). Приложение реализует пассивную диффузию (закон Фика) и активный P-gp эффлюкс (кинетика Михаэлиса–Ментен), рассчитывает PK-показатели (Cmax, AUC, Kp,uu) и визуализирует результаты в интерактивных графиках Plotly.

![Screenshot](assets/screenshot.png)

!!! tip "Живой пример"
    Запусти приложение локально: `streamlit run app.py`
    Браузер откроется автоматически по адресу `http://localhost:8501`.

---

## Быстрый старт

```bash
git clone https://github.com/learning2think/In-Silico-BBB.git
cd In-Silico-BBB
pip install -r requirements.txt
streamlit run app.py
```

---

## Возможности

| Функция | Описание |
|---|---|
| **Симуляция** | LSODA (scipy) — автопереключение Adams/BDF для жёстких систем |
| **PK-метрики** | Cmax, AUC (трапеции), Kp,uu с поправкой на fu, t(Cmax) |
| **Белковое связывание** | Слайдеры fu_plasma и fu_brain; истинный Kp,uu = (C_brain·fu_brain)/(C_blood·fu_plasma) |
| **Системный клиренс** | k_elim переключает модель из in vitro в in vivo режим |
| **Анализ чувствительности** | Веерные графики по k_pass, Vmax, Km |
| **Реестр веществ** | 7 соединений с литературными параметрами |
| **Экспорт** | CSV с метаданными + PNG 150 dpi |

---

## Навигация по документации

- **[Quickstart](guide/quickstart.md)** — установка и первый запуск
- **[Parameters](guide/parameters.md)** — справочник всех параметров модели
- **[Charts](guide/charts.md)** — как читать графики
- **[API Reference](api/model.md)** — автогенерированная документация модулей
- **[Contributing](dev/contributing.md)** — руководство по участию в разработке
