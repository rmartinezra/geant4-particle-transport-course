# Experimento 1B — Cinemática Compton

## OBJETIVO

Reconstruir la energía del fotón dispersado frente al ángulo y ajustar $m_e c^2$.

## QUÉ SIMULAR

Primeras interacciones Compton de fotones de $300\ \mathrm{keV}$ en aluminio.

## QUÉ MEDIR

$E_\gamma(\theta)$ evento a evento y el balance de energía completo.

## QUÉ AJUSTAR

La curva no lineal y

$$
\frac{1}{E'}-\frac{1}{E_0}=\frac{1-\cos\theta}{m_e c^2}
$$

dejando $m_e c^2$ libre.

## QUÉ OBTENER

Un valor cercano a $511\ \mathrm{keV}$. Geant4 puede incorporar electrones ligados y Doppler broadening; la incertidumbre del fit describe la dispersión Monte Carlo del modelo y no una incertidumbre experimental real de la masa. La referencia física, los efectos del modelo y cualquier smearing instrumental futuro deben mantenerse separados.

## VISUALIZACIÓN

El WRL muestra el estado final de cada primera interacción: verde para el gamma incidente, amarillo para la dirección del fotón dispersado y rojo para la del electrón de retroceso. Los vectores amarillo y rojo conservan las direcciones de Geant4, pero se escalan para ser visibles; su longitud no representa el alcance físico.

## RESULTADOS ESPERADOS

$m_e c^2\approx 511\ \mathrm{keV}$, con residuos no nulos respecto al electrón libre.

## PREGUNTAS

¿Qué cambia al introducir resolución angular o energética artificial? ¿Por qué no debe confundirse con Doppler broadening?
