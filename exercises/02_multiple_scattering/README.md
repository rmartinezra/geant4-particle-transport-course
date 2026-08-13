# Experimento 2 — Multiple Coulomb Scattering

## OBJETIVO

Obtener la anchura angular y sus leyes de escala únicamente de trayectorias Geant4.

## QUÉ SIMULAR

Muones positivos atravesando hierro para varios espesores y momentos.

## QUÉ MEDIR

`theta_x`, `theta_y`, `theta_total`, media, desviación estándar, RMS y q16/q50/q84.

## QUÉ AJUSTAR

`sigma_core=A*x^alpha` y `sigma_core=B*p^-beta`, con `alpha` y `beta` libres. `sigma_core=(q84-q16)/2`.

## QUÉ OBTENER

`alpha≈0.5` y `beta≈1`. El C++ no calcula Highland; la fórmula aparece solo después en el análisis como comparación sin ajustar.

## VISUALIZACIÓN

El WRL muestra el bloque de Fe, muones incidentes, desviaciones de trayectorias y secundarios.

## RESULTADOS ESPERADOS

FULL: `alpha≈0.51`, `beta≈1.04`; las colas no gaussianas permanecen visibles.

## PREGUNTAS

¿Por qué el RMS global es más sensible a colas? ¿Qué mide una proyección frente al ángulo polar total?
