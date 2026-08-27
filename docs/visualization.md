# Visualización de WRL con Castle Model Viewer

Geant4 genera la escena; **Castle Model Viewer** la abre. Son dos etapas independientes:

```text
Docker + Geant4 ──VRML2FILE──> archivo .wrl ──Castle en el host──> escena 3D
```

WRL es la extensión habitual de VRML. El driver `VRML2FILE` de Geant4 escribe geometría y trayectorias en un archivo de texto cuya primera línea es `#VRML V2.0 utf8`. No necesita servidor gráfico, por lo que la simulación funciona dentro del contenedor aunque el visor se ejecute fuera de Docker.

## 1. Generar una escena

Por ejemplo, para la práctica Compton 1A:

```bash
docker compose run --rm geant4-course make visualize-ex1a
```

Cada `visualization.mac` abre `VRML2FILE`, dibuja el volumen, activa el almacenamiento de trayectorias, acumula eventos y cierra la escena. El script comprueba el driver, la cabecera y el tamaño antes de conservar el archivo.

En Compton 1A y 1B se usa una leyenda deliberadamente visible:

| Color | Significado |
|---|---|
| Verde | trayectoria del fotón primario hasta salir o alcanzar la primera interacción |
| Amarillo | dirección del fotón dispersado desde el vértice Compton |
| Rojo | dirección del electrón de retroceso desde el mismo vértice |

Los segmentos amarillo y rojo conservan las direcciones calculadas por Geant4, pero sus longitudes se escalan a `1.5 cm` y `1.0 cm` para que sean visibles. **No representan el alcance físico** del gamma ni del electrón. La producción numérica continúa deteniendo el evento en la primera interacción; esta ayuda existe únicamente en el WRL docente.

Las rutas predeterminadas son:

```text
generated/visualization/ex1a/compton_transmission_10events.wrl
generated/visualization/ex1b/compton_kinematics_10events.wrl
generated/visualization/ex2/muon_mcs_10events.wrl
generated/visualization/ex3/muon_energy_loss_10events.wrl
generated/visualization/ex4/neutron_fission_10events.wrl
```

## 2. Preparar Castle en Windows con WSL

[Castle Model Viewer](https://castle-engine.io/castle-model-viewer) es el nombre actual del antiguo `view3dscene` y admite VRML 2.0. Para evitar problemas de ventanas con WSLg, este curso recomienda la aplicación nativa de Windows x86_64.

Desde la terminal WSL, pero **no dentro del contenedor Docker**, ejecuta una sola vez:

```bash
./scripts/setup_castle_viewer_windows.sh
```

El script descarga la versión estable fijada por el curso, verifica su SHA-256 y la descomprime en `%USERPROFILE%\Apps\CastleModelViewer-5.2.0`. Es una aplicación portátil: no modifica el registro ni requiere permisos de administrador.

Para una instalación manual:

1. descarga la versión estable `Windows (x86_64)` desde la [página oficial](https://castle-engine.io/castle-model-viewer);
2. descomprime el ZIP en una carpeta permanente;
3. abre `castle-model-viewer.exe` y usa **File → Open** para seleccionar el WRL.

En Linux nativo, descarga el paquete Linux oficial y deja `castle-model-viewer` disponible en `PATH`, o define `CASTLE_VIEWER_EXE` con su ruta.

## 3. Abrir el WRL

En Windows con WSL:

```bash
./scripts/open_wrl_castle.sh \
  generated/visualization/ex1a/compton_transmission_10events.wrl
```

El script convierte la ruta Linux a una ruta Windows e inicia Castle fuera de WSLg. Para utilizar otra instalación:

```bash
CASTLE_VIEWER_EXE=/ruta/al/castle-model-viewer.exe \
  ./scripts/open_wrl_castle.sh generated/visualization/ex1a/compton_transmission_10events.wrl
```

### Crear una captura PNG reproducible

Castle también puede renderizar el WRL sin depender de una ventana interactiva:

```bash
./scripts/open_wrl_castle.sh --screenshot \
  generated/visualization/ex1a/compton_transmission_castle.png \
  generated/visualization/ex1a/compton_transmission_10events.wrl
```

El helper crea una imagen de `1000 × 700` con antialiasing y se niega a sobrescribir una captura existente. Esta opción sirve para la entrega de Clase 1 y para diagnosticar si el problema está en el WRL o únicamente en la presentación de la ventana.

## 4. Orientarse en la escena

Usa el modo **Examine**, adecuado para inspeccionar un blanco y sus trayectorias:

- arrastrar con botón izquierdo: rotar;
- rueda o arrastrar con botón derecho: acercar y alejar;
- `Shift` + arrastrar con botón izquierdo: desplazar;
- `Home`: recuperar una vista útil si la escena queda fuera de cámara;
- `Space`: detener una rotación accidental.

En Compton 1A busca el haz verde, el bloque de aluminio y la diferencia entre líneas que atraviesan el blanco y líneas que terminan en un vértice con vectores amarillo y rojo. En Compton 1B relaciona, para cada vértice, el fotón dispersado amarillo y el electrón de retroceso rojo.

Las escenas contienen solo diez eventos para que las trayectorias sigan siendo legibles. No representan la estadística completa del análisis.

## 5. Si no aparece la ventana o la escena

1. Confirma que el WRL existe y tiene cabecera válida:

   ```bash
   test -s generated/visualization/ex1a/compton_transmission_10events.wrl
   head -n 1 generated/visualization/ex1a/compton_transmission_10events.wrl
   ```

   La segunda orden debe imprimir `#VRML V2.0 utf8`.

2. Ejecuta Castle mediante `open_wrl_castle.sh`; no ejecutes `view3dscene` dentro de WSL.
3. Usa `Alt` + `Tab` para llevar Castle al frente y pulsa `Home` dentro del visor.
4. Si Castle abre pero no carga el archivo, usa **File → Open** y selecciona el mismo WRL desde el checkout.
5. Genera una captura con `open_wrl_castle.sh --screenshot` y compárala con las imágenes publicadas en la [galería del README](../README.md#primero-observa-las-simulaciones). Esas PNG proceden de WRL reales del curso.

Los WRL generados están ignorados por Git; solo se publican las capturas pequeñas usadas como referencia visual.
