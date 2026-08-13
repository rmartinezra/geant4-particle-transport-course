# Curso reproducible de transporte de partículas con Geant4

Cinco módulos docentes basados en cuatro experimentos: sección eficaz Compton, cinemática Compton, dispersión múltiple de Coulomb, pérdida de energía y fisión de neutrones en U-235.

El entorno fija **Geant4 11.2.2**. No hace falta instalar Geant4 ni Python en el host: Docker compila, simula, analiza y escribe visualizaciones VRML2 sin X11, Qt u OpenGL.

## Inicio rápido

```bash
git clone https://github.com/rmartinezra/geant4-particle-transport-course.git
cd geant4-particle-transport-course
docker compose build
docker compose run --rm geant4-course make test
docker compose run --rm geant4-course make run-ex1a FAST=1
docker compose run --rm geant4-course make analyze-ex1a
```

`run-ex1a` genera por defecto datos Monte Carlo, metadata con seeds y un WRL de al menos 10 eventos. `analyze-ex1a` genera las figuras y el ajuste. Todo persiste en el host bajo `generated/`.

## Comandos

```bash
make help
make build
make test
make run-ex1a       # también ex1b, ex2, ex3 y ex4
make analyze-ex1a   # también ex1b, ex2, ex3 y ex4
make visualize-ex1a # también ex1b, ex2, ex3 y ex4
make visualize-all
make all FAST=1
make check-repo
```

- `FAST=1`: menos eventos, misma física.
- `FULL=1`: estadísticas de referencia.
- `VIS=0`: desactiva explícitamente la visualización automática de un `run`.
- `VIS_EVENTS=20`: cambia los eventos del WRL; valores menores que 10 fallan.
- `SEED=12345` y `VIS_SEED=10101`: controlan las seeds reproducibles.

El repositorio no contiene CSV, WRL, logs, builds ni datasets generados. Algunas figuras PNG FULL se publican como referencia sin sus datos fuente.

## Procedencia y licencia

Los ejecutables parten de ejemplos oficiales de Geant4 y conservan sus avisos de licencia. El archivo `LICENSE` reproduce la licencia de Geant4 aplicable a ese código derivado.

Consulte `docs/docker_quickstart.md`, `docs/physics_notes.md`, `docs/visualization.md` y `docs/expected_results.md`.
