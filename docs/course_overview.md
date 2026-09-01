# Visión general del curso

Este curso introduce el transporte de partículas con Geant4 mediante una ruta corta y verificable: **dos clases**, **dos prácticas guiadas** y **tres proyectos de aplicación**.

La idea científica común es construir una magnitud a partir de los eventos simulados y compararla con una referencia solamente al final:

```text
pregunta física → predicción → eventos Geant4 → observable → inferencia
                                                           ↓
                                             comparación posterior
```

## Estructura

| Etapa | Material | Estado |
|---|---|---|
| Clase 1 | [Transporte, interacción y efecto Compton](classes/class01_transport.md) | Lección completa |
| Práctica guiada 1A | Transmisión gamma en aluminio | Incluida en la Clase 1 |
| Práctica guiada 1B | Cinemática Compton | Incluida en la Clase 1 |
| Clase 2 | [Del evento al resultado físico](classes/class02_analysis.md) | Lección completa |
| Proyecto A | [Dispersión múltiple de Coulomb](projects/projectA_mcs.md) | Aplicación |
| Proyecto B | [Pérdida de energía](projects/projectB_energy_loss.md) | Aplicación |
| Proyecto C | [Fisión y sección eficaz](projects/projectC_fission.md) | Aplicación |

Las Clases 1 y 2 constituyen el recorrido guiado completo. Las fichas de los proyectos sirven como navegación y delimitación de las aplicaciones posteriores.

## Ruta conceptual

```text
física microscópica → sección eficaz → camino libre medio
       → transporte Monte Carlo → eventos → observables
       → ajuste → magnitud física
```

1. En la Clase 1, el estudiante interpreta una interacción microscópica como una probabilidad macroscópica de supervivencia. Primero predice y visualiza; después calcula a mano a partir de CSV.
2. En la Clase 2 se genera una producción FULL propia —100 000 eventos por espesor en 1A y 200 000 eventos en 1B— y se organiza el paso desde esos datos hasta estimadores, incertidumbres, residuos y ajustes reproducibles.
3. En los proyectos A, B y C se aplicará la misma cadena a dispersión angular, pérdida de energía y fisión, respectivamente.

No se espera que el estudiante ejecute todos los módulos al comenzar. Antes de la Clase 1 basta con descargar la imagen y usar `make env-check`; las corridas `FULL=1` y los [resultados de referencia](expected_results.md) se reservan para el momento indicado por el docente.

## Entregables de la Clase 1

- [Hoja de trabajo de la Clase 1](../worksheets/class01.md), completada sin consultar los resultados de referencia.
- Archivos WRL de las prácticas 1A y 1B observados con [Castle Model Viewer](visualization.md) antes del análisis numérico.
- Cálculos propios de transmisión, coeficiente de atenuación, longitud libre media y relación de Compton.

La [página principal](../README.md) contiene el inicio rápido y el mapa completo del repositorio.

## Entregables de la Clase 2

- [Hoja de trabajo de la Clase 2](../worksheets/class02.md).
- CSV FULL de 1A y 1B producidos con `make prepare-class02` y una seed registrada.
- Resultados de los ajustes de 1A y 1B con unidades e incertidumbres.
- Figuras principales y de residuos de ambas prácticas.
- Registro de configuración, seeds, commit y limitaciones.
- Comparación con las referencias realizada únicamente después de cerrar el análisis.
