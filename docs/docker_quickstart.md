# Inicio rápido con Docker

## Construir y comprobar

```bash
docker compose build
docker compose run --rm geant4-course geant4-config --version
docker compose run --rm geant4-course make test
```

El segundo comando debe imprimir `11.2.2`. `make test` realiza build, genera cinco WRL, ejecuta los cinco módulos FAST, analiza sus CSV y aplica tolerancias físicas docentes.

## Persistencia

Compose monta el checkout como `/workspace`. Los datos, figuras, fits, logs y WRL quedan en `generated/` del host aunque se elimine el contenedor.

## Permisos

En Linux, Compose ejecuta con `${UID}:${GID}` y evita archivos propiedad de root. Si esas variables no existen se usa `1000:1000`, compatible con la mayoría de instalaciones y con Docker Desktop/WSL2. Se puede indicar otra identidad:

```bash
UID=$(id -u) GID=$(id -g) docker compose run --rm geant4-course make run-ex2 FAST=1
```

## Modos

```bash
docker compose run --rm geant4-course make run-ex3 FAST=1
docker compose run --rm geant4-course make run-ex3 FULL=1 VIS_EVENTS=20
docker compose run --rm geant4-course make run-ex3 VIS=0
```

FAST y FULL cambian únicamente estadística/puntos de producción. La configuración visual es corta e independiente.
