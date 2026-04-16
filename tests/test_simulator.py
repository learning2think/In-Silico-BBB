"""
Тесты двухкомпартментной модели ГЭБ.

Запуск:
    pytest tests/ -v

Тесты проверяют:
  - закон сохранения вещества (физическое ограничение модели);
  - диффузионное равновесие при отсутствии P-gp;
  - влияние P-gp на снижение концентрации в мозге;
  - успешность симуляций для всех предустановленных веществ;
  - корректность правых частей ОДУ;
  - неотрицательность производных метрик (AUC, Cmax).
"""

import numpy as np
import pytest

from bbb.core.model import bbb_ode
from bbb.core.simulator import Simulator, SimulationParams
from bbb.data.substances import SUBSTANCES


# ---------------------------------------------------------------------------
# Вспомогательные значения
# ---------------------------------------------------------------------------

_DEFAULT_PARAMS = SimulationParams(
    k_pass=0.5,
    vmax=0.0,
    km=10.0,
    c0_blood=1.0,
    c0_brain=0.0,
    t_end=48.0,
    v_blood=1.0,
    v_brain=0.3,
    n_points=300,
)


# ---------------------------------------------------------------------------
# Тест 1: закон сохранения вещества
# ---------------------------------------------------------------------------

def test_mass_conservation_no_pgp():
    """
    При отсутствии P-gp общее количество вещества (сумма по компартментам)
    должно оставаться неизменным в пределах численной погрешности решателя.
    """
    params = _DEFAULT_PARAMS
    sim = Simulator()
    result = sim.run(params)

    total_initial = params.c0_blood * params.v_blood + params.c0_brain * params.v_brain
    total_final = result.c_blood[-1] * params.v_blood + result.c_brain[-1] * params.v_brain

    assert abs(total_final - total_initial) / total_initial < 1e-4, (
        f"Нарушение закона сохранения: "
        f"начало={total_initial:.6f}, конец={total_final:.6f}"
    )


def test_mass_conservation_with_pgp():
    """
    P-gp лишь перекачивает вещество между компартментами, не уничтожает его,
    поэтому закон сохранения должен выполняться и при активном эффлюксе.
    """
    params = SimulationParams(
        k_pass=0.3, vmax=2.5, km=8.0,
        c0_blood=1.0, t_end=48.0, v_blood=1.0, v_brain=0.3, n_points=300,
    )
    sim = Simulator()
    result = sim.run(params)

    total_initial = params.c0_blood * params.v_blood
    total_final = result.c_blood[-1] * params.v_blood + result.c_brain[-1] * params.v_brain

    assert abs(total_final - total_initial) / total_initial < 1e-4


# ---------------------------------------------------------------------------
# Тест 2: диффузионное равновесие без P-gp
# ---------------------------------------------------------------------------

def test_passive_diffusion_equilibrium():
    """
    При vmax=0 и достаточном времени симуляции концентрации в обоих
    компартментах должны выровняться: C_blood ≈ C_brain.
    """
    params = SimulationParams(
        k_pass=0.8, vmax=0.0, km=1.0,
        c0_blood=1.0, t_end=72.0, v_blood=1.0, v_brain=0.3, n_points=200,
    )
    sim = Simulator()
    result = sim.run(params)

    assert abs(result.c_blood[-1] - result.c_brain[-1]) < 0.01, (
        f"Равновесие не достигнуто: "
        f"C_blood={result.c_blood[-1]:.4f}, C_brain={result.c_brain[-1]:.4f}"
    )


# ---------------------------------------------------------------------------
# Тест 3: P-gp снижает концентрацию в мозге
# ---------------------------------------------------------------------------

def test_pgp_reduces_brain_concentration():
    """
    Активация P-gp должна уменьшать как Cmax, так и AUC в мозге по сравнению
    с симуляцией без эффлюкса при прочих равных параметрах.
    """
    base = dict(k_pass=0.3, c0_blood=1.0, t_end=24.0, v_blood=1.0, v_brain=0.3)
    sim = Simulator()

    result_no_pgp  = sim.run(SimulationParams(**base, vmax=0.0,  km=10.0))
    result_with_pgp = sim.run(SimulationParams(**base, vmax=2.5, km=8.0))

    assert result_with_pgp.c_brain_max < result_no_pgp.c_brain_max, (
        "P-gp не снизил Cmax в мозге"
    )
    assert result_with_pgp.auc_brain < result_no_pgp.auc_brain, (
        "P-gp не снизил AUC в мозге"
    )


# ---------------------------------------------------------------------------
# Тест 4: успешный запуск для всех предустановленных веществ
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("substance_name", list(SUBSTANCES.keys()))
def test_simulation_success_for_all_substances(substance_name):
    """
    Симуляция должна завершаться успешно (sol.success=True) для каждого
    предустановленного вещества при стандартных начальных условиях.
    """
    sub = SUBSTANCES[substance_name]
    params = SimulationParams(
        k_pass=sub.k_pass, vmax=sub.vmax, km=sub.km,
        c0_blood=1.0, t_end=24.0,
    )
    result = Simulator().run(params)

    assert result.success, (
        f"Симуляция не завершилась для '{substance_name}': {result.message}"
    )


# ---------------------------------------------------------------------------
# Тест 5: правые части ОДУ сохраняют вещество
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("y,k_pass,vmax,km", [
    ([0.8, 0.2], 0.5, 0.0,  10.0),   # без P-gp
    ([0.8, 0.2], 0.5, 2.0,  10.0),   # с P-gp
    ([0.5, 0.5], 0.1, 5.0,   5.0),   # насыщение P-gp
    ([0.001, 0.001], 0.8, 1.0, 50.0), # малые концентрации
])
def test_ode_rhs_mass_conservation(y, k_pass, vmax, km):
    """
    d/dt(V_blood * C_blood + V_brain * C_brain) = 0 — закон сохранения
    выражен непосредственно в правых частях ОДУ.
    """
    v_blood, v_brain = 1.0, 0.3
    dydt = bbb_ode(0.0, y, k_pass, vmax, km, v_blood, v_brain)
    total_rate = dydt[0] * v_blood + dydt[1] * v_brain
    assert abs(total_rate) < 1e-10, (
        f"Нарушение баланса в ОДУ: d/dt(total) = {total_rate:.2e}"
    )


# ---------------------------------------------------------------------------
# Тест 6: AUC и Cmax неотрицательны
# ---------------------------------------------------------------------------

def test_auc_and_cmax_positive():
    """
    При ненулевой начальной концентрации AUC и Cmax должны быть > 0.
    """
    result = Simulator().run(SimulationParams(c0_blood=1.0))
    assert result.auc_brain > 0.0, "AUC в мозге не должна быть нулевой"
    assert result.c_brain_max > 0.0, "Cmax в мозге не должна быть нулевой"


# ---------------------------------------------------------------------------
# Тест 7: нулевая начальная концентрация → нулевой результат
# ---------------------------------------------------------------------------

def test_zero_initial_concentration():
    """
    При c0_blood=0 и c0_brain=0 концентрации должны оставаться нулевыми
    во всех точках (система линейная по начальным условиям).
    """
    params = SimulationParams(c0_blood=0.0, c0_brain=0.0)
    result = Simulator().run(params)
    assert np.allclose(result.c_blood, 0.0, atol=1e-10)
    assert np.allclose(result.c_brain, 0.0, atol=1e-10)
