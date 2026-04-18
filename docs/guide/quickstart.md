# Quickstart

## Требования

- Python **3.11+**
- git

## Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/learning2think/In-Silico-BBB.git
cd In-Silico-BBB

# 2. Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Установить зависимости
pip install -r requirements.txt
```

## Запуск приложения

```bash
streamlit run app.py
```

Браузер откроется автоматически по адресу `http://localhost:8501`.

## Первый запуск: пошаговый сценарий

1. **Выберите вещество** в левой панели (например, *Диазепам*) — параметры k_pass, Vmax, Km заполнятся автоматически.
2. Нажмите **Запустить симуляцию** — на вкладке *Results* появятся интерактивный график и PK-метрики.
3. Переключитесь на вкладку **Sensitivity** — постройте веерный график по k_pass, чтобы увидеть влияние пассивной проницаемости на Cmax в мозге.
4. Нажмите **Export CSV** или **Export PNG** для сохранения результатов.

!!! note "Режимы модели"
    - `k_elim = 0` — закрытая система (in vitro, масса сохраняется).
    - `k_elim > 0` — открытая система (in vivo, учитывается системный клиренс).

## Установка зависимостей для разработки

```bash
pip install -r requirements-dev.txt
pre-commit install
```
