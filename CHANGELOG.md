# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
### Changed
### Fixed

---

## [0.2.0] - 2026-04-18

### Added
- `pyproject.toml` with `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]` sections
- `.pre-commit-config.yaml`: ruff + ruff-format, mypy (`bbb/` only), pyupgrade `--py310-plus`,
  check-yaml/toml, end-of-file-fixer, trailing-whitespace
- `.github/workflows/ci.yml`: **lint**, **typecheck**, **test** (matrix Python 3.10–3.12),
  **security** (pip-audit, push-only), **screenshot** (push-only, Playwright)
- Codecov integration — coverage XML upload in test job
- CI/CD badges in README.md: CI status, coverage, code quality
- `scripts/screenshot.py` — Playwright-based automated app screenshot
- Google-style docstrings for all public functions in `bbb/visualization/plots.py`
- `_ChartConfig` TypedDict annotation for `_CHART_CONFIG` in `app.py`
- Explicit `result: SimulationResult` type annotation in `_build_csv()` (`app.py`)
- `Development` section in README.md (pre-commit, ruff, mypy, first-run commands)

### Changed
- `_build_csv()` — `result` parameter now explicitly typed as `SimulationResult`

---

## [0.1.3.1] - 2026-04-17

### Changed
- UI/UX refactoring: Hero-banner with gradient, metric cards, conclusion card with
  colour-coded gradient backgrounds (green/orange/red by Kp,uu level)
- Plotly interactive charts are now the primary visualisation; matplotlib retained
  for PNG export only
- `_base_layout()` and `_plotly_axis()` helpers centralise Plotly theme config
- `_sensitivity_colors()` uses `plotly.colors.sample_colorscale` — removes
  matplotlib colormap dependency from Plotly code path
- Horizontal legend positioning in concentration chart; vertical legend in fan plot
- Download buttons (CSV + PNG) placed in 2-column layout below the chart
- Comparison table moved into `st.expander` to reduce initial page clutter
- `@st.fragment` applied to `_sensitivity_tab()` for isolated widget re-rendering

---

## [0.1.3] - 2026-04-16

### Added
- Protein-binding sliders (`fu_plasma`, `fu_brain`) for true unbound Kp,uu calculation:
  `Kp,uu = (C_brain · fu_brain) / (C_blood · fu_plasma)`
- `k_elim` slider — systemic clearance constant (switches model to open in-vivo mode)
- Comparison table for all 7 substances cached with `@st.cache_data`
- Session-state persistence: last simulation result survives widget interactions
- PNG export via matplotlib at 150 dpi with tight layout
- Sensitivity analysis tab: fan plots for k_pass, Vmax, Km with compartment selector

### Changed
- `SimulationParams` dataclass extended with `k_elim` field (default 0.0)
- `bbb_ode()` updated: elimination term `J_elim = k_elim · C_blood` subtracted from
  `dC_blood/dt`

---

## [0.1.0] - 2026-04-12

### Added
- Initial release: two-compartment BBB ODE model
  - Passive diffusion (Fick's law): `J_diff = k_pass · (C_blood − C_brain)`
  - Active P-gp efflux (Michaelis–Menten): `J_pgp = Vmax · C_brain / (Km + C_brain)`
  - Volume coefficients enforce mass conservation across compartments
- LSODA solver via `scipy.integrate.solve_ivp` (`rtol=1e-8`, `atol=1e-10`)
- `SimulationParams` and `SimulationResult` dataclasses (`bbb/core/simulator.py`)
- `Simulator` class with `run(params) → SimulationResult` method
- 7 compounds with literature-verified parameters and protein-binding values:
  Diazepam, Verapamil, Dextran, Caffeine, Morphine, Donepezil, Levetiracetam
- AUC via `np.trapezoid` (NumPy 2.0+ compatible)
- Streamlit UI with sidebar parameter controls and interactive Plotly charts
- 17 pytest tests covering mass conservation, P-gp physics, per-substance regression
- MIT License

---

[Unreleased]: https://github.com/learning2think/In-Silico-BBB/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/learning2think/In-Silico-BBB/compare/v0.1.3.1...v0.2.0
[0.1.3.1]: https://github.com/learning2think/In-Silico-BBB/compare/v0.1.3...v0.1.3.1
[0.1.3]: https://github.com/learning2think/In-Silico-BBB/compare/v0.1.0...v0.1.3
[0.1.0]: https://github.com/learning2think/In-Silico-BBB/releases/tag/v0.1.0
