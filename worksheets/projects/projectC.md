# Hoja del Proyecto C — Fisión en U-235

Guía asociada: [Proyecto C — Fisión y sección eficaz en U-235](../../docs/projects/projectC_fission.md).

Esta hoja guía la actividad de clase sin revelar el valor de referencia.

Nombre: ________________________________________

Fecha: _________________________________________

Commit: ________________________________________

Seed: __________________________________________

Modo: `FAST=1` / `FULL=1` / otro: ______________

## Parte A — Predicción física

Partícula: __________________________ Energía: __________________ eV

Material: ___________________________ Espesor de producción: _____________ cm

Lista hadrónica: ____________________________________________________________

Modelo de baja energía: _____________________________________________________

Proceso activo que se medirá: _______________________________________________

¿Qué forma esperas para la distribución de distancias de primera fisión?

____________________________________________________________________________

¿Qué información aporta un neutrón que sale sin fisionar?

____________________________________________________________________________

¿En qué dirección se sesgaría $\lambda$ si eliminaras todos los escapes?

____________________________________________________________________________

## Parte B — Observación del WRL

Archivo: `generated/visualization/ex4/neutron_fission_10events.wrl`

- [ ] Identifiqué el volumen de U-235.
- [ ] Identifiqué la dirección de los neutrones.
- [ ] Busqué escapes; si no apareció ninguno en diez eventos, lo registré.
- [ ] Identifiqué un vértice y productos de fisión.

Espesor de la geometría visual: __________________ cm

¿Por qué es diferente del espesor de producción y qué propiedad física no cambia?

____________________________________________________________________________

____________________________________________________________________________

Ruta de la captura conservada: ______________________________________________

## Parte C — Auditoría de eventos

Comando usado: ______________________________________________________________

Eventos generados: __________________

Fisiones: __________________

Escapes censurados: __________________

Verifica el balance de conteos:

$$
\underline{\hspace{3cm}}=\underline{\hspace{3cm}}+\underline{\hspace{3cm}}
$$

Densidad del U-235: __________________ g/cm³

Densidad numérica: __________________ átomos/cm³

Procesos presentes en eventos interactuantes: _______________________________

¿Todos los escapes conservan una distancia positiva dentro del material? ______

Explica qué representa `distance_inside_material_cm` para:

- una fisión: ______________________________________________________________
- un escape: _______________________________________________________________

## Parte D — Likelihood censurada

Número de fisiones $d=$ __________________

Exposición total $T=\sum_i t_i=$ __________________ cm

Completa los estimadores:

$$
\widehat\lambda=\underline{\hspace{5cm}}
$$

$$
\widehat\Sigma=\underline{\hspace{5cm}}
$$

$$
\widehat\sigma_f=\underline{\hspace{5cm}}
$$

Resultados:

$\widehat\lambda=$ __________________ $\pm$ __________________ cm

$\widehat\Sigma=$ __________________ $\pm$ __________________ cm⁻¹

$\widehat\sigma_f=$ __________________ $\pm$ __________________ barn/átomo

Describe `survival_probability.png`:

- comportamiento aproximadamente exponencial: _____________________________
- posibles desviaciones sistemáticas: _____________________________________
- efecto visible del límite geométrico: ___________________________________

¿Cómo cambiaría el cálculo si se usara solo la media de las distancias que sí fisionan?

____________________________________________________________________________

## Parte E — Comparación y conclusión

Solo después de completar lo anterior:

Referencia posterior de Geant4: __________________ barn/átomo

Diferencia relativa: __________________ %

¿Es compatible con la incertidumbre estadística estimada? ___________________

Conclusión que responde la pregunta central:

____________________________________________________________________________

____________________________________________________________________________

Limitación principal del modelo o de la muestra:

____________________________________________________________________________

- [ ] Conservé seed, commit, energía y espesores.
- [ ] Conservé el WRL o su captura.
- [ ] Conservé CSV, resumen y figuras.
- [ ] Incluí los escapes en la exposición.
- [ ] Reporté unidades e incertidumbre.
- [ ] Consulté la referencia solo al final.
