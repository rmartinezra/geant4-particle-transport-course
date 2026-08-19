# Clase 1 — Hoja de trabajo

Nombre: ________________________________________

Fecha: _________________________________________

Trabaja primero con tus predicciones y después contrástalas con la simulación. No consultes los resultados FULL de referencia.

## Parte A — Antes de simular

1. Si aumenta el espesor $x$, ¿qué esperas que ocurra con la transmisión $T$?

   ____________________________________________________________________________

   ____________________________________________________________________________

2. ¿Qué significa físicamente el camino libre medio $\lambda$?

   ____________________________________________________________________________

3. Si aumenta la sección eficaz microscópica $\sigma$ y el material no cambia, ¿$\lambda$ aumenta o disminuye? Explica.

   ____________________________________________________________________________

4. ¿Por qué dos partículas idénticas no tienen que interactuar a la misma distancia?

   ____________________________________________________________________________

5. Distingue con una frase sección eficaz total y sección eficaz diferencial.

   ____________________________________________________________________________

## Parte B — Compton 1A

### Predicción

Dibuja o describe la forma que esperas para $T$ frente a $x$ antes de ejecutar la simulación.

____________________________________________________________________________

____________________________________________________________________________

### Observación del WRL

Nombre del archivo observado: _______________________________________________

Describe una trayectoria que alcanza el límite y otra que termina dentro del aluminio.

____________________________________________________________________________

____________________________________________________________________________

¿Todos los fotones interactúan? _____________________________________________

¿Qué evidencia visual usaste? ______________________________________________

### Una fila del CSV

$x=$ ____________________ cm

$N_0=$ ___________________

$N_{\mathrm{trans}}=$ ______________

$T=N_{\mathrm{trans}}/N_0=$ _______

### Estimación manual

$\mu_{\mathrm{est}}=-\ln(T)/x=$ ____________________ cm⁻¹

$\lambda_{\mathrm{est}}=1/\mu_{\mathrm{est}}=$ __________ cm

1. ¿Por qué un solo punto no es suficiente para una estimación precisa?

   ____________________________________________________________________________

2. ¿Qué esperas observar al representar $\ln(T)$ frente a $x$?

   ____________________________________________________________________________

3. En este ejercicio, ¿qué condición debe cumplir un fotón para contar en $N_{\mathrm{trans}}$?

   ____________________________________________________________________________

## Parte C — Compton 1B

### Predicción

Si el fotón se dispersa hacia atrás, ¿esperas una energía $E'$ mayor o menor que para una desviación pequeña? Justifica antes de mirar los eventos.

____________________________________________________________________________

____________________________________________________________________________

### Observación del WRL

Nombre del archivo observado: _______________________________________________

¿Qué trayectorias o vértices identificaste? __________________________________

____________________________________________________________________________

### Un evento del CSV

`event_id =` __________________

$E_0=$ ________________________ keV

$\theta=$ _____________________ grados

$E'_{\mathrm{MC}}=$ _____________________ keV

$E'_{\mathrm{ideal}}=$ __________________ keV

$\mathrm{diferencia}=E'_{\mathrm{MC}}-E'_{\mathrm{ideal}}=$ __________________ keV

`energía cinética del electrón =` _________________ keV

1. ¿Qué ocurre con $E'$ cuando aumenta $\theta$?

   ____________________________________________________________________________

2. ¿La diferencia entre $E'_{\mathrm{MC}}$ y $E'_{\mathrm{ideal}}$ demuestra por sí sola un error? ¿Qué información adicional necesitarías?

   ____________________________________________________________________________

3. ¿Qué diferencia conceptual hay entre las preguntas físicas de 1A y 1B?

   ____________________________________________________________________________

## Parte D — Síntesis

Completa la cadena:

$\sigma$ → __________________ → distancia → __________________ → estado final

Añade donde corresponda el número aleatorio utilizado por el Monte Carlo:

```text
____________________________________________________________________________
```

### Pregunta final

> Explica en un máximo de tres frases qué hace un Monte Carlo de transporte.

1. __________________________________________________________________________

2. __________________________________________________________________________

3. __________________________________________________________________________

## Entrega mínima

- [ ] Hoja de trabajo completa.
- [ ] Una captura de un WRL de 1A o 1B.
- [ ] Cálculo manual de $T$, $\mu$ y $\lambda$ para un punto.
- [ ] Comparación de un evento Compton con la cinemática ideal.
- [ ] Respuesta corta sobre la diferencia física entre 1A y 1B.
