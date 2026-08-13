# Experimento 3 — Pérdida de energía

## OBJETIVO

Medir `dE/dx` de muones en agua y separar balances energéticos.

## QUÉ SIMULAR

Muones positivos en agua para varios espesores y energías.

## QUÉ MEDIR

Pérdida del primario, depósito local, energía transferida a secundarios, `N`, media, desviación, SEM, mediana y q16/q84.

## QUÉ AJUSTAR

La pérdida media frente al espesor delgado. `dedx_vs_energy.png` muestra barras SEM.

## QUÉ OBTENER

Para 3 GeV, aproximadamente `2.3 MeV/cm`. `G4EmCalculator` es solo una comparación posterior.

## VISUALIZACIÓN

El WRL muestra agua, muones atravesando el volumen y secundarios/deposición asociados a interacciones reales.

## RESULTADOS ESPERADOS

Las distribuciones tienen colas radiativas; aun con muchos eventos pueden converger lentamente. Esa gran varianza es física y no se oculta.

## PREGUNTAS

¿Por qué pérdida del primario y depósito local difieren? ¿Qué efecto tienen las colas sobre media, mediana y SEM?
