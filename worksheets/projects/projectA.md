# Hoja del Proyecto A — Dispersión múltiple

Guía asociada: [Proyecto A — Dispersión múltiple de Coulomb](../../docs/projects/projectA_mcs.md).

Esta hoja no contiene resultados de referencia. Complétala durante la clase con tu propia corrida.

Nombre: ________________________________________

Fecha: _________________________________________

Commit: ________________________________________

Seed: __________________________________________

Modo: `FAST=1` / `FULL=1` / otro: ______________

## Parte A — Predicción física

Material: __________________________ Partícula: _____________________________

Lista o constructor físico: __________________________________________________

¿Cómo esperas que cambie la anchura angular al aumentar el espesor?

____________________________________________________________________________

¿Cómo esperas que cambie al aumentar el momento?

____________________________________________________________________________

¿Esperas una distribución exactamente gaussiana? Justifica.

____________________________________________________________________________

¿Cuál será más sensible a eventos de cola: RMS o $(q_{84}-q_{16})/2$?

____________________________________________________________________________

## Parte B — Observación del WRL

Archivo: `generated/visualization/ex2/muon_mcs_10events.wrl`

- [ ] Identifiqué el volumen de hierro.
- [ ] Identifiqué la dirección inicial de los muones.
- [ ] Encontré una trayectoria con desviación visible.
- [ ] Encontré al menos un secundario o un evento de cola.

Configuración visual observada:

Energía: __________________ GeV  Espesor: __________________ cm

Describe una observación que el WRL permite hacer y una que requiere estadística:

____________________________________________________________________________

____________________________________________________________________________

Ruta de la captura conservada: ______________________________________________

## Parte C — Auditoría de los datos

Comando usado: ______________________________________________________________

| Archivo | Filas o configuraciones | Qué representa una fila | ¿Unidades verificadas? |
|---|---:|---|---|
| `thickness_scan.csv` | ______ | __________________________ | ______ |
| `energy_scan.csv` | ______ | __________________________ | ______ |
| `angular_events.csv` | ______ | __________________________ | ______ |

Eventos por configuración: __________________

Densidad del hierro: __________________ g/cm³

Longitud de radiación registrada: __________________ cm

¿Se cumple $N_{\mathrm{transmitted}}\leq N_{\mathrm{generated}}$ en todo el barrido? ______

Media de `theta_x_rad` en la muestra representativa: __________________ rad

Media de `theta_y_rad` en la muestra representativa: __________________ rad

¿Las proyecciones están aproximadamente centradas? ___________________________

## Parte D — Análisis

Define el observable robusto usado como anchura del núcleo:

$$
\sigma_{\mathrm{core}}=\underline{\hspace{7cm}}
$$

### Dependencia con el espesor

Modelo ajustado: _____________________________________________________________

$\alpha=$ __________________ $\pm$ __________________

¿Los residuos o puntos muestran una tendencia no descrita por el modelo?

____________________________________________________________________________

### Dependencia con el momento

Modelo ajustado: _____________________________________________________________

$\beta=$ __________________ $\pm$ __________________

¿Los residuos o puntos muestran una tendencia no descrita por el modelo?

____________________________________________________________________________

### Núcleo y colas

RMS de una configuración elegida: __________________ rad

Anchura robusta de la misma configuración: __________________ rad

Explica la diferencia:

____________________________________________________________________________

## Parte E — Conclusión y reproducibilidad

Responde la pregunta central en tres o cuatro frases:

____________________________________________________________________________

____________________________________________________________________________

Limitación principal de tu muestra o modelo:

____________________________________________________________________________

- [ ] Conservé la seed y el commit.
- [ ] Conservé el WRL o su captura.
- [ ] Conservé CSV, resumen y figuras.
- [ ] Puse unidades en todos los resultados.
- [ ] Consulté la referencia solamente después de concluir.
