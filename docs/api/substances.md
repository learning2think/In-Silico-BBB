# Substances

Модуль `bbb.data.substances` содержит реестр модельных веществ.

**Встроенные вещества (7):**

| Вещество | logP | k_pass | Vmax | Km | P-gp |
|---|---|---|---|---|---|
| Диазепам | 2.8 | 0.80 | 0.15 | 50.0 | Слабый |
| Верапамил | 3.8 | 0.30 | 2.50 | 8.0 | Выраженный |
| Декстран | — | 0.008 | 0.0 | — | Нет |
| Кофеин | −0.07 | 0.50 | 0.05 | 30.0 | Незначительный |
| Морфин | 0.9 | 0.12 | 1.20 | 12.0 | Выраженный |
| Донепезил | 4.0 | 0.60 | 0.18 | 25.0 | Слабый |
| Леветирацетам | −0.6 | 0.25 | 0.0 | — | Нет |

**Добавление нового вещества:**

```python
from bbb.data.substances import SUBSTANCES, Substance

SUBSTANCES["MyCompound"] = Substance(
    name="MyCompound",
    k_pass=0.4,
    vmax=1.2,
    km=15.0,
    fu_plasma=0.30,
    fu_brain=0.15,
    color="#9C27B0",
    description="Brief description.",
    reference="Author, Journal, Year.",
)
```

---

::: bbb.data.substances
