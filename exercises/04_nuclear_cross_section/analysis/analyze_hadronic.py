#!/usr/bin/env python3
"""Estima lambda y sigma de captura mediante MLE con censura derecha."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BARN_CM2 = 1.e-24


def arguments() -> argparse.Namespace:
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=project / "data")
    parser.add_argument("--figures-dir", type=Path, default=project / "figures")
    parser.add_argument("--summary", type=Path, default=project / "data" / "summary_hadronic.txt")
    return parser.parse_args()


def main() -> int:
    args = arguments()
    event_path = args.data_dir / "hadronic_events.csv"
    with event_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError(f"CSV vacio: {event_path}")
    paths = np.asarray([float(row["path_length_cm"]) for row in rows])
    interacted = np.asarray([int(row["interacted"]) for row in rows], dtype=bool)
    escaped = np.asarray([int(row["escaped"]) for row in rows], dtype=bool)
    number_density = float(rows[0]["number_density_cm3"])
    n_interacted = int(interacted.sum())
    n_escaped = int(escaped.sum())
    if n_interacted == 0:
        raise RuntimeError("No hay interacciones para el MLE")

    # Unbinned censored exponential likelihood:
    # L proportional lambda^(-Nint) exp[-sum(all exposures)/lambda].
    total_exposure = float(paths.sum())
    mean_free_path = total_exposure/n_interacted
    macroscopic_xs = 1.0/mean_free_path
    microscopic_cm2 = macroscopic_xs/number_density
    microscopic_barn = microscopic_cm2/BARN_CM2
    relative_stat = 1.0/math.sqrt(n_interacted)
    lambda_sem = mean_free_path*relative_stat
    sigma_sem_barn = microscopic_barn*relative_stat

    # Empirical survival includes censored particles in the risk set.  All
    # censoring occurs at the common exit plane, so this is Kaplan-Meier here.
    max_path = float(paths.max())
    grid = np.linspace(0.0, max_path, 400)
    empirical_survival = np.asarray([np.mean(paths >= value) for value in grid])
    fitted_survival = np.exp(-grid/mean_free_path)
    survival_max_abs = float(np.max(np.abs(empirical_survival - fitted_survival)))

    args.figures_dir.mkdir(parents=True, exist_ok=True)
    bins = np.linspace(0.0, max_path, 80)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    weights = np.full(n_interacted, 1.0/len(rows))
    ax.hist(paths[interacted], bins=bins, weights=weights/(bins[1]-bins[0]),
            histtype="step", lw=1.6, label="capturas por primario y cm")
    x = np.linspace(0.0, max_path, 500)
    ax.plot(x, np.exp(-x/mean_free_path)/mean_free_path, label="MLE exponencial censurado")
    if n_escaped:
        ax.axvline(np.median(paths[escaped]), color="C3", ls=":", label=f"salida: {n_escaped} censurados")
    ax.set(xlabel="distancia hasta captura o salida [cm]", ylabel="densidad por primario [1/cm]",
           title=r"Captura $n+{}^{10}$B a 1 eV")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figures_dir / "interaction_length_distribution.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.semilogy(grid, np.maximum(empirical_survival, 0.5/len(rows)), label="supervivencia empirica/Kaplan-Meier")
    ax.semilogy(grid, fitted_survival, "--", label=fr"$e^{{-x/\hat{{\lambda}}}}$")
    ax.set(xlabel="distancia [cm]", ylabel="S(x)", title="Ley exponencial y censura a la salida")
    ax.grid(alpha=0.25, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.figures_dir / "survival_probability.png", dpi=180)
    plt.close(fig)

    # Reference values are loaded only after reconstructing lambda and sigma.
    metadata = json.loads((args.data_dir / "run_metadata.json").read_text(encoding="utf-8"))
    reference_barn = float(metadata["reference_microscopic_barn"])
    reference_macro = float(metadata["reference_macroscopic_cm-1"])
    sigma_ratio = microscopic_barn/reference_barn
    result_fields = (
        "N_generated", "N_interacted", "N_escaped_right_censored",
        "total_exposure_cm", "mean_free_path_cm", "mean_free_path_sem_cm",
        "number_density_cm3", "macroscopic_cross_section_cm-1",
        "microscopic_cross_section_barn", "microscopic_cross_section_sem_barn",
        "reference_macroscopic_cm-1", "reference_microscopic_barn",
    )
    result = {
        "N_generated": len(rows), "N_interacted": n_interacted,
        "N_escaped_right_censored": n_escaped, "total_exposure_cm": total_exposure,
        "mean_free_path_cm": mean_free_path, "mean_free_path_sem_cm": lambda_sem,
        "number_density_cm3": number_density, "macroscopic_cross_section_cm-1": macroscopic_xs,
        "microscopic_cross_section_barn": microscopic_barn,
        "microscopic_cross_section_sem_barn": sigma_sem_barn,
        "reference_macroscopic_cm-1": reference_macro,
        "reference_microscopic_barn": reference_barn,
    }
    with (args.data_dir / "cross_section_result.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=result_fields)
        writer.writeheader()
        writer.writerow(result)

    processes = {row["process_name"] for row in rows if int(row["interacted"])}
    checks = {
        "clasificacion_interaccion_o_escape": bool(np.all(interacted.astype(int) + escaped.astype(int) == 1)),
        "unico_canal_nCapture": processes == {"nCapture"},
        "distancias_positivas": bool(np.all(paths > 0.0)),
        "supervivencia_exponencial_max_abs_menor_0.02": survival_max_abs < 0.02,
        "acuerdo_ProcessStore_15porciento": 0.85 < sigma_ratio < 1.15,
    }
    lines = [
        "EXPERIMENTO 4 — SECCION EFICAZ NUCLEAR POR LONGITUD LIBRE",
        "",
        "Reaccion elegida: captura de neutrones de 1 eV en material isotopico puro 10B; unico proceso activo: nCapture.",
        "Fisica: Hadr03 con G4HadronPhysicsQGSP_BIC_HP; a 1 eV usa NeutronHPCapture y el conjunto NeutronHPCaptureXS (el dump tambien registra G4NeutronCaptureXS).",
        f"N generados={len(rows)}, capturados={n_interacted}, escapados/censurados={n_escaped}",
        f"exposicion total (interacciones + censuras)={total_exposure:.9g} cm",
        f"lambda_MLE={mean_free_path:.9g} +- {lambda_sem:.3g} cm (incertidumbre estadistica asintotica)",
        f"densidad numerica n={number_density:.9g} atomos/cm3",
        f"Sigma=1/lambda={macroscopic_xs:.9g} cm^-1",
        f"sigma=1/(n*lambda)={microscopic_barn:.9g} +- {sigma_sem_barn:.3g} barn",
        f"particle = neutron",
        f"energy = 1 eV",
        f"material = B10 isotopico puro",
        f"process = nCapture",
        f"lambda_cm = {mean_free_path:.9g}",
        f"uncertainty_lambda_cm = {lambda_sem:.9g}",
        f"macroscopic_cross_section_cm-1 = {macroscopic_xs:.9g}",
        f"microscopic_cross_section_cm2 = {microscopic_cm2:.9g}",
        f"microscopic_cross_section_barn = {microscopic_barn:.9g}",
        f"geant4_reference_cross_section_barn = {reference_barn:.9g}",
        f"relative_difference_percent = {100.0*(sigma_ratio-1.0):.6g}",
        "",
        f"G4HadronicProcessStore (consultado tras los eventos): {reference_barn:.9g} barn; razon MLE/referencia={sigma_ratio:.6f}",
        f"max |S_empirica-exp(-x/lambda)|={survival_max_abs:.6g}",
        "MLE con censura: lambda=sum_i(t_i)/N_interacciones. Cada escape aporta su longitud recorrida a la exposicion y no se elimina.",
        "",
        "VALIDACIONES",
    ]
    lines.extend(f"{'PASS' if passed else 'FAIL'}: {name}" for name, passed in checks.items())
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Analisis hadronico escrito en {args.summary}")
    print(f"Figuras: {args.figures_dir}")
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
