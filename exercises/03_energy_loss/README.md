# Proyecto B del curso — Pérdida de energía

**Pregunta del proyecto:** ¿cómo se reparten la pérdida del primario, el depósito local y la energía de los secundarios?

Material para la sesión: [guía del Proyecto B](../../docs/projects/projectB_energy_loss.md) y [hoja de trabajo](../../worksheets/projects/projectB.md).

```bash
docker compose run --rm geant4-course make visualize-ex3
docker compose run --rm geant4-course make run-ex3 FAST=1 VIS=0 SEED=20260901
docker compose run --rm geant4-course make analyze-ex3
```

Datos, figuras, resumen y WRL quedan respectivamente en `generated/data/ex3/`, `generated/figures/ex3/`, `generated/fits/ex3/` y `generated/visualization/ex3/`.

## OBJETIVO

Medir $dE/dx$ de muones en agua y separar balances energéticos.

## QUÉ SIMULAR

Muones positivos en agua para varios espesores y energías.

## QUÉ MEDIR

Pérdida del primario, depósito local, energía transferida a secundarios, $N$, media, desviación, SEM, mediana y $q_{16}/q_{84}$.

## QUÉ AJUSTAR

La pérdida media frente al espesor delgado. `dedx_vs_energy.png` muestra barras SEM.

## QUÉ OBTENER

El poder de frenado inferido a partir de los eventos. `G4EmCalculator` es solo una comparación posterior.

## VISUALIZACIÓN

El WRL muestra agua, muones atravesando el volumen y secundarios/deposición asociados a interacciones reales.

## RESULTADOS ESPERADOS

Las distribuciones tienen colas radiativas; aun con muchos eventos pueden converger lentamente. Esa gran varianza es física y no se oculta.

Los valores FULL se reservan en [resultados de referencia — contiene spoilers](../../docs/expected_results.md).

## PREGUNTAS

¿Por qué pérdida del primario y depósito local difieren? ¿Qué efecto tienen las colas sobre media, mediana y SEM?
