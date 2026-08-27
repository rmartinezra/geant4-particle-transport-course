# Experimento 1A — Sección eficaz Compton

## OBJETIVO

Obtener $\mu$, $\lambda$ y la sección eficaz microscópica a partir de transmisión Monte Carlo.

## QUÉ SIMULAR

Fotones de $300\ \mathrm{keV}$ sobre espesores de aluminio con fotoeléctrico, conversión y producción de pares desactivados.

## QUÉ MEDIR

$T(x)=N_{\mathrm{trans}}/N_0$, con incertidumbre binomial.

## QUÉ AJUSTAR

$T(x)=\exp(-\mu x)$ mediante likelihood binomial. La densidad atómica y todas las unidades se conservan explícitas.

## QUÉ OBTENER

$\lambda=1/\mu$ y $\sigma=\mu/n$, exclusivamente de los eventos. `G4EmCalculator` se consulta después como referencia independiente.

## VISUALIZACIÓN

El WRL muestra el bloque de Al y el estado final de cada primera interacción: verde para el gamma incidente o transmitido, amarillo para la dirección del fotón dispersado y rojo para la del electrón de retroceso. Los vectores amarillo y rojo conservan las direcciones de Geant4, pero se escalan para ser visibles; su longitud no representa el alcance físico.

## RESULTADOS ESPERADOS

$\mu\approx 0.274\ \mathrm{cm}^{-1}$, $\lambda\approx 3.65\ \mathrm{cm}$, $\sigma\approx 4.55\ \text{barn/átomo}$.

## PREGUNTAS

¿Por qué la likelihood binomial es preferible para transmisión? ¿Cómo escala la incertidumbre con $N_0$?
