#!/usr/bin/env python3
"""Recupera m_e c^2 de la correlacion Compton evento a evento."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares


REFERENCE_MASS_KEV = 510.99895


def arguments() -> argparse.Namespace:
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=project / "data" / "compton_events.csv")
    parser.add_argument("--summary", type=Path, default=project / "data" / "summary_B.txt")
    parser.add_argument("--figure-dir", type=Path, default=project / "figures")
    parser.add_argument("--energy-resolution-frac", type=float, default=0.0)
    parser.add_argument("--angular-resolution-deg", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=314159)
    return parser.parse_args()


def model(cos_theta: np.ndarray, e0: float, mass: float) -> np.ndarray:
    return e0 * mass / (mass + e0 * (1.0 - cos_theta))


def nonlinear_fit(cos_theta: np.ndarray, energy: np.ndarray, e0: float) -> tuple[float, float]:
    fit = least_squares(
        lambda parameter: model(cos_theta, e0, parameter[0]) - energy,
        x0=np.array([500.0]),
        bounds=(np.array([1e-9]), np.array([np.inf])),
        xtol=1e-14,
        ftol=1e-14,
        gtol=1e-14,
    )
    mass = float(fit.x[0])
    residual = fit.fun
    dof = max(1, len(energy) - 1)
    variance = float(np.dot(residual, residual) / dof)
    information = float(np.dot(fit.jac[:, 0], fit.jac[:, 0]))
    uncertainty = float(np.sqrt(variance / information)) if information > 0 else float("nan")
    return mass, uncertainty


def main() -> int:
    args = arguments()
    if args.energy_resolution_frac < 0 or args.angular_resolution_deg < 0:
        raise SystemExit("Las resoluciones no pueden ser negativas")
    data = np.genfromtxt(args.input, delimiter=",", names=True, dtype=None, encoding="utf-8")
    data = np.atleast_1d(data)
    required = {
        "event_id", "E0_keV", "Egamma_scattered_keV", "cos_theta", "theta_deg",
        "electron_kinetic_energy_keV", "process_name", "ux_initial", "uy_initial",
        "uz_initial", "ux_final", "uy_final", "uz_final",
        "local_energy_deposit_keV", "other_secondary_energy_keV",
    }
    missing = required - set(data.dtype.names or ())
    if missing:
        raise RuntimeError(f"Faltan columnas: {sorted(missing)}")

    e0_all = np.asarray(data["E0_keV"], float)
    energy_raw = np.asarray(data["Egamma_scattered_keV"], float)
    cos_raw = np.asarray(data["cos_theta"], float)
    theta_raw = np.asarray(data["theta_deg"], float)
    electron = np.asarray(data["electron_kinetic_energy_keV"], float)
    local_deposit = np.asarray(data["local_energy_deposit_keV"], float)
    other_secondary = np.asarray(data["other_secondary_energy_keV"], float)
    process = np.asarray(data["process_name"], str)
    e0 = float(np.mean(e0_all))
    if not np.allclose(e0_all, e0, rtol=0, atol=1e-9):
        raise RuntimeError("E0 no es constante")
    if len(data) == 0 or np.any((energy_raw <= 0) | (energy_raw > e0_all + 1e-8)):
        raise RuntimeError("Fallo 0 < Egamma_scattered <= E0")
    if np.any((cos_raw < -1.0 - 1e-12) | (cos_raw > 1.0 + 1e-12)):
        raise RuntimeError("Fallo -1 <= cos_theta <= 1")
    if np.any(electron < -1e-9):
        raise RuntimeError("Se encontro energia cinetica del electron negativa")
    if np.any(process != "compt"):
        raise RuntimeError(f"Procesos inesperados: {np.unique(process)}")

    electron_only_residual = e0_all - energy_raw - electron
    energy_residual = electron_only_residual - local_deposit - other_secondary
    if np.max(np.abs(energy_residual)) > 0.02:
        raise RuntimeError("El balance completo de energia falla por mas de 0.02 keV")
    if np.min(electron_only_residual) < -0.02 or np.max(electron_only_residual) > 2.0:
        raise RuntimeError("La energia atomica no contabilizada por gamma+electron es inesperada")
    expected_raw = model(cos_raw, e0, REFERENCE_MASS_KEV)
    compton_residual = energy_raw - expected_raw
    initial = np.column_stack([data["ux_initial"], data["uy_initial"], data["uz_initial"]]).astype(float)
    final = np.column_stack([data["ux_final"], data["uy_final"], data["uz_final"]]).astype(float)
    if not np.allclose(np.linalg.norm(initial, axis=1), 1.0, atol=2e-6) or not np.allclose(
        np.linalg.norm(final, axis=1), 1.0, atol=2e-6
    ):
        raise RuntimeError("Las direcciones guardadas no son unitarias")
    dot = np.sum(initial * final, axis=1)
    if not np.allclose(dot, cos_raw, atol=2e-12):
        raise RuntimeError("cos_theta no coincide con el producto escalar guardado")
    # G4Tools CSV uses six significant digits. Near cos(theta)=+/-1, arccos
    # amplifies that rounding, so a 0.01 degree serialization tolerance is used.
    if not np.allclose(np.degrees(np.arccos(np.clip(cos_raw, -1, 1))), theta_raw, atol=1e-2):
        raise RuntimeError("theta_deg no coincide con arccos(cos_theta)")

    rng = np.random.default_rng(args.seed)
    energy = energy_raw.copy()
    theta = theta_raw.copy()
    if args.energy_resolution_frac > 0:
        energy += rng.normal(0.0, args.energy_resolution_frac * energy)
    if args.angular_resolution_deg > 0:
        theta += rng.normal(0.0, args.angular_resolution_deg, size=len(theta))
    valid = energy > 0
    energy = energy[valid]
    theta = theta[valid]
    cos_theta = np.cos(np.radians(theta))
    if len(energy) < 3:
        raise RuntimeError("Quedaron muy pocos eventos validos despues del smearing")

    mass_nl, uncertainty_nl = nonlinear_fit(cos_theta, energy, e0)
    x = 1.0 - cos_theta
    y = 1.0 / energy - 1.0 / e0
    slope = float(np.dot(x, y) / np.dot(x, x))
    linear_residual = y - slope * x
    linear_variance = float(np.dot(linear_residual, linear_residual) / max(1, len(x) - 1))
    uncertainty_slope = float(np.sqrt(linear_variance / np.dot(x, x)))
    mass_linear = 1.0 / slope
    uncertainty_linear = uncertainty_slope / slope**2

    design = np.column_stack([x, np.ones_like(x)])
    slope_free, intercept_free = np.linalg.lstsq(design, y, rcond=None)[0]
    free_residual = y - (slope_free * x + intercept_free)
    free_variance = float(np.dot(free_residual, free_residual) / max(1, len(x) - 2))
    free_covariance = free_variance * np.linalg.inv(design.T @ design)
    mass_linear_free = 1.0 / slope_free
    uncertainty_linear_free = np.sqrt(free_covariance[0, 0]) / slope_free**2
    relative_difference = 100.0 * (mass_nl - REFERENCE_MASS_KEV) / REFERENCE_MASS_KEV
    if abs(relative_difference) > 5.0:
        raise RuntimeError("El ajuste no recupera m_e c^2 dentro de 5 %")

    args.figure_dir.mkdir(parents=True, exist_ok=True)
    angle_grid = np.linspace(0.0, 180.0, 500)
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    image = ax.hexbin(theta, energy, gridsize=110, mincnt=1, bins="log", cmap="viridis")
    ax.plot(angle_grid, model(np.cos(np.radians(angle_grid)), e0, mass_nl), color="crimson", lw=2,
            label=rf"Ajuste: $M={mass_nl:.6f}$ keV")
    fig.colorbar(image, ax=ax, label="Eventos por celda (escala log)")
    ax.set(xlabel=r"Ángulo del gamma $\theta$ [grados]", ylabel=r"$E_\gamma'$ [keV]")
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figure_dir / "compton_energy_vs_angle.png", dpi=180)
    plt.close(fig)

    plot_index = np.linspace(0, len(x) - 1, min(20_000, len(x)), dtype=int)
    x_grid = np.linspace(0.0, 2.0, 400)
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    ax.scatter(x[plot_index], y[plot_index], s=2, alpha=0.16, label="Eventos (submuestra visual)")
    ax.plot(x_grid, slope * x_grid, color="crimson", lw=2,
            label=rf"Intercepto 0: pendiente $=1/M$, $M={mass_linear:.6f}$ keV")
    ax.plot(x_grid, slope_free * x_grid + intercept_free, "--", color="black", lw=1.5,
            label="Diagnóstico con intercepto libre")
    ax.set(xlabel=r"$X=1-\cos\theta$", ylabel=r"$Y=1/E_\gamma'-1/E_0$ [keV$^{-1}$]")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figure_dir / "compton_linearized.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.hist(theta_raw, bins=100, histtype="stepfilled", alpha=0.75)
    ax.set(xlabel=r"Ángulo del gamma $\theta$ [grados]", ylabel="Eventos")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(args.figure_dir / "compton_angle_distribution.png", dpi=180)
    plt.close(fig)

    ideal = args.energy_resolution_frac == 0 and args.angular_resolution_deg == 0
    explanation = (
        "No se aplico resolucion instrumental. La incertidumbre no colapsa a cero porque el "
        "G4KleinNishinaModel usado aqui incluye electrones ligados y ensanchamiento Doppler; "
        "cuantifica la dispersion Monte Carlo de ese modelo, no una resolucion del detector."
        if ideal else
        "Las incertidumbres incluyen el smearing instrumental artificial aplicado solo durante el analisis."
    )
    summary = f"""Experimento 1B - cinematica Compton
