# Model

Модуль `bbb.core.model` содержит правые части ОДУ двухкомпартментной модели ГЭБ.

**Реализует:**

- Пассивную диффузию по закону Фика: `J_diff = k_pass · (C_blood − C_brain)`
- Активный P-gp эффлюкс по кинетике Михаэлиса–Ментен: `J_pgp = Vmax · C_brain / (Km + C_brain)`
- Системный клиренс (первый порядок): `J_elim = k_elim · C_blood`

Численное интегрирование выполняется в `bbb.core.simulator.Simulator`.

---

::: bbb.core.model
