# Contributing

## Настройка окружения разработчика

```bash
git clone https://github.com/learning2think/In-Silico-BBB.git
cd In-Silico-BBB

python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Pre-commit hooks

```bash
# Установить хуки (однократно)
pre-commit install

# Прогнать по всему репозиторию вручную
pre-commit run --all-files
```

Настроенные хуки (`.pre-commit-config.yaml`):

| Хук | Действие |
|---|---|
| `ruff` | Линтинг Python |
| `ruff-format` | Форматирование (Black-совместимое) |
| `mypy` | Проверка типов (`bbb/` only) |
| `pyupgrade` | Синтаксис Python 3.10+ |
| `check-yaml`, `check-toml` | Валидация конфигов |
| `end-of-file-fixer`, `trailing-whitespace` | Форматирование файлов |

## Запуск тестов

```bash
# Быстрый прогон
pytest tests/ -v

# С отчётом о покрытии (HTML)
pytest tests/ --cov=bbb --cov-report=html
# Открыть htmlcov/index.html
```

## Code style

```bash
ruff check .               # линтер
ruff check . --fix         # авто-исправление
ruff format .              # форматирование

mypy bbb/                  # типизация (только пакет bbb/)
```

Конфигурация ruff и mypy находится в `pyproject.toml`.

## Добавление нового вещества в substances.py

1. Откройте `bbb/data/substances.py`.
2. Добавьте новый экземпляр `Substance` в словарь `SUBSTANCES`:

```python
SUBSTANCES["Новое вещество"] = Substance(
    name="Новое вещество",
    k_pass=0.5,       # пассивная проницаемость [1/ч]
    vmax=1.0,         # Vmax P-gp [мкМ/ч]; 0.0 если не субстрат P-gp
    km=20.0,          # Km P-gp [мкМ]
    fu_plasma=0.5,    # свободная фракция в плазме (0–1)
    fu_brain=0.5,     # свободная фракция в ткани мозга (0–1)
    color="#FF5733",  # HEX-цвет для графика
    description="Краткое описание вещества.",
    reference="Автор, Журнал, Год.",
)
```

3. Запустите тесты — `test_simulation_success_for_all_substances` проверит новое вещество автоматически.

## Добавление нового теста

Тесты находятся в `tests/test_simulator.py`. Используйте pytest fixtures и assertions:

```python
def test_my_new_feature():
    from bbb.core.simulator import Simulator, SimulationParams
    params = SimulationParams(k_pass=0.5, vmax=1.0, km=10.0)
    result = Simulator().run(params)
    assert result.success
    assert result.c_brain_max > 0
```

## Структура проекта

```
In-Silico-BBB/
├── app.py                    # Streamlit entry point
├── requirements.txt          # Runtime зависимости
├── requirements-dev.txt      # Dev зависимости
├── pyproject.toml            # ruff, mypy, pytest конфигурация
├── mkdocs.yml                # MkDocs конфигурация
├── bbb/
│   ├── core/
│   │   ├── model.py          # ODE правые части
│   │   └── simulator.py      # SimulationParams, SimulationResult, Simulator
│   ├── data/
│   │   └── substances.py     # Substance dataclass + SUBSTANCES реестр
│   └── visualization/
│       └── plots.py          # Matplotlib + Plotly графики
├── tests/
│   └── test_simulator.py
├── docs/                     # MkDocs документация
└── .github/workflows/
    ├── ci.yml                # Lint, typecheck, tests, security, screenshot
    └── docs.yml              # Deploy docs to GitHub Pages
```
