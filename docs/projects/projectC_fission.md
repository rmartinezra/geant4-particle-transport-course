# Proyecto C — Fisión y sección eficaz en U-235

**Pregunta central:** ¿cómo se estima una longitud de interacción cuando parte de los neutrones escapa sin fisionar?

Trabaja con esta guía y registra el razonamiento en la [hoja del Proyecto C](../../worksheets/projects/projectC.md). La sección de [resultados FULL de referencia](../expected_results.md) se abre solamente después de obtener una estimación propia.

## Qué vas a simular

| Elemento | Configuración de producción |
|---|---|
| Partícula primaria | Neutrón |
| Energía | 1 eV |
| Material físico | U-235 isotópico puro, `U235` |
| Geometría de producción | 0.5 cm de material |
| Lista hadrónica | Hadr03 con `G4HadronPhysicsQGSP_BIC_HP` |
| Modelo y dataset | `NeutronHPFission` entre 0 y 20 MeV; `NeutronHPFissionXS` |
| Canal activo | Solo `nFission` |

Para convertir la longitud de interacción en sección eficaz microscópica, la simulación registra la densidad y la densidad numérica del U-235. Los procesos elástico, inelástico y captura se desactivan de forma explícita: este proyecto mide el canal de fisión, no la sección eficaz total del neutrón.

La geometría finita hace que algunos neutrones atraviesen los 0.5 cm sin fisionar. Esos eventos no son fallos ni deben borrarse: aportan una exposición conocida y son observaciones censuradas por la derecha.

## Antes de ejecutar

Registra una predicción para:

1. la forma de la distribución de distancias de primera fisión;
2. qué información aporta un neutrón que escapa;
3. el sesgo esperado si se analizan únicamente las fisiones;
4. la relación dimensional entre camino libre medio, sección eficaz macroscópica y microscópica.

## 1. Generar y observar la simulación

```bash
docker compose run --rm geant4-course make visualize-ex4
./scripts/open_wrl_castle.sh \
  generated/visualization/ex4/neutron_fission_10events.wrl
```

La escena usa 2 cm de U-235, en vez de 0.5 cm, para que diez eventos permitan observar productos de fisión con mayor facilidad. Conserva la misma energía, material y modelos físicos, y no aplica biasing.

![Ejemplo de neutrones y productos de fisión en U-235](../../examples/visualization/neutron_fission.png)

Identifica el haz de neutrones, el volumen de U-235 y vértices con múltiples productos secundarios. Si aparece un neutrón que cruza sin fisionar, regístralo; con solo diez eventos puede no aparecer ninguno. La mayor longitud del volumen visual no debe confundirse con la geometría de producción.

## 2. Correr los datos de clase

```bash
docker compose run --rm geant4-course \
  make run-ex4 FAST=1 VIS=0 SEED=20260901
```

El modo FAST genera 3000 neutrones. La ejecución sobrescribe los datos anteriores de `generated/data/ex4/`. El modo normal usa 10 000 y `FULL=1` usa 100 000 cuando se necesita reducir la incertidumbre estadística.

## 3. Auditar los datos

```bash
head generated/data/ex4/interaction_lengths.csv
head generated/data/ex4/hadronic_events.csv
```

| Archivo | Qué representa una fila |
|---|---|
| `interaction_lengths.csv` | Un neutrón, su distancia dentro del material y su estado de interacción/escape |
| `hadronic_events.csv` | Registro enriquecido con densidad, densidad numérica y proceso |
| `run_metadata.json` | Geometría, seeds, física, conteos y referencia consultada al final |

Comprueba que cada evento sea una fisión `nFission` o un escape censurado, y que ningún escape tenga exposición cero. Debe cumplirse:

$$
N_{\mathrm{generados}}=N_{\mathrm{fisiones}}+N_{\mathrm{escapes}}.
$$

## 4. Analizar y ver las figuras

```bash
docker compose run --rm geant4-course make analyze-ex4
```

El análisis añade y produce:

```text
generated/data/ex4/cross_section_result.csv
generated/figures/ex4/interaction_length_distribution.png
generated/figures/ex4/survival_probability.png
generated/fits/ex4/summary_hadronic.txt
```

Si $d$ es el número de fisiones y $T=\sum_i t_i$ es la exposición total de todos los neutrones, incluidos los que escapan, la máxima verosimilitud censurada da:

$$
\widehat\lambda=\frac{T}{d},
\qquad
\widehat\Sigma=\frac{1}{\widehat\lambda}=\frac{d}{T},
\qquad
\widehat\sigma_f=\frac{\widehat\Sigma}{n}.
$$

La referencia de `G4HadronicProcessStore` se consulta después de los eventos. Úsala para comparar, nunca para reemplazar la estimación de los datos.

Al mirar `survival_probability.png`, decide si la forma exponencial describe razonablemente la supervivencia y si aparecen desviaciones sistemáticas.

## Evidencia para entregar

- captura del WRL distinguiendo volumen, neutrón y productos de fisión;
- seed, modo, commit y espesor de producción;
- conteos de fisiones y escapes;
- exposición total y estimaciones de $\lambda$, $\Sigma$ y $\sigma_f$ con unidades;
- explicación de cómo entran los escapes en la likelihood;
- comparación posterior con la referencia y una conclusión sobre posibles limitaciones.

El [README técnico del ejercicio](../../exercises/04_nuclear_cross_section/README.md) describe la implementación.
