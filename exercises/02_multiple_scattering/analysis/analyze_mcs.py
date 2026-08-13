#!/usr/bin/env python3
"""Analiza MCS sin consultar formulas de referencia antes de leer los eventos."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


MUON_MASS_GEV = 0.1056583755


def arguments() -> argparse.Namespace:
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=project / "data")
    parser.add_argument("--figures-dir", type=Path, default=project / "figures")
    parser.add_argument("--summary", type=Path, default=project / "data" / "summary_mcs.txt")
    return parser.parse_args()


def table(path: Path) -> dict[str, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError(f"CSV vacio: {path}")
    result: dict[str, np.ndarray] = {}
    for key in rows[0]:
        try:
            result[key] = np.asarray([float(row[key]) for row in rows])
        except ValueError:
            result[key] = np.asarray([row[key] for row in rows])
    return result


def gaussian(x: np.ndarray, amplitude: float, mean: float, sigma: float) -> np.ndarray:
    return amplitude * np.exp(-0.5*((x - mean)/sigma)**2)


def fit_power(x: np.ndarray, y: np.ndarray) -> tuple[float, float, np.ndarray]:
    coeff, covariance = curve_fit(lambda value, scale, alpha: scale*value**alpha, x, y,
                                  p0=(y[0]/x[0]**0.5, 0.5), maxfev=20_000)
    return float(coeff[0]), float(coeff[1]), np.sqrt(np.diag(covariance))


def fixed_power_scale(x: np.ndarray, y: np.ndarray, exponent: float) -> float:
    basis = x**exponent
    return float(np.dot(basis, y)/np.dot(basis, basis))


def highland(thickness_cm: np.ndarray, radiation_length_cm: np.ndarray,
             momentum_gev: np.ndarray) -> np.ndarray:
    total_energy = np.sqrt(momentum_gev**2 + MUON_MASS_GEV**2)
    beta = momentum_gev/total_energy
    ratio = thickness_cm/radiation_length_cm
    # 13.6 MeV, converted to GeV. theta0 is the width of one projected plane.
    return 0.0136/(beta*momentum_gev)*np.sqrt(ratio)*(1.0 + 0.038*np.log(ratio))


def main() -> int:
    args = arguments()
    thickness = table(args.data_dir / "thickness_scan.csv")
    energy = table(args.data_dir / "energy_scan.csv")
    events = table(args.data_dir / "angular_events.csv")
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    transmitted = events["transmitted"] > 0.5
    tx = events["theta_x_rad"][transmitted]
    ty = events["theta_y_rad"][transmitted]
    if len(tx) < 100:
        raise RuntimeError("Muy pocos eventos transmitidos para el ajuste angular")
    q16, median, q84 = np.quantile(tx, [0.16, 0.50, 0.84])
    robust_sigma = 0.5*(q84 - q16)
    fit_lo, fit_hi = median - 2.5*robust_sigma, median + 2.5*robust_sigma
    central = tx[(tx >= fit_lo) & (tx <= fit_hi)]
    counts, edges = np.histogram(central, bins=100, range=(fit_lo, fit_hi))
    centers = 0.5*(edges[1:] + edges[:-1])
    popt, pcov = curve_fit(gaussian, centers, counts,
                           p0=(counts.max(), float(central.mean()), float(central.std(ddof=1))),
                           bounds=([0.0, fit_lo, 0.0], [np.inf, fit_hi, np.inf]), maxfev=20_000)
    gaussian_sigma, gaussian_sigma_err = float(popt[2]), float(np.sqrt(pcov[2, 2]))

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    common = max(np.quantile(np.abs(np.concatenate([tx, ty])), 0.995), 4*robust_sigma)
    bins = np.linspace(-common, common, 151)
    ax.hist(tx, bins=bins, density=True, histtype="step", lw=1.6, label=r"$\theta_x$")
    ax.hist(ty, bins=bins, density=True, histtype="step", lw=1.4, label=r"$\theta_y$")
    xfit = np.linspace(fit_lo, fit_hi, 500)
    norm = 1.0/(np.sqrt(2*np.pi)*gaussian_sigma)
    ax.plot(xfit, norm*np.exp(-0.5*((xfit-popt[1])/gaussian_sigma)**2), "k--",
            label=fr"Gauss central: $\sigma$={1e3*gaussian_sigma:.3f} mrad")
    ax.axvspan(fit_lo, fit_hi, color="0.8", alpha=0.25, label="intervalo de ajuste")
    ax.set(xlabel="angulo proyectado [rad]", ylabel="densidad de probabilidad",
           title="MCS: 100 GeV, 50 cm de hierro")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(args.figures_dir / "angular_distribution.png", dpi=180)
    plt.close(fig)

    width_t = 0.5*(thickness["q84_theta_x_rad"] - thickness["q16_theta_x_rad"])
    scale_t, alpha_t, error_t = fit_power(thickness["thickness_cm"], width_t)
    scale_sqrt = fixed_power_scale(thickness["thickness_cm"], width_t, 0.5)
    highland_t = highland(thickness["thickness_cm"], thickness["radiation_length_cm"],
                          thickness["momentum_GeV_c"])
    grid_t = np.linspace(thickness["thickness_cm"].min(), thickness["thickness_cm"].max(), 400)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot(thickness["thickness_cm"], 1e3*width_t, "o", label="Geant4: semiancho 16--84 %")
    ax.plot(grid_t, 1e3*scale_t*grid_t**alpha_t, label=fr"ajuste libre $x^{{{alpha_t:.3f}}}$")
    ax.plot(grid_t, 1e3*scale_sqrt*np.sqrt(grid_t), "--", label=r"referencia $\sqrt{x}$ normalizada")
    ax.plot(thickness["thickness_cm"], 1e3*highland_t, "s:", label="Highland (sin ajustar)")
    ax.set(xlabel="espesor de Fe [cm]", ylabel="anchura proyectada [mrad]",
           title="Anchura MCS frente al espesor")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figures_dir / "width_vs_thickness.png", dpi=180)
    plt.close(fig)

    width_p = 0.5*(energy["q84_theta_x_rad"] - energy["q16_theta_x_rad"])
    # fit_power returns y=scale*p^alpha; report the conventional positive alpha in p^-alpha.
    scale_p, exponent_p, error_p = fit_power(energy["momentum_GeV_c"], width_p)
    alpha_p = -exponent_p
    scale_inv = fixed_power_scale(energy["momentum_GeV_c"], width_p, -1.0)
    highland_p = highland(energy["thickness_cm"], energy["radiation_length_cm"],
                          energy["momentum_GeV_c"])
    representative_index = int(np.argmin(np.abs(energy["energy_GeV"] - 100.0)))
    representative_highland = float(highland_p[representative_index])
    representative_relative = 100.0*(robust_sigma - representative_highland)/representative_highland
    grid_p = np.geomspace(energy["momentum_GeV_c"].min(), energy["momentum_GeV_c"].max(), 400)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.loglog(energy["momentum_GeV_c"], 1e3*width_p, "o", label="Geant4: semiancho 16--84 %")
    ax.loglog(grid_p, 1e3*scale_p*grid_p**exponent_p, label=fr"ajuste libre $p^{{-{alpha_p:.3f}}}$")
    ax.loglog(grid_p, 1e3*scale_inv/grid_p, "--", label=r"referencia $1/p$ normalizada")
    ax.loglog(energy["momentum_GeV_c"], 1e3*highland_p, "s:", label="Highland (sin ajustar)")
    ax.set(xlabel="momento [GeV/c]", ylabel="anchura proyectada [mrad]",
           title="Anchura MCS frente al momento")
    ax.grid(alpha=0.25, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figures_dir / "width_vs_momentum.png", dpi=180)
    plt.close(fig)

    robust_sigma_y = float(0.5*(np.quantile(ty, 0.84) - np.quantile(ty, 0.16)))
    symmetry_ratio = robust_sigma/robust_sigma_y
    rms_tail_ratio = float(np.std(tx, ddof=1)/np.std(ty, ddof=1))
    mean_x_z = float(abs(tx.mean())/(np.std(tx, ddof=1)/np.sqrt(len(tx))))
    mean_y_z = float(abs(ty.mean())/(np.std(ty, ddof=1)/np.sqrt(len(ty))))
    checks = {
        "simetria_anchuras_0.95_a_1.05": 0.95 <= symmetry_ratio <= 1.05,
        "media_x_compatible_5SEM": mean_x_z <= 5.0,
        "media_y_compatible_5SEM": mean_y_z <= 5.0,
        "anchura_crece_con_espesor": bool(np.all(np.diff(width_t) > 0.0)),
        "anchura_disminuye_con_momento": bool(np.all(np.diff(width_p) < 0.0)),
        "orden_Highland_factor_0.5_a_2": bool(np.all((width_t/highland_t > 0.5) & (width_t/highland_t < 2.0))),
    }
    lines = [
        "EXPERIMENTO 2 — DISPERSION MULTIPLE DE COULOMB",
        "",
        f"Eventos representativos transmitidos: {len(tx)} / {len(events['transmitted'])}",
        f"Intervalo del ajuste gaussiano central: [{fit_lo:.8g}, {fit_hi:.8g}] rad",
        f"sigma gaussiana central = {gaussian_sigma:.8g} +- {gaussian_sigma_err:.2g} rad",
        f"sigma robusta (q84-q16)/2 = {robust_sigma:.8g} rad",
        f"media theta_x = {tx.mean():.8g} rad; media theta_y = {ty.mean():.8g} rad",
        f"razon de anchuras centrales robustas x/y = {symmetry_ratio:.6f}",
        f"razon std global x/y (incluye colas raras) = {rms_tail_ratio:.6f}",
        "",
        f"Ajuste espesor sigma=A*x^alpha: A={scale_t:.8g} rad/cm^alpha; alpha={alpha_t:.5f} +- {error_t[1]:.5f} (esperado ~0.5)",
        f"Ajuste momento sigma=B*p^-alpha: B={scale_p:.8g}; alpha={alpha_p:.5f} +- {error_p[1]:.5f} (esperado ~1)",
        f"Geant4/Highland en barrido de espesor: min={np.min(width_t/highland_t):.4f}, max={np.max(width_t/highland_t):.4f}",
        f"alpha_thickness = {alpha_t:.8g}",
        f"uncertainty_alpha_thickness = {error_t[1]:.8g}",
        f"alpha_momentum = {alpha_p:.8g}",
        f"uncertainty_alpha_momentum = {error_p[1]:.8g}",
        f"sigma_theta_representative_rad = {robust_sigma:.9g}",
        f"highland_theta_representative_rad = {representative_highland:.9g}",
        f"relative_difference_percent = {representative_relative:.6g}",
        "Highland se evaluo solo despues de producir/leer los eventos: 13.6 MeV/(beta*p)*sqrt(x/X0)*[1+0.038 ln(x/X0)].",
        "theta0 de Highland es la anchura de UNA proyeccion; no es el RMS del angulo polar bidimensional.",
        "La anchura usada en los barridos es central y robusta: (q84-q16)/2; las colas no gaussianas permanecen visibles en la figura angular.",
        "",
        "VALIDACIONES",
    ]
    lines.extend(f"{'PASS' if passed else 'FAIL'}: {name}" for name, passed in checks.items())
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Analisis MCS escrito en {args.summary}")
    print(f"Figuras: {args.figures_dir}")
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
