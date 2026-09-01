# Hoja del Proyecto B — Pérdida de energía

Guía asociada: [Proyecto B — Pérdida de energía de muones en agua](../../docs/projects/projectB_energy_loss.md).

Completa la hoja con la simulación realizada en clase; no uses valores de referencia antes de concluir.

Nombre: ________________________________________

Fecha: _________________________________________

Commit: ________________________________________

Seed: __________________________________________

Modo: `FAST=1` / `FULL=1` / otro: ______________

## Parte A — Predicción física

Material: __________________________ Partícula: _____________________________

Configuración electromagnética: _____________________________________________

¿Qué simplificación física deliberada tiene este proyecto?

____________________________________________________________________________

Predice la relación entre pérdida media y espesor en la región delgada:

____________________________________________________________________________

¿Esperas que media y mediana sean iguales? Justifica.

____________________________________________________________________________

¿En qué situación la energía perdida por el primario no se deposita toda dentro del agua?

____________________________________________________________________________

## Parte B — Observación del WRL

Archivo: `generated/visualization/ex3/muon_energy_loss_10events.wrl`

- [ ] Identifiqué el volumen de agua.
- [ ] Identifiqué los muones primarios.
- [ ] Identifiqué al menos un punto de producción de secundarios.
- [ ] Distinguí una trayectoria que sale del volumen.

Configuración visual:

Energía: __________________ GeV  Longitud de agua: __________________ cm

¿Por qué la geometría visual puede ser más larga que algunas geometrías del barrido?

____________________________________________________________________________

Ruta de la captura conservada: ______________________________________________

## Parte C — Auditoría de datos

Comando usado: ______________________________________________________________

| Archivo | Filas o configuraciones | Qué representa una fila | ¿Unidades verificadas? |
|---|---:|---|---|
| `thickness_scan.csv` | ______ | __________________________ | ______ |
| `dedx_energy_scan.csv` | ______ | __________________________ | ______ |
| `energy_loss_events.csv` | ______ | __________________________ | ______ |
| `process_contributions.csv` | ______ | __________________________ | ______ |

Eventos por configuración: __________________

Densidad del agua: __________________ g/cm³

Para un evento representativo:

$E_{\mathrm{inicial}}=$ __________________ MeV

$E_{\mathrm{final}}=$ __________________ MeV

$\Delta E_{\mathrm{primario}}=$ __________________ MeV

$E_{\mathrm{depositada}}=$ __________________ MeV

$E_{\mathrm{transferida\ a\ secundarios}}=$ __________________ MeV

Verifica $\Delta E_{\mathrm{primario}}=E_{\mathrm{inicial}}-E_{\mathrm{final}}$:

____________________________________________________________________________

## Parte D — Distribución y ajuste

En la configuración representativa:

Media: __________________ MeV

Mediana: __________________ MeV

Desviación estándar: __________________ MeV

SEM: __________________ MeV

$q_{16}$: __________________ MeV  $q_{84}$: __________________ MeV

Describe centro, anchura y cola de `energy_loss_distribution.png`:

____________________________________________________________________________

____________________________________________________________________________

Región de espesores usada para estimar la pendiente: _________________________

$dE/dx=$ __________________ $\pm$ __________________ MeV/cm

¿La gráfica de pérdida media frente al espesor parece lineal en esa región?

____________________________________________________________________________

Describe la tendencia de `dedx_vs_energy.png` sin consultar aún la referencia:

____________________________________________________________________________

¿Qué procesos aportan a las colas o dominan a energías diferentes?

____________________________________________________________________________

## Parte E — Interpretación y reproducibilidad

Explica con tus datos la diferencia entre:

- pérdida del primario: ____________________________________________________
- energía transferida a secundarios: ______________________________________
- depósito local: __________________________________________________________

Conclusión que responde la pregunta central:

____________________________________________________________________________

____________________________________________________________________________

Limitación principal:

____________________________________________________________________________

- [ ] Conservé seed, commit y configuración física.
- [ ] Conservé el WRL o su captura.
- [ ] Conservé CSV, resumen y figuras.
- [ ] Reporté incertidumbre y unidades.
- [ ] Consulté `G4EmCalculator` solo como comparación posterior.
