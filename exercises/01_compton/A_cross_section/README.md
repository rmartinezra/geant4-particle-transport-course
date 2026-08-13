# Experimento 1A — Sección eficaz Compton

## OBJETIVO

Obtener `mu`, `lambda` y la sección eficaz microscópica a partir de transmisión Monte Carlo.

## QUÉ SIMULAR

Fotones de 300 keV sobre espesores de aluminio con fotoeléctrico, conversión y producción de pares desactivados.

## QUÉ MEDIR

`T(x)=N_trans/N0`, con incertidumbre binomial.

## QUÉ AJUSTAR

`T(x)=exp(-mu*x)` mediante likelihood binomial. La densidad atómica y todas las unidades se conservan explícitas.

## QUÉ OBTENER

`lambda=1/mu` y `sigma=mu/n`, exclusivamente de los eventos. `G4EmCalculator` se consulta después como referencia independiente.

## VISUALIZACIÓN

El WRL muestra el bloque de Al, fotones transmitidos, fotones dispersados y secundarios cuando aparecen.

## RESULTADOS ESPERADOS

`mu≈0.274 cm⁻¹`, `lambda≈3.65 cm`, `sigma≈4.55 barn/átomo`.

## PREGUNTAS

¿Por qué la likelihood binomial es preferible para transmisión? ¿Cómo escala la incertidumbre con `N0`?
