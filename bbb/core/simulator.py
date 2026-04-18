"""
Модуль simulator — класс Simulator для численного решения ОДУ модели ГЭБ.

Публичный API
-------------
  SimulationParams  — датакласс параметров одного запуска.
  SimulationResult  — датакласс результата (t, c_blood, c_brain, AUC, Cmax).
  Simulator         — класс с методом run(params) → SimulationResult.

Выбор численного метода
-----------------------
Используется LSODA (Livermore Solver for Ordinary Differential Equations
with Automatic method switching) через scipy.integrate.solve_ivp.

LSODA автоматически переключается между явными (Adams) и неявными (BDF)
схемами в зависимости от жёсткости системы:

  - При малых значениях Km и высоких концентрациях член Михаэлиса–Ментен
    может создавать жёсткость → BDF подавляет нестабильность без потери
    точности.
  - На нежёстких участках LSODA переходит на Adams (скорость явных методов).

Точность: rtol=1e-8, atol=1e-10 — достаточно для концентраций ~1e-3 мкМ.
"""

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from bbb.core.model import bbb_ode


@dataclass
class SimulationParams:
    """
    Параметры одного запуска симуляции.

    Атрибуты
    --------
    k_pass : float
        Коэффициент пассивной проницаемости [1/ч].
    vmax : float
        Максимальная скорость P-gp [мкМ/ч].
    km : float
        Константа Михаэлиса для P-gp [мкМ].
    c0_blood : float
        Начальная концентрация в крови [мкМ].
    c0_brain : float
        Начальная концентрация в мозге [мкМ].
    t_end : float
        Время окончания симуляции [ч].
    v_blood : float
        Относительный объём кровяного компартмента [усл. ед.].
    v_brain : float
        Относительный объём мозгового компартмента [усл. ед.].
    n_points : int
        Количество точек для вывода результата.
    """

    k_pass: float = 0.5
    vmax: float = 1.0
    km: float = 10.0
    c0_blood: float = 1.0
    c0_brain: float = 0.0
    t_end: float = 24.0
    v_blood: float = 1.0
    v_brain: float = 0.3
    n_points: int = 500
    k_elim: float = 0.0  # системный клиренс из крови [1/ч]; 0 = in vitro


@dataclass
class SimulationResult:
    """
    Результат численного интегрирования.

    Атрибуты
    --------
    t : np.ndarray
        Массив временных точек [ч].
    c_blood : np.ndarray
        Концентрация в кровяном компартменте [мкМ].
    c_brain : np.ndarray
        Концентрация в мозговом компартменте [мкМ].
    success : bool
        Флаг успешного завершения интегрирования.
    message : str
        Сообщение решателя (для диагностики).
    auc_brain : float
        Площадь под кривой (AUC) в мозге [мкМ·ч] — интегральный показатель
        экспозиции вещества в ткани мозга.
    c_brain_max : float
        Максимальная концентрация в мозге [мкМ] — Cmax.
    """

    t: np.ndarray
    c_blood: np.ndarray
    c_brain: np.ndarray
    success: bool
    message: str
    auc_brain: float
    c_brain_max: float
    t_brain_max: float  # время достижения Cmax в мозге [ч]


class Simulator:
    """
    Симулятор транспорта вещества через гематоэнцефалический барьер.

    Реализует численное решение системы ОДУ методом LSODA через
    интерфейс scipy.integrate.solve_ivp.

    Пример использования
    --------------------
    >>> from bbb.core.simulator import Simulator, SimulationParams
    >>> params = SimulationParams(k_pass=0.8, vmax=0.15, km=50.0, t_end=24)
    >>> sim = Simulator()
    >>> result = sim.run(params)
    >>> print(f"Cmax в мозге: {result.c_brain_max:.4f} мкМ")
    """

    def __init__(
        self,
        rtol: float = 1e-8,
        atol: float = 1e-10,
    ) -> None:
        """
        Инициализация симулятора.

        Параметры
        ---------
        rtol : float
            Относительная точность решателя (по умолчанию 1e-8).
        atol : float
            Абсолютная точность решателя (по умолчанию 1e-10).
            Выбрана малой, так как концентрации могут быть ~1e-3 мкМ
            в конце симуляции.
        """
        self.rtol = rtol
        self.atol = atol

    def run(self, params: SimulationParams) -> SimulationResult:
        """
        Запустить симуляцию транспорта через ГЭБ.

        Параметры
        ---------
        params : SimulationParams
            Параметры модели и начальные условия.

        Возвращает
        ----------
        SimulationResult
            Результат интегрирования с временным рядом концентраций
            и производными показателями (AUC, Cmax).

        Примечание
        ----------
        При неудачном завершении решателя возвращается SimulationResult
        с ``success=False`` и описанием проблемы в поле ``message``.
        Исключение не бросается.
        """
        # Временна́я сетка для вывода результата
        t_eval = np.linspace(0.0, params.t_end, params.n_points)

        # Начальные условия: [C_blood(0), C_brain(0)]
        y0 = [params.c0_blood, params.c0_brain]

        # Численное интегрирование методом LSODA
        # (автоматическое переключение Adams/BDF для жёстких и нежёстких участков)
        sol = solve_ivp(
            fun=bbb_ode,
            t_span=(0.0, params.t_end),
            y0=y0,
            method="LSODA",
            t_eval=t_eval,
            args=(
                params.k_pass,
                params.vmax,
                params.km,
                params.v_blood,
                params.v_brain,
                params.k_elim,
            ),
            rtol=self.rtol,
            atol=self.atol,
            dense_output=False,
        )

        c_blood = sol.y[0]
        c_brain = sol.y[1]

        # Площадь под кривой концентрации в мозге (метод трапеций)
        # np.trapz удалён в NumPy 2.0, используем np.trapezoid
        auc_brain = float(np.trapezoid(c_brain, sol.t))

        # Максимальная концентрация в мозге и время её достижения
        idx_max = int(np.argmax(c_brain))
        c_brain_max = float(c_brain[idx_max])
        t_brain_max = float(sol.t[idx_max])

        return SimulationResult(
            t=sol.t,
            c_blood=c_blood,
            c_brain=c_brain,
            success=sol.success,
            message=sol.message,
            auc_brain=auc_brain,
            c_brain_max=c_brain_max,
            t_brain_max=t_brain_max,
        )
