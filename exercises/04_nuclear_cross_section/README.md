# Proyecto C del curso — Sección eficaz de fisión en U-235

**Pregunta del proyecto:** ¿cómo estimar una longitud de interacción sin eliminar los neutrones que escapan?

Material para la sesión: [guía del Proyecto C](../../docs/projects/projectC_fission.md) y [hoja de trabajo](../../worksheets/projects/projectC.md).

```bash
docker compose run --rm geant4-course make visualize-ex4
docker compose run --rm geant4-course make run-ex4 FAST=1 VIS=0 SEED=20260901
docker compose run --rm geant4-course make analyze-ex4
```

Datos, figuras, resumen y WRL quedan respectivamente en `generated/data/ex4/`, `generated/figures/ex4/`, `generated/fits/ex4/` y `generated/visualization/ex4/`.

## OBJETIVO

Reconstruir la sección eficaz `nFission` a partir de la primera distancia de fisión y censura derecha.

## QUÉ SIMULAR

Neutrones de $1\ \mathrm{eV}$ en U-235 isotópico puro con `G4HadronPhysicsQGSP_BIC_HP`, `NeutronHPFission` y `NeutronHPFissionXS`.

## QUÉ MEDIR

ID, energía, interacción, distancia, escape, exposición dentro del material y nombre de proceso. Ningún escape se elimina.

## QUÉ AJUSTAR

Likelihood exponencial censurada: $\widehat{\lambda}=\mathrm{exposición}_{\mathrm{total}}/N_{\mathrm{fisiones}}$.

## QUÉ OBTENER

$\Sigma=1/\lambda$ y $\sigma_f=\Sigma/n$. `G4HadronicProcessStore` se consulta solo después para exactamente `nFission`.

## VISUALIZACIÓN

La geometría visual usa $2\ \mathrm{cm}$ para observar fisiones y productos secundarios en 10 eventos; producción usa $0.5\ \mathrm{cm}$ para conservar una fracción útil de escapes censurados. No hay biasing.

## RESULTADOS ESPERADOS

La estimación debe ser positiva y conservar la contribución de los eventos censurados. Los valores FULL se reservan en [resultados de referencia — contiene spoilers](../../docs/expected_results.md).

## PREGUNTAS

¿Qué sesgo aparece si se eliminan escapes? ¿Por qué la configuración visual puede diferir en longitud sin cambiar la física?
