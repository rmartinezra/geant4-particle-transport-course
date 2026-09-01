# Proyecto A — Dispersión múltiple de Coulomb

**Pregunta central:** ¿cómo cambian la anchura angular y las colas cuando varían el espesor del hierro y el momento del muón?

Usa esta guía durante la clase y registra predicciones, observaciones y resultados en la [hoja del Proyecto A](../../worksheets/projects/projectA.md). No consultes los [resultados FULL de referencia](../expected_results.md) antes de terminar tu análisis.

## Qué vas a simular

| Elemento | Configuración de producción |
|---|---|
| Partícula primaria | Muón positivo, `mu+` |
| Material físico | Hierro, material NIST `G4_Fe` |
| Lista electromagnética | `emstandard_opt0` del ejemplo Geant4 TestEm5 |
| Barrido de espesor | 5, 10, 20, 40, 60, 80 y 100 cm a 100 GeV |
| Barrido de energía | 5, 10, 20, 50, 100, 200 y 500 GeV a 50 cm |
| Muestra representativa | 100 GeV y 50 cm |

La simulación sigue el muón a través de un bloque finito de hierro. En la producción estadística, los secundarios se registran al crearse y después se eliminan para concentrar la medida en la desviación del primario. El transporte electromagnético y la pérdida de energía del muón siguen activos.

Para cada muón se comparan la dirección inicial y final. Se guardan las proyecciones angulares `theta_x_rad`, `theta_y_rad`, el ángulo polar total, la transmisión y la energía final.

## Antes de ejecutar

Anota en la hoja:

1. si esperas que la distribución angular sea exactamente gaussiana;
2. cómo debería cambiar su anchura al aumentar el espesor;
3. cómo debería cambiar al aumentar el momento;
4. qué medida será más resistente a las colas: RMS o intervalo central de cuantiles.

## 1. Generar y observar la simulación

Desde la raíz del repositorio:

```bash
docker compose run --rm geant4-course make visualize-ex2
./scripts/open_wrl_castle.sh \
  generated/visualization/ex2/muon_mcs_10events.wrl
```

El primer comando crea el archivo; el segundo se ejecuta **fuera del contenedor** y lo abre en Castle Model Viewer. La escena visual usa 10 muones de 5 GeV y 100 cm de hierro para que las desviaciones sean visibles. En esta escena los secundarios no se eliminan.

![Ejemplo de dispersión múltiple de muones en hierro](../../examples/visualization/muon_mcs.png)

Busca en el WRL:

- el volumen de hierro y la dirección inicial del haz;
- el ensanchamiento de las trayectorias después del material;
- diferencias entre desviaciones pequeñas y eventos de cola;
- secundarios producidos por interacciones reales.

El WRL sirve para comprender la geometría y los eventos, no para medir la distribución con solo diez casos.

## 2. Correr los datos de clase

```bash
docker compose run --rm geant4-course \
  make run-ex2 FAST=1 VIS=0 SEED=20260901
```

`FAST=1` ejecuta 300 eventos por cada configuración y otros 300 en la muestra representativa. `VIS=0` evita regenerar el WRL que ya observaste. El target reemplaza los CSV anteriores de `generated/data/ex2/`; por eso debes registrar la seed antes de repetirlo.

Para una producción posterior con mayor precisión cambia `FAST=1` por `FULL=1`; son 100 000 eventos por configuración y puede tardar considerablemente más.

## 3. Auditar los datos

```bash
head generated/data/ex2/thickness_scan.csv
head generated/data/ex2/energy_scan.csv
head generated/data/ex2/angular_events.csv
```

| Archivo | Qué representa una fila |
|---|---|
| `thickness_scan.csv` | Resumen de todos los eventos para un espesor a 100 GeV |
| `energy_scan.csv` | Resumen de todos los eventos para una energía a 50 cm |
| `angular_events.csv` | Un muón de la configuración representativa |
| `run_metadata.json` | Seed, versión, física y registro de cada corrida |

Comprueba `N_generated`, `N_transmitted`, unidades, material, densidad y longitud de radiación. En los eventos, verifica que `theta_total_rad` sea no negativo y que las proyecciones estén centradas aproximadamente alrededor de cero.

## 4. Analizar y ver las figuras

```bash
docker compose run --rm geant4-course make analyze-ex2
```

Abre con el visor de imágenes del sistema:

```text
generated/figures/ex2/angular_distribution.png
generated/figures/ex2/width_vs_thickness.png
generated/figures/ex2/width_vs_momentum.png
```

El resumen numérico queda en:

```text
generated/fits/ex2/summary_mcs.txt
```

El análisis define una anchura robusta del núcleo:

$$
\sigma_{\mathrm{core}}=\frac{q_{84}-q_{16}}{2}
$$

y ajusta, sin fijar los exponentes:

$$
\sigma_{\mathrm{core}}=A x^\alpha,
\qquad
\sigma_{\mathrm{core}}=B p^{-\beta}.
$$

Solo después del fit compara la tendencia medida con la dependencia aproximada en $\sqrt{x}$, $1/p$ y la fórmula de Highland. Examina también las colas: el RMS global puede responder de manera distinta a la anchura central.

## Evidencia para entregar

- captura del WRL con una trayectoria desviada identificada;
- seed, modo y commit usados;
- auditoría breve de los tres CSV;
- exponentes $\alpha$ y $\beta$ con sus incertidumbres;
- comparación razonada entre RMS y anchura robusta;
- una conclusión que responda la pregunta central sin atribuir a la estadística efectos que pertenecen a la física o a la selección del observable.

El [README técnico del ejercicio](../../exercises/02_multiple_scattering/README.md) resume la implementación.
