<div align="center">

# 🧠 In Silico BBB

**Mechanistic two-compartment simulator of blood–brain barrier drug transport**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.56-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/tests-17%20passed-2ea44f?logo=pytest&logoColor=white)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![UMNIK](https://img.shields.io/badge/Funded%20by-UMNIK%20Innovation%20Fund-F97316)](https://fasie.ru/)

[🇬🇧 English](#-english) · [🇷🇺 Русский](#-русский)

</div>

---

## 🇬🇧 English

### Overview

The blood–brain barrier (BBB) is a highly selective physiological interface between the bloodstream and brain tissue. Approximately **98% of small molecules** fail to reach therapeutic concentrations in the CNS, making preclinical permeability assessment a critical bottleneck in neurological drug development.

**In Silico BBB** is an open-source computational platform implementing a mechanistic two-compartment kinetic model of BBB transport. It captures both **passive diffusion** (Fick's law) and **active P-glycoprotein efflux** (Michaelis–Menten kinetics) — the primary transporter limiting CNS drug accumulation.

**Target users:** pharmacologists, medicinal chemists, and neuroscientists engaged in preclinical CNS drug discovery.

---

### Features

| Feature | Description |
|---|---|
| **Transport simulation** | ODE integration via LSODA (scipy) with automatic stiff/non-stiff switching |
| **PK metrics** | Cmax, AUC (trapezoid), Kp,uu (fu-corrected), t(Cmax) |
| **Protein binding correction** | fu_plasma and fu_brain sliders; true unbound Kp,uu = (C_brain·fu_brain)/(C_blood·fu_plasma) |
| **Systemic clearance** | k_elim parameter switches model from closed in vitro to open in vivo mode |
| **Sensitivity analysis** | Fan plots for k_pass, Vmax, or Km with compartment selector |
| **Compound comparison** | Ranking table for all 7 built-in substances under identical conditions |
| **Export** | CSV with metadata header + PNG plot (150 dpi) |
| **Substance registry** | 7 compounds with literature-verified parameters and protein binding values |
| **Interactive UI** | Streamlit app — no programming required |
| **Test suite** | 17 pytest tests covering mass conservation, P-gp physics, and all substances |

---

### Mathematical Model

#### Compartments

| Compartment | Biological analogue | Volume (a.u.) |
|---|---|---|
| Apical | Blood / donor well | V_blood = 1.0 |
| Basolateral | Brain tissue / acceptor well | V_brain = 0.3 |

#### Transport mechanisms

**Passive diffusion** (Fick's law):
```
J_diff = k_pass × (C_blood − C_brain)          [µM/h]
```

**Active P-gp efflux** (Michaelis–Menten):
```
J_pgp  = Vmax × C_brain / (Km + C_brain)       [µM/h]
```

**Systemic clearance** (first-order elimination from blood):
```
J_elim = k_elim × C_blood                      [µM/h]
```

#### ODE system

```
dC_blood/dt = −J_diff + (V_brain/V_blood) × J_pgp − J_elim
dC_brain/dt =  (V_blood/V_brain) × J_diff − J_pgp
```

Volume coefficients enforce **mass conservation** (when k_elim = 0):
`d/dt(C_blood × V_blood + C_brain × V_brain) = 0`

#### Output metrics

| Metric | Definition |
|---|---|
| **Cmax** | Peak concentration in brain compartment [µM] |
| **t(Cmax)** | Time to reach Cmax [h] |
| **AUC** | Area under brain concentration–time curve (trapezoidal) [µM·h] |
| **Kp,uu** | Mean (C_brain·fu_brain)/(C_blood·fu_plasma) over final 5 % of simulation |

#### Numerical method

**LSODA** via `scipy.integrate.solve_ivp` — automatic Adams/BDF switching.
Tolerances: `atol = 1e-10`, `rtol = 1e-8`.

---

### Project Structure

```
In-Silico-BBB/
│
├── bbb/                          # Core Python package
│   ├── core/
│   │   ├── model.py              # ODE right-hand sides (bbb_ode)
│   │   └── simulator.py          # SimulationParams · SimulationResult · Simulator
│   ├── data/
│   │   └── substances.py         # Substance dataclass + SUBSTANCES registry (7 compounds)
│   └── visualization/
│       └── plots.py              # plot_concentrations() · plot_parameter_sensitivity()
│
├── tests/
│   └── test_simulator.py         # 17 pytest tests
│
├── app.py                        # Streamlit entry point
├── requirements.txt
└── README.md
```

---

### Installation

**Requirements:** Python 3.11+

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/In-Silico-BBB.git
cd In-Silico-BBB

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py
```

The browser will open automatically at `http://localhost:8501`.

---

### Running Tests

```bash
pytest tests/ -v
```

| Test | Validates |
|---|---|
| `test_mass_conservation_no_pgp` | Mass conservation without P-gp efflux |
| `test_mass_conservation_with_pgp` | Mass conservation with P-gp active |
| `test_passive_diffusion_equilibrium` | C_blood ≈ C_brain at steady state |
| `test_pgp_reduces_brain_concentration` | P-gp lowers Cmax and AUC in brain |
| `test_simulation_success_for_all_substances` | All 7 substances solve without error |
| `test_ode_rhs_mass_conservation` | d/dt(total mass) = 0 at ODE level |
| `test_auc_and_cmax_positive` | AUC > 0 and Cmax > 0 for non-zero dose |
| `test_zero_initial_concentration` | Zero IC → zero concentrations throughout |

---

### Substance Registry

| Compound | logP | k_pass [1/h] | Vmax [µM/h] | Km [µM] | fu_plasma | fu_brain | P-gp substrate |
|---|---|---|---|---|---|---|---|
| Diazepam | 2.8 | 0.80 | 0.15 | 50.0 | 0.01 | 0.03 | Weak |
| Verapamil | 3.8 | 0.30 | 2.50 | 8.0 | 0.10 | 0.10 | Strong |
| Dextran | — | 0.008 | 0.0 | — | 1.00 | 1.00 | None (barrier marker) |
| Caffeine | −0.07 | 0.50 | 0.05 | 30.0 | 0.65 | 0.80 | Negligible |
| Morphine | 0.9 | 0.12 | 1.20 | 12.0 | 0.65 | 0.70 | Strong |
| Donepezil | 4.0 | 0.60 | 0.18 | 25.0 | 0.05 | 0.12 | Weak |
| Levetiracetam | −0.6 | 0.25 | 0.0 | — | 0.90 | 0.85 | None |

All parameters sourced from peer-reviewed literature (see `bbb/data/substances.py` for references).

#### Adding a custom compound

Edit `bbb/data/substances.py`:

```python
SUBSTANCES["MyCompound"] = Substance(
    name="MyCompound",
    k_pass=0.4,      # passive permeability [1/h]
    vmax=1.2,        # P-gp Vmax [µM/h]
    km=15.0,         # P-gp Km [µM]
    fu_plasma=0.30,  # unbound fraction in plasma
    fu_brain=0.15,   # unbound fraction in brain tissue
    color="#9C27B0",
    description="Brief description.",
    reference="Author, Journal, Year.",
)
```

---

### Roadmap

#### Phase 1 — UMNIK Year 1
- [ ] QSAR module: predict k_pass from molecular structure (RDKit descriptors + random forest)
- [ ] Additional efflux transporters: BCRP (ABCG2) and MRP4 with independent Michaelis–Menten terms
- [ ] Expand registry to 50+ literature-verified compounds

#### Phase 2 — UMNIK Year 2
- [ ] Three-compartment model (donor / endothelium / acceptor) for Transwell and PAMPA-BBB comparison
- [ ] REST API for high-throughput virtual library screening
- [ ] Validation against published PET imaging data (mouse, rat, human)

#### Long-term
- [ ] Integration with molecular docking platforms (AutoDock, Glide)
- [ ] Patient-specific PBPK parameterisation from clinical PK data

---

### License

MIT License — see [LICENSE](LICENSE) for details.

---

### Citation

If you use In Silico BBB in your research, please cite:

```
In Silico BBB — Mechanistic BBB Transport Simulator (2024).
GitHub: https://github.com/<your-username>/In-Silico-BBB
Supported by UMNIK programme, Innovation Promotion Fund (Фонд содействия инновациям).
```

---
---

## 🇷🇺 Русский

### Обзор

Гематоэнцефалический барьер (ГЭБ) — высокоселективный физиологический барьер между кровотоком и тканью мозга. Около **98% малых молекул** не достигают терапевтических концентраций в ЦНС, что делает доклиническую оценку проницаемости критически важным этапом разработки ЦНС-препаратов.

**In Silico BBB** — платформа с открытым исходным кодом, реализующая механистическую двухкомпартментную кинетическую модель транспорта через ГЭБ. Модель учитывает **пассивную диффузию** (закон Фика) и **активный P-gp эффлюкс** (кинетика Михаэлиса–Ментен) — ключевой транспортёр, ограничивающий накопление большинства лекарств в мозге.

**Целевая аудитория:** фармакологи, медицинские химики, нейробиологи на этапе доклинической разработки ЦНС-препаратов.

---

### Функциональность

| Возможность | Описание |
|---|---|
| **Симуляция транспорта** | Численное решение ОДУ методом LSODA (scipy), автопереключение Adams/BDF |
| **PK-метрики** | Cmax, AUC (трапеции), Kp,uu с поправкой на fu, t(Cmax) |
| **Поправка на белки** | Слайдеры fu_plasma и fu_brain; истинный Kp,uu = (C_brain·fu_brain)/(C_blood·fu_plasma) |
| **Системный клиренс** | Параметр k_elim переключает режим из in vitro (закрытая система) в in vivo |
| **Анализ чувствительности** | Веерный график по k_pass, Vmax или Km с выбором компартмента |
| **Сравнение веществ** | Ранжирующая таблица по Kp,uu для всех 7 веществ при одинаковых условиях |
| **Экспорт** | CSV с метаданными и заголовком + PNG-график (150 dpi) |
| **Реестр веществ** | 7 соединений с верифицированными параметрами и значениями fu |
| **Интерактивный UI** | Streamlit-приложение, не требует программирования |
| **Автотесты** | 17 pytest-тестов: физика модели, P-gp, все 7 веществ |

---

### Математическая модель

#### Компартменты

| Компартмент | Биологический аналог | Объём (усл. ед.) |
|---|---|---|
| Апикальный | Кровь / донорная лунка | V_blood = 1.0 |
| Базолатеральный | Ткань мозга / акцепторная лунка | V_brain = 0.3 |

#### Транспортные механизмы

**Пассивная диффузия** (закон Фика):
```
J_diff = k_pass × (C_blood − C_brain)          [мкМ/ч]
```

**Активный P-gp эффлюкс** (Михаэлис–Ментен):
```
J_pgp  = Vmax × C_brain / (Km + C_brain)       [мкМ/ч]
```

**Системный клиренс** (элиминация первого порядка из крови):
```
J_elim = k_elim × C_blood                      [мкМ/ч]
```

#### Система ОДУ

```
dC_blood/dt = −J_diff + (V_brain/V_blood) × J_pgp − J_elim
dC_brain/dt =  (V_blood/V_brain) × J_diff − J_pgp
```

Объёмные коэффициенты обеспечивают **закон сохранения вещества** (при k_elim = 0):
`d/dt(C_blood × V_blood + C_brain × V_brain) = 0`

#### Выходные показатели

| Показатель | Определение |
|---|---|
| **Cmax** | Максимальная концентрация в мозговом компартменте [мкМ] |
| **t(Cmax)** | Время достижения максимума [ч] |
| **AUC** | Площадь под кривой концентрация–время в мозге (трапеции) [мкМ·ч] |
| **Kp,uu** | Среднее (C_brain·fu_brain)/(C_blood·fu_plasma) за последние 5 % симуляции |

#### Численный метод

**LSODA** через `scipy.integrate.solve_ivp` — автоматическое переключение Adams (нежёсткие участки) / BDF (жёсткие).
Точность: `atol = 1e-10`, `rtol = 1e-8`.

---

### Структура проекта

```
In-Silico-BBB/
│
├── bbb/                          # Основной Python-пакет
│   ├── core/
│   │   ├── model.py              # Правые части ОДУ (bbb_ode)
│   │   └── simulator.py          # SimulationParams · SimulationResult · Simulator
│   ├── data/
│   │   └── substances.py         # Датакласс Substance + реестр SUBSTANCES (7 веществ)
│   └── visualization/
│       └── plots.py              # plot_concentrations() · plot_parameter_sensitivity()
│
├── tests/
│   └── test_simulator.py         # 17 pytest-тестов
│
├── app.py                        # Точка входа Streamlit
├── requirements.txt
└── README.md
```

---

### Установка и запуск

**Требования:** Python 3.11+

```bash
# 1. Клонировать репозиторий
git clone https://github.com/<your-username>/In-Silico-BBB.git
cd In-Silico-BBB

# 2. Создать и активировать виртуальное окружение
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить приложение
streamlit run app.py
```

Браузер откроется автоматически по адресу `http://localhost:8501`.

---

### Запуск тестов

```bash
pytest tests/ -v
```

| Тест | Что проверяет |
|---|---|
| `test_mass_conservation_no_pgp` | Закон сохранения без P-gp |
| `test_mass_conservation_with_pgp` | Закон сохранения с P-gp |
| `test_passive_diffusion_equilibrium` | Диффузионное равновесие C_blood ≈ C_brain |
| `test_pgp_reduces_brain_concentration` | P-gp снижает Cmax и AUC в мозге |
| `test_simulation_success_for_all_substances` | Все 7 веществ решаются без ошибок |
| `test_ode_rhs_mass_conservation` | d/dt(масса) = 0 на уровне ОДУ |
| `test_auc_and_cmax_positive` | AUC > 0 и Cmax > 0 при ненулевой дозе |
| `test_zero_initial_concentration` | Нулевые начальные условия → нулевые концентрации |

---

### Реестр веществ

| Вещество | logP | k_pass [1/ч] | Vmax [мкМ/ч] | Km [мкМ] | fu_plasma | fu_brain | P-gp |
|---|---|---|---|---|---|---|---|
| Диазепам | 2.8 | 0.80 | 0.15 | 50.0 | 0.01 | 0.03 | Слабый |
| Верапамил | 3.8 | 0.30 | 2.50 | 8.0 | 0.10 | 0.10 | Выраженный |
| Декстран | — | 0.008 | 0.0 | — | 1.00 | 1.00 | Нет (маркер) |
| Кофеин | −0.07 | 0.50 | 0.05 | 30.0 | 0.65 | 0.80 | Незначительный |
| Морфин | 0.9 | 0.12 | 1.20 | 12.0 | 0.65 | 0.70 | Выраженный |
| Донепезил | 4.0 | 0.60 | 0.18 | 25.0 | 0.05 | 0.12 | Слабый |
| Леветирацетам | −0.6 | 0.25 | 0.0 | — | 0.90 | 0.85 | Нет |

Параметры взяты из рецензируемой литературы (источники — в `bbb/data/substances.py`).

#### Добавление нового вещества

Отредактируйте `bbb/data/substances.py`:

```python
SUBSTANCES["МоёВещество"] = Substance(
    name="МоёВещество",
    k_pass=0.4,      # пассивная проницаемость [1/ч]
    vmax=1.2,        # Vmax P-gp [мкМ/ч]
    km=15.0,         # Km P-gp [мкМ]
    fu_plasma=0.30,  # свободная фракция в плазме
    fu_brain=0.15,   # свободная фракция в ткани мозга
    color="#9C27B0",
    description="Краткое описание вещества.",
    reference="Автор, журнал, год.",
)
```

---

### Планы развития

#### Этап 1 — год 1 УМНИК
- [ ] QSAR-блок: предсказание k_pass по структуре молекулы (дескрипторы RDKit, случайный лес)
- [ ] Транспортёры BCRP (ABCG2) и MRP4 с независимыми параметрами Михаэлиса–Ментен
- [ ] Расширение реестра до 50+ верифицированных соединений

#### Этап 2 — год 2 УМНИК
- [ ] Трёхкомпартментная модель (донор / эндотелий / акцептор) для сравнения с данными Transwell и PAMPA-BBB
- [ ] REST API для пакетного скрининга виртуальных библиотек
- [ ] Валидация на опубликованных PET-данных (мышь, крыса, человек)

#### Долгосрочная перспектива
- [ ] Интеграция с платформами молекулярного докинга (AutoDock, Glide)
- [ ] Персонализированная PBPK-параметризация на основе клинических PK-данных пациента

---

### Лицензия

MIT — подробности в файле [LICENSE](LICENSE).

---

### Цитирование

Если вы используете In Silico BBB в своей работе, пожалуйста, укажите ссылку:

```
In Silico BBB — Mechanistic BBB Transport Simulator (2024).
GitHub: https://github.com/<your-username>/In-Silico-BBB
Поддержано программой УМНИК, Фонд содействия инновациям.
```

---

<div align="center">
<i>In Silico BBB — на пересечении вычислительной биофизики, фармакологии и программной инженерии.</i>
</div>