input_csv = {args.input.resolve()}
E0_keV = {e0:.12g}
numero_de_eventos = {len(data)}
numero_de_eventos_ajustados = {len(energy)}
energy_resolution_frac = {args.energy_resolution_frac:.12g}
angular_resolution_deg = {args.angular_resolution_deg:.12g}
smearing_seed = {args.seed}

M_nonlinear_fit_keV = {mass_nl:.12g}
uncertainty_M_nonlinear_keV = {uncertainty_nl:.12g}
M_linear_fit_keV = {mass_linear:.12g}
uncertainty_M_linear_keV = {uncertainty_linear:.12g}
M_linear_free_intercept_keV = {mass_linear_free:.12g}
uncertainty_M_linear_free_intercept_keV = {uncertainty_linear_free:.12g}
linear_free_intercept_keV^-1 = {intercept_free:.12g}

reference_electron_rest_energy_keV = {REFERENCE_MASS_KEV:.8f}
relative_difference_percent = {relative_difference:.12g}
max_abs_complete_energy_conservation_residual_keV = {np.max(np.abs(energy_residual)):.12g}
max_energy_not_in_gamma_plus_electron_keV = {np.max(electron_only_residual):.12g}
max_abs_compton_relation_residual_keV = {np.max(np.abs(compton_residual)):.12g}
rms_compton_relation_residual_keV = {np.sqrt(np.mean(compton_residual**2)):.12g}

{explanation}
El G4KleinNishinaModel de esta version incluye capas ligadas y movimiento inicial del electron;
por ello la curva de electron libre se ensancha aun sin resolucion instrumental.
"""
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(summary, encoding="utf-8")
    print(summary)
    print(f"Figuras: {args.figure_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
