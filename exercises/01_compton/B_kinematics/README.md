# Experimento 1B — Cinemática Compton

## OBJETIVO

Reconstruir la energía del fotón dispersado frente al ángulo y ajustar `m_e c²`.

## QUÉ SIMULAR

Primeras interacciones Compton de fotones de 300 keV en aluminio.

## QUÉ MEDIR

`E_gamma(theta)` evento a evento y el balance de energía completo.

## QUÉ AJUSTAR

La curva no lineal y `1/E' - 1/E0 = (1-cos(theta))/(m_e c²)`, dejando `m_e c²` libre.

## QUÉ OBTENER

Un valor cercano a 511 keV. Geant4 puede incorporar electrones ligados y Doppler broadening; la incertidumbre del fit describe la dispersión Monte Carlo del modelo y no una incertidumbre experimental real de la masa. La referencia física, los efectos del modelo y cualquier smearing instrumental futuro deben mantenerse separados.

## VISUALIZACIÓN

El WRL muestra fotones incidentes, cambios de dirección Compton y electrones secundarios cuando corresponda.

## RESULTADOS ESPERADOS

`m_e c²≈511 keV`, con residuos no nulos respecto al electrón libre.

## PREGUNTAS

¿Qué cambia al introducir resolución angular o energética artificial? ¿Por qué no debe confundirse con Doppler broadening?
