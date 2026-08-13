#!/usr/bin/env python3
"""Analiza perdida de energia, poder de frenado y canales de TestEm18."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


def arguments() -> argparse.Namespace:
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=project / "data")
    parser.add_argument("--figures-dir", type=Path, default=project / "figures")
    parser.add_argument("--summary", type=Path, default=project / "data" / "summary_energy_loss.txt")
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


def main() -> int:
    args = arguments()
    thickness = table(args.data_dir / "thickness_scan.csv")
    energy = table(args.data_dir / "energy_scan.csv")
    events = table(args.data_dir / "energy_loss_events.csv")
    processes = table(args.data_dir / "process_contributions.csv")
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    # Simulation observables are established before looking at the separate
    # G4EmCalculator reference column.
    loss = events["energy_loss_MeV"]
    deposited = events["energy_deposited_MeV"]
    secondary_transferred = events["secondary_energy_transferred_MeV"]
    max_plot = np.quantile(loss, 0.995)
    bins = np.linspace(0.0, max_plot, 140)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.hist(loss, bins=bins, density=True, histtype="step", lw=1.6,
            label="perdida del primario $E_i-E_f$")
    ax.hist(deposited, bins=bins, density=True, histtype="step", lw=1.5,
            label="deposito local (primario + secundarios)")
    ax.axvline(np.mean(loss), color="C0", ls="--", alpha=0.8)
    ax.axvline(np.median(loss), color="C0", ls=":", alpha=0.8)
    ax.set(xlabel="energia [MeV]", ylabel="densidad de probabilidad",
           title="Muon de 3 GeV en 10 cm de agua")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figures_dir / "energy_loss_distribution.png", dpi=180)
    plt.close(fig)

    small = thickness["thickness_cm"] <= 10.0
    xsmall = thickness["thickness_cm"][small]
    ysmall = thickness["mean_energy_loss_MeV"][small]
    semsmall = thickness["sem_energy_loss_MeV"][small]
    coeff, covariance = curve_fit(lambda x, slope, intercept: slope*x + intercept,
                                  xsmall, ysmall, sigma=semsmall, absolute_sigma=True)
    slope, intercept = map(float, coeff)
    slope_err, intercept_err = np.sqrt(np.diag(covariance))
    density = float(thickness["density_g_cm3"][0])
    grid = np.linspace(0.0, thickness["thickness_cm"].max(), 300)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.errorbar(thickness["thickness_cm"], thickness["mean_energy_loss_MeV"],
                yerr=thickness["sem_energy_loss_MeV"], fmt="o", capsize=3, label="Geant4")
    ax.plot(grid, slope*grid + intercept, label="ajuste lineal con x <= 10 cm")
    ax.axvspan(0, 10, color="0.8", alpha=0.25, label="intervalo ajustado")
    ax.set(xlabel="espesor de agua [cm]", ylabel="perdida media [MeV]",
           title="Perdida media frente al espesor (3 GeV)")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figures_dir / "mean_energy_loss_vs_thickness.png", dpi=180)
    plt.close(fig)

    simulated_dedx = energy["mean_dedx_MeV_cm"]
    simulated_dedx_sem = energy["sem_energy_loss_MeV"]/energy["thickness_cm"]
    # Only now use the G4EmCalculator values emitted after each completed run.
    reference_dedx = energy["reference_dedx_MeV_cm"]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.errorbar(energy["beta_gamma"], simulated_dedx, yerr=simulated_dedx_sem,
                fmt="o-", capsize=3, label="eventos Geant4, media ± SEM")
    ax.semilogx(energy["beta_gamma"], reference_dedx, "s--", label="G4EmCalculator")
    ax.set_xscale("log")
    ax.set(xlabel=r"$\beta\gamma$", ylabel=r"$\langle\Delta E\rangle/x$ [MeV/cm]",
           title="Poder de frenado de muones en agua")
    ax.grid(alpha=0.25, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figures_dir / "dedx_vs_energy.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.semilogx(processes["energy_GeV"], processes["fraction_ionization"], "o-", label="ionizacion")
    ax.semilogx(processes["energy_GeV"], processes["fraction_bremsstrahlung"], "o-", label="bremsstrahlung")
    ax.semilogx(processes["energy_GeV"], processes["fraction_pair_production"], "o-", label="produccion de pares")
    ax.semilogx(processes["energy_GeV"], processes["fraction_other"], "o-", label="otros")
    ax.set(xlabel="energia cinetica [GeV]", ylabel="fraccion de la perdida media",
           title="Contribuciones por proceso en 1 cm de agua", ylim=(-0.02, 1.02))
    ax.grid(alpha=0.25, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figures_dir / "process_contributions_vs_energy.png", dpi=180)
    plt.close(fig)

    ratio = simulated_dedx/reference_dedx
    energy_3_index = int(np.argmin(np.abs(energy["energy_GeV"] - 3.0)))
    reference_3 = float(reference_dedx[energy_3_index])
    relative_3 = 100.0*(slope - reference_3)/reference_3
    minimum_index = int(np.argmin(simulated_dedx))
    checks = {
        "perdidas_no_negativas": bool(np.all(loss >= -2.e-6)),
        "energia_final_no_supera_inicial": bool(np.all(events["final_energy_MeV"] <= events["initial_energy_MeV"] + 2.e-6)),
        "perdida_media_crece_con_espesor": bool(np.all(np.diff(thickness["mean_energy_loss_MeV"]) > 0.0)),
        "muones_0.2GeV_atraviesan_1cm": bool(energy["fraction_stopped"][0] == 0.0),
        "balance_procesos": bool(np.allclose(
            processes["fraction_ionization"] + processes["fraction_bremsstrahlung"]
            + processes["fraction_pair_production"] + processes["fraction_other"], 1.0,
            rtol=1.e-8, atol=1.e-8)),
        # FAST conserva las colas radiativas y puede fluctuar mucho en los
        # puntos de energía alta; el smoke test comprueba solo el orden físico.
        "orden_G4EmCalculator_factor_0.3_a_2": bool(np.all((ratio > 0.3) & (ratio < 2.0))),
    }
    lines = [
        "EXPERIMENTO 3 — PERDIDA DE ENERGIA DE MUONES",
        "",
        f"Ajuste delgado (1, 2, 5 y 10 cm): DeltaE = a*x + b",
        f"a = dE/dx = {slope:.8g} +- {slope_err:.2g} MeV/cm",
        f"b = {intercept:.8g} +- {intercept_err:.2g} MeV",
        f"poder de frenado masico a/rho = {slope/density:.8g} +- {slope_err/density:.2g} MeV cm2/g",
        f"dEdx_measured_MeV_cm = {slope:.9g}",
        f"dEdx_measured_MeV_cm2_g = {slope/density:.9g}",
        f"dEdx_geant4_reference_MeV_cm_at_3GeV = {reference_3:.9g}",
        f"relative_difference_percent = {relative_3:.6g}",
        f"energy_of_minimum_observed_GeV = {energy['energy_GeV'][minimum_index]:.9g}",
        "",
        f"Configuracion representativa: 3 GeV, 10 cm; N={len(loss)}",
        f"perdida primaria: media={loss.mean():.8g} MeV, std={loss.std(ddof=1):.8g} MeV, SEM={loss.std(ddof=1)/np.sqrt(len(loss)):.8g} MeV, mediana={np.median(loss):.8g} MeV, q16={np.quantile(loss, 0.16):.8g} MeV, q84={np.quantile(loss, 0.84):.8g} MeV",
        f"deposito local: media={deposited.mean():.8g} MeV; energia transferida a secundarios en su creacion: media={secondary_transferred.mean():.8g} MeV",
        "La perdida primaria es E_in-E_out. El deposito local suma energia depositada dentro del cubo por el primario y los secundarios rastreados; no incluye energia que escapa.",
        "Los barridos matan secundarios solo despues de registrar su energia de creacion: conservan la perdida total del primario y reducen el costo; el archivo representativo si los rastrea.",
        "",
        f"Geant4/G4EmCalculator para 1 cm: min={ratio.min():.5f}, max={ratio.max():.5f}",
        "La referencia ComputeTotalDEDX se calculo en EndOfRunAction, despues de completar los eventos, y no intervino en el ajuste lineal.",
        "Las colas radiativas largas son parte de la fisica: la media y su SEM pueden converger lentamente incluso con muchos eventos.",
        "",
        "VALIDACIONES",
    ]
    lines.extend(f"{'PASS' if passed else 'FAIL'}: {name}" for name, passed in checks.items())
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Analisis de perdida de energia escrito en {args.summary}")
    print(f"Figuras: {args.figures_dir}")
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
