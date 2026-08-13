# Resultados esperados

Los valores siguientes corresponden a Geant4 11.2.2. Deben reproducirse dentro de las tolerancias, no bit a bit: las seeds, el paralelismo y el tamaño de muestra producen variaciones estadísticas.

| Módulo | Magnitud FULL | Resultado Monte Carlo |
|---|---|---:|
| Compton A | `mu` | 0.274090 ± 0.000611 cm⁻¹ |
| Compton A | `lambda` | 3.64843 ± 0.00813 cm |
| Compton A | `sigma` | 4.54995 ± 0.01014 barn/átomo |
| Compton B | `m_e c²`, fit lineal | 511.302 ± 0.068 keV |
| MCS | `alpha_thickness` | 0.51350 ± 0.00110 |
| MCS | `alpha_momentum` | 1.03593 ± 0.00482 |
| Pérdida de energía | `dE/dx`, mu+ de 3 GeV en agua | 2.29342 ± 0.0058 MeV/cm |
| Fisión U-235 | `lambda`, neutrón de 1 eV | 0.294824 ± 0.001032 cm |
| Fisión U-235 | `sigma_fission` | 69.493 ± 0.243 barn/átomo |

Tolerancias FAST automáticas: masa Compton 480–540 keV, exponentes MCS 0.3–0.7 y 0.7–1.3, `dE/dx` 1–5 MeV/cm y magnitudes hadrónicas positivas. FULL debe dar incertidumbres menores y acuerdo más estrecho con las referencias posteriores.

Las corridas FULL usaron 100 000 eventos por punto para Compton A, MCS, pérdida de energía y fisión, y 200 000 eventos para Compton B. Las referencias internas se consultaron después de medir: 4.55532 barn/átomo en Compton A, 510.99895 keV para la energía de reposo del electrón, 2.30 MeV/cm con `G4EmCalculator` y 69.64 barn/átomo para `nFission`. No se usan como restricciones de los ajustes.

Las gráficas publicadas en `examples/expected_results/` proceden de esas corridas FULL; no se incluyen sus CSV fuente. En pérdida de energía, las barras de `dedx_vs_energy.png` son SEM y las distribuciones conservan las colas radiativas.
