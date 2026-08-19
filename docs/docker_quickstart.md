# Inicio rápido con Docker

## Descargar y comprobar

La imagen pública ya contiene Geant4 11.2.2 y todas las dependencias. No necesitas construirla:

```bash
docker pull rmartinezmaple/geant4-particle-transport-course:11.2.2
docker compose run --rm geant4-course make env-check
```

`env-check` confirma la versión exacta `11.2.2`, las dependencias, los datasets, la escritura, la compilación de los dos módulos Compton y un WRL temporal. No ejecuta barridos, análisis ni fits.

Antes de la Clase 1 no ejecutes `make test`, `make all` ni `FULL=1`: esos flujos recorren material posterior y pueden revelar resultados.

Compose también descarga la imagen automáticamente si todavía no existe, pero el `docker pull` explícito permite ver con claridad el progreso y confirmar la etiqueta usada.

## Validación integral posterior

Cuando el docente lo indique, `make test` compila los cinco módulos, genera sus WRL, ejecuta simulaciones FAST, analiza los CSV y aplica tolerancias físicas docentes:

```bash
docker compose run --rm geant4-course make test
```

Este comando no forma parte de la preparación de la Clase 1.

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

## Construcción local opcional

Solo hace falta construir la imagen si quieres auditar el Dockerfile o modificar Geant4:

```bash
docker compose -f compose.yaml -f compose.build.yaml build
docker compose run --rm geant4-course geant4-config --version
```

El archivo `compose.build.yaml` añade el bloque de construcción al servicio normal. El flujo de estudiantes usa únicamente `compose.yaml` y la imagen pública.

## Actualizar la imagen

La etiqueta del curso queda fijada en `11.2.2` para preservar la reproducibilidad:

```bash
docker pull rmartinezmaple/geant4-particle-transport-course:11.2.2
```

No uses `latest` para entregar resultados evaluables; una etiqueta explícita evita cambios inesperados.

## Problemas frecuentes

- **Docker no está iniciado:** abre Docker Desktop o inicia el servicio Docker y repite el comando.
- **Permiso denegado en Linux:** comprueba que tu usuario pertenece al grupo `docker` o ejecuta Docker según la política de tu laboratorio.
- **Archivos propiedad de root:** antepone `UID=$(id -u) GID=$(id -g)` al comando Compose.
- **Poco espacio:** la imagen ocupa aproximadamente 1.96 GB sin comprimir; `docker system df` muestra el uso local.
- **Una corrida FULL tarda mucho:** empieza con `FAST=1`; la física es la misma y cambia la estadística.
