#!/usr/bin/env python3
"""Ajusta la atenuacion usando exclusivamente transmission_scan.csv."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit, minimize_scalar


def arguments() -> argparse.Namespace:
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=project / "data" / "transmission_scan.csv")
    parser.add_argument("--summary", type=Path, default=project / "data" / "summary_A.txt")
    parser.add_argument("--figure-dir", type=Path, default=project / "figures")
    return parser.parse_args()


def exponential(x: np.ndarray, mu: float) -> np.ndarray:
    return np.exp(-mu * x)


def binomial_mle(x: np.ndarray, n: np.ndarray, k: np.ndarray) -> tuple[float, float]:
    def nll(mu: float) -> float:
        p = np.clip(np.exp(-mu * x), 1e-15, 1.0 - 1e-15)
        return float(-np.sum(k * np.log(p) + (n - k) * np.log1p(-p)))

    result = minimize_scalar(nll, bounds=(1e-12, 10.0), method="bounded")
    if not result.success:
        raise RuntimeError(f"Fallo la maxima verosimilitud: {result.message}")
    mu = float(result.x)
    p = np.exp(-mu * x)
    fisher_information = np.sum(n * x * x * p / (1.0 - p))
    return mu, float(1.0 / np.sqrt(fisher_information))


def main() -> int:
    args = arguments()
    table = np.genfromtxt(args.input, delimiter=",", names=True, dtype=None, encoding="utf-8")
    table = np.atleast_1d(table)
    required = {
        "thickness_cm", "N0", "N_transmitted", "N_interacted", "transmission",
        "transmission_stat_error", "atomic_number_density_cm3", "energy_keV",
        "geant4_compton_sigma_cm2_atom", "geant4_compton_mu_cm_inv",
    }
    missing = required - set(table.dtype.names or ())
    if missing:
        raise RuntimeError(f"Faltan columnas: {sorted(missing)}")

    order = np.argsort(table["thickness_cm"])
    x = np.asarray(table["thickness_cm"][order], float)
    n = np.asarray(table["N0"][order], float)
    k = np.asarray(table["N_transmitted"][order], float)
    t = np.asarray(table["transmission"][order], float)
    st = np.asarray(table["transmission_stat_error"][order], float)
    if np.any((t <= 0.0) | (t >= 1.0)):
        raise RuntimeError("La validacion 0 < T < 1 fallo")
    if np.any(np.asarray(table["N_interacted"][order], int) + k.astype(int) != n.astype(int)):
        raise RuntimeError("N_transmitted + N_interacted != N0")
    increases = np.diff(t)
    increase_sigma = np.sqrt(st[:-1] ** 2 + st[1:] ** 2)
    if np.any(increases > 3.0 * increase_sigma):
        raise RuntimeError("La transmision aumenta mas de 3 sigma entre espesores consecutivos")

    mu, s_mu = binomial_mle(x, n, k)
    popt, pcov = curve_fit(exponential, x, t, sigma=st, absolute_sigma=True, p0=[mu], bounds=(0, np.inf))
    mu_exp, s_mu_exp = float(popt[0]), float(np.sqrt(pcov[0, 0]))
    y = np.log(t)
    sy = st / t
    weights = 1.0 / sy**2
    slope = float(np.sum(weights * x * y) / np.sum(weights * x * x))
    s_slope = float(1.0 / np.sqrt(np.sum(weights * x * x)))
    mu_log, s_mu_log = -slope, s_slope

    atom_density_values = np.asarray(table["atomic_number_density_cm3"], float)
    atom_density = float(np.mean(atom_density_values))
    if not np.allclose(atom_density_values, atom_density, rtol=1e-10):
        raise RuntimeError("La densidad atomica cambia entre corridas")
    mean_free_path = 1.0 / mu
    s_mean_free_path = s_mu / mu**2
    sigma_cm2 = mu / atom_density
    s_sigma_cm2 = s_mu / atom_density
    sigma_barn = sigma_cm2 / 1e-24
    s_sigma_barn = s_sigma_cm2 / 1e-24
    reference_sigma = float(np.mean(np.asarray(table["geant4_compton_sigma_cm2_atom"], float)))
    reference_mu = float(np.mean(np.asarray(table["geant4_compton_mu_cm_inv"], float)))
    relative_difference = 100.0 * (sigma_cm2 - reference_sigma) / reference_sigma
    if mu <= 0 or mean_free_path <= 0 or sigma_cm2 <= 0:
        raise RuntimeError("mu, lambda y sigma deben ser positivos")
    if abs(relative_difference) > 5.0:
        raise RuntimeError("La seccion reconstruida difiere mas de 5 % de la referencia Geant4")

    args.figure_dir.mkdir(parents=True, exist_ok=True)
    grid = np.linspace(0.0, 1.05 * np.max(x), 400)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.errorbar(x, t, yerr=st, fmt="o", capsize=3, label="Monte Carlo")
    ax.plot(grid, exponential(grid, mu), label=rf"MLE binomial: $\mu={mu:.5f}\,\mathrm{{cm}}^{{-1}}$")
    ax.set(xlabel="Espesor x [cm]", ylabel="Transmisión T", ylim=(0, 1.03))
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figure_dir / "transmission_vs_thickness.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.errorbar(x, y, yerr=sy, fmt="o", capsize=3, label=r"$\ln(T)$ simulado")
    ax.plot(grid, -mu_log * grid, label=rf"Ajuste: $\ln T=-({mu_log:.5f})x$")
    ax.set(xlabel="Espesor x [cm]", ylabel=r"$\ln(T)$")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figure_dir / "log_transmission_vs_thickness.png", dpi=180)
    plt.close(fig)

    material = str(np.atleast_1d(table["material"])[0]) if "material" in table.dtype.names else "desconocido"
    energy = float(np.mean(np.asarray(table["energy_keV"], float)))
    summary = f"""Experimento 1A - transmision Compton
input_csv = {args.input.resolve()}
material = {material}
energy_keV = {energy:.9g}
number_of_thicknesses = {len(x)}
fit_principal = maxima_verosimilitud_binomial

mu_cm^-1 = {mu:.12g}
uncertainty_mu_cm^-1 = {s_mu:.12g}
lambda_cm = {mean_free_path:.12g}
uncertainty_lambda_cm = {s_mean_free_path:.12g}
sigma_cm2_per_atom = {sigma_cm2:.12g}
sigma_barn_per_atom = {sigma_barn:.12g}
uncertainty_sigma_cm2_per_atom = {s_sigma_cm2:.12g}
uncertainty_sigma_barn_per_atom = {s_sigma_barn:.12g}

weighted_exponential_mu_cm^-1 = {mu_exp:.12g}
weighted_exponential_uncertainty_mu_cm^-1 = {s_mu_exp:.12g}
linear_log_mu_cm^-1 = {mu_log:.12g}
linear_log_uncertainty_mu_cm^-1 = {s_mu_log:.12g}

geant4_reference_mu_cm^-1 = {reference_mu:.12g}
geant4_reference_sigma_cm2_per_atom = {reference_sigma:.12g}
geant4_reference_sigma_barn_per_atom = {reference_sigma/1e-24:.12g}
relative_difference_percent = {relative_difference:.9g}

Nota: la referencia de G4EmCalculator se consulta solo despues del ajuste; no entra en el fit.
"""
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(summary, encoding="utf-8")
    print(summary)
    print(f"Figuras: {args.figure_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
