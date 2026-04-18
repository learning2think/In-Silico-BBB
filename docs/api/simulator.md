# Simulator

Модуль `bbb.core.simulator` предоставляет публичный API для запуска симуляций.

**Публичный API:**

| Класс / датакласс | Назначение |
|---|---|
| `SimulationParams` | Параметры одного запуска симуляции |
| `SimulationResult` | Результат: временные ряды концентраций, AUC, Cmax, t(Cmax) |
| `Simulator` | Класс с методом `run(params) → SimulationResult` |

**Пример использования:**

```python
from bbb.core.simulator import Simulator, SimulationParams

params = SimulationParams(
    k_pass=0.8,
    vmax=0.15,
    km=50.0,
    c0_blood=1.0,
    t_end=24.0,
)
sim = Simulator()
result = sim.run(params)
print(f"Cmax в мозге: {result.c_brain_max:.4f} мкМ")
print(f"AUC в мозге: {result.auc_brain:.4f} мкМ·ч")
```

---

::: bbb.core.simulator
