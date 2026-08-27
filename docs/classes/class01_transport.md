# Antes de la clase

Para esta clase solo necesitas **Git** y **Docker**. No necesitas instalar Geant4, CMake ni Python en tu sistema.

```bash
git clone https://github.com/rmartinezra/geant4-particle-transport-course.git
cd geant4-particle-transport-course

docker pull rmartinezmaple/geant4-particle-transport-course:11.2.2
docker compose run --rm geant4-course make env-check
```

El último comando comprueba el entorno, compila únicamente los dos módulos Compton y ensaya VRML2FILE con un archivo temporal. Debe terminar con:

```text
Entorno listo para la Clase 1.
```

Antes de la clase **no ejecutes** `make test`, `make all`, `FULL=1` ni consultes los resultados FULL exactos. Esos comandos adelantan observables y ajustes que construiremos durante el curso.

Puedes imprimir o copiar la [hoja de trabajo](../../worksheets/class01.md). No contiene respuestas.

# Clase 1 — De la sección eficaz al evento Monte Carlo

## Pregunta central

> ¿Cómo convierte Geant4 una sección eficaz microscópica en una trayectoria y una interacción Monte Carlo?

La meta no es empezar por un fit ni memorizar clases de C++. La secuencia de trabajo es:

```text
teoría → predicción → pocos eventos → visualización → datos
       → cálculo manual → simulación → interpretación
```

Al terminar debes poder explicar cómo una propiedad microscópica termina convertida en una distancia aleatoria, un proceso y un estado final.

## Organización orientativa

| Bloque | Tema | Duración orientativa |
|---|---|---:|
| A | Física del transporte | 35–40 min |
| B | Práctica guiada 1A: transmisión | 35–40 min |
| C | Práctica guiada 1B: estado final | 25–30 min |
| D | Síntesis y primer mapa de Geant4 | 10–15 min |

Los tiempos son una guía. Conviene preservar el orden conceptual incluso si una discusión requiere más tiempo.

# Bloque A — Física del transporte

## 1. Sección eficaz microscópica

La sección eficaz microscópica de un proceso depende, en general, de la energía:

$$
\sigma(E)
$$

Sus unidades son de área: $\mathrm{cm}^2$ o barn, con $1\ \mathrm{barn}=10^{-24}\ \mathrm{cm}^2$. No es una probabilidad adimensional. Es una medida efectiva de la capacidad de **un centro dispersor** para producir una interacción.

Una sección eficaz mayor significa una interacción más probable al atravesar una misma población de centros, pero todavía necesitamos saber cuántos centros hay por unidad de volumen.

## 2. Densidad numérica

La densidad numérica

$$
n
$$

se mide en $\text{átomos}/\mathrm{cm}^3$. Describe cuántos centros dispersores ofrece el material por unidad de volumen. No debe confundirse con la densidad de masa en $\mathrm{g}/\mathrm{cm}^3$.

## 3. Sección eficaz macroscópica

Para un material homogéneo y un proceso dado:

$$
\Sigma(E)=n\,\sigma(E)
$$

$\Sigma$ tiene unidades de $\mathrm{cm}^{-1}$. Puede interpretarse como una tasa de interacción por unidad de longitud. Esta es la cantidad que conecta directamente la física microscópica con el transporte dentro de un volumen.

## 4. Camino libre medio

El camino libre medio es

$$
\lambda=\frac{1}{\Sigma}
$$

Sus unidades son $\mathrm{cm}$. $\lambda$ grande corresponde a interacciones poco frecuentes y trayectorias típicamente largas. $\lambda$ pequeña corresponde a interacciones frecuentes y distancias típicamente cortas.

No significa que todas las partículas recorran exactamente $\lambda$. Es el promedio de una distribución de distancias.

## 5. Supervivencia y primera interacción

La probabilidad de que una partícula recorra más de una distancia $x$ sin interactuar es

$$
P(X>x)=\exp(-\Sigma x)=\exp(-x/\lambda)
$$

La densidad de probabilidad de la distancia hasta la primera interacción es

$$
p(x)=\frac{1}{\lambda}\exp(-x/\lambda),\qquad x\ge 0
$$

La exponencial no afirma que la partícula pierda una fracción continua de sí misma. Describe una colección de historias: algunas interactúan pronto, otras tarde y otras salen del volumen sin interactuar.

## 6. De una sección eficaz a un número aleatorio

Si $\xi$ es uniforme entre cero y uno,

$$
\xi\sim U(0,1)
$$

entonces podemos muestrear una distancia exponencial mediante

$$
x=-\lambda\ln(\xi)
$$

Ejemplo: si $\lambda=3\ \mathrm{cm}$ y $\xi=0.5$,

$$
x=-3\ln(0.5)\approx 2.08\ \mathrm{cm}
$$

La cadena conceptual central es:

$$
\sigma(E)\rightarrow\Sigma(E)\rightarrow\lambda(E)
\rightarrow\text{número aleatorio}
\rightarrow\text{distancia hasta la interacción}
$$

Geant4 transforma así una propiedad microscópica en una trayectoria aleatoria. No hace falta una derivación más larga para usar esta idea correctamente.

## 7. Competencia entre procesos

Una partícula puede tener varios procesos disponibles. Sus secciones eficaces macroscópicas contribuyen a

$$
\Sigma_{\mathrm{total}}=\Sigma_1+\Sigma_2+\cdots
$$

Una vez determinada la próxima interacción, la probabilidad relativa de seleccionar el proceso $i$ es

$$
P_i=\frac{\Sigma_i}{\Sigma_{\mathrm{total}}}
$$

El transporte debe resolver dos preguntas distintas:

1. **¿Dónde o cuándo ocurre la próxima interacción?**
2. **¿Qué proceso produce esa interacción?**

En esta clase basta esta distinción. La arquitectura interna de `G4VProcess` queda para más adelante.

## 8. Tres niveles de descripción física

### Sección eficaz total

Responde principalmente: **¿con qué frecuencia ocurre una interacción?** Determina tasas, supervivencia y caminos libres.

### Sección eficaz diferencial

Responde: **una vez que ocurre, ¿cómo se distribuyen los estados finales?** Un ejemplo es

$$
\frac{d\sigma}{d\Omega}
$$

que distribuye direcciones dentro del ángulo sólido.

### Cinemática

Relaciona energía, momento, ángulo y masas entre el estado inicial y el final. La conservación impone relaciones posibles, mientras el modelo diferencial asigna probabilidades dentro de esas posibilidades.

Esta separación prepara las dos prácticas:

- 1A estudia principalmente **si ocurre** una interacción antes de salir;
- 1B estudia **qué estado final** se produce cuando ocurre Compton.

## Pausa de predicción

Sin ejecutar todavía el programa, discute:

- ¿Qué cambia en $\lambda$ si aumenta $\sigma$ y el material es el mismo?
- ¿Dos partículas con la misma energía deben recorrer la misma distancia?
- Si compiten dos procesos, ¿seleccionar el proceso y seleccionar la distancia son la misma decisión?

# Bloque B — Práctica guiada 1A

## ¿Cómo disminuye un haz gamma al atravesar aluminio?

Lanzaremos fotones de 300 keV contra aluminio. Antes de simular, registra una predicción:

> ¿Qué debería ocurrir con la fracción transmitida cuando aumenta el espesor?

Incluye la tendencia, una forma funcional plausible y el significado físico de caminos libres grandes o pequeños. No consultes todavía las gráficas de referencia.

## 1. Ejecutar sin analizar el fit

```bash
docker compose run --rm geant4-course make run-ex1a FAST=1
```

El target:

1. compila si hace falta;
2. genera una visualización WRL corta;
3. ejecuta un scan Monte Carlo FAST;
4. guarda datos y logs;
5. **no ejecuta el análisis completo**.

Revisa estas rutas:

```text
generated/visualization/ex1a/
generated/data/ex1a/
generated/logs/ex1a/
```

## 2. Mirar primero el WRL

Abre `generated/visualization/ex1a/compton_transmission_10events.wrl` con **Castle Model Viewer**. El visor se ejecuta en el sistema anfitrión y no forma parte del contenedor. En Windows con WSL:

```bash
./scripts/open_wrl_castle.sh \
  generated/visualization/ex1a/compton_transmission_10events.wrl
```

Si todavía no lo preparaste, ejecuta una vez `./scripts/setup_castle_viewer_windows.sh`. La [guía de visualización](../visualization.md) contiene el procedimiento completo.

Busca el haz incidente, el volumen de aluminio, trayectorias que alcanzan el límite y trayectorias que terminan en una interacción. Dependiendo de cómo el visor represente el vértice y las partículas creadas, también pueden distinguirse cambios de dirección o secundarios en el punto de interacción.

Preguntas para discutir antes de mirar el CSV:

1. ¿Qué representa una trayectoria individual?
2. ¿Todos los fotones interactúan?
3. ¿Cómo distinguirías una salida sin interacción de una interacción dentro del blanco?
4. ¿Puede, en un problema de transporte general, un fotón interactuar y aun así salir del volumen?

### Qué significa `N_transmitted` en este ejercicio

Aquí medimos supervivencia **hasta la primera interacción**. El código registra el proceso que termina el primer paso y detiene el evento:

- `Transportation`: el primario alcanzó el límite sin interacción Compton y cuenta en `N_transmitted`;
- `compt`: ocurrió la primera interacción dentro del aluminio y cuenta en `N_interacted`.

Por tanto, un fotón que interactuara y saliera más tarde no pertenece a `N_transmitted` en esta definición. Sería un observable distinto. Esta elección es coherente con $P(X>x)$ y con la distribución de la primera interacción.

## 3. Inspeccionar el CSV

```bash
docker compose run --rm geant4-course \
  bash -lc "head generated/data/ex1a/transmission_scan.csv"
```

Concéntrate primero en cuatro columnas:

| Columna real | Símbolo de trabajo | Significado |
|---|---|---|
| `thickness_cm` | $x$ | espesor de aluminio |
| `N0` | $N_0$ | fotones incidentes |
| `N_transmitted` | $N_{\mathrm{trans}}$ | fotones que salen sin interacción |
| `transmission` | $T$ | fracción $N_{\mathrm{trans}}/N_0$ |

Las demás columnas conservan incertidumbre, material, energía, seeds y referencias para la reproducibilidad. No necesitas analizarlas todas hoy.

## 4. Hacer un cálculo manual

Elige una fila con $0<T<1$ y anota sus valores. Calcula:

$$
T=\frac{N_{\mathrm{trans}}}{N_0}
$$

$$
\mu_{\mathrm{est}}\approx-\frac{\ln T}{x}
$$

$$
\lambda_{\mathrm{est}}\approx\frac{1}{\mu_{\mathrm{est}}}
$$

Comprueba unidades en cada paso. Un solo punto produce una estimación con ruido; distintos puntos no darán exactamente el mismo valor. En Clase 2 combinaremos todos los espesores mediante un modelo estadístico.

## 5. Detenerse antes del fit

En Clase 1 no uses como actividad principal:

```text
make analyze-ex1a
```

Hoy importa entender qué se contó y por qué aparece una exponencial. La likelihood binomial, el ajuste global, los residuos y las incertidumbres del parámetro se desarrollarán en Clase 2.

# Bloque C — Práctica guiada 1B

## ¿Qué ocurre después de la interacción?

En 1A preguntamos **cuándo** ocurre la primera interacción. Ahora preguntamos:

> Una vez que ocurre Compton, ¿qué estado final produce?

Antes de ejecutar, predice: si el fotón se dispersa hacia atrás, ¿conservará más o menos energía que si cambia muy poco de dirección?

## 1. Visualizar y producir eventos

```bash
docker compose run --rm geant4-course make run-ex1b FAST=1
```

Mira primero:

```text
generated/visualization/ex1b/compton_kinematics_10events.wrl
```

Ábrelo desde WSL con:

```bash
./scripts/open_wrl_castle.sh \
  generated/visualization/ex1b/compton_kinematics_10events.wrl
```

Identifica el fotón incidente, el punto de interacción, el fotón dispersado, el electrón de retroceso y el cambio de dirección cuando sean visibles. Una imagen de diez eventos sirve para formular preguntas; no reemplaza la estadística de miles de eventos.

## 2. Cinemática Compton

Para un electrón libre inicialmente en reposo, conservación de energía y momento conduce a

$$
E'=
\frac{E_0}
{1+\dfrac{E_0}{m_e c^2}(1-\cos\theta)}
$$

Aquí:

- $E_0$ es la energía inicial del fotón;
- $E'$ es la energía del fotón dispersado;
- $\theta$ es el ángulo de scattering;
- $m_e c^2$ es la energía de reposo del electrón.

No necesitamos derivar QED. La ecuación ideal es una consecuencia cinemática para ese estado inicial; la sección eficaz diferencial determina con qué frecuencia aparecen los distintos ángulos.

## 3. Inspeccionar eventos

```bash
docker compose run --rm geant4-course \
  bash -lc "head generated/data/ex1b/compton_events.csv"
```

Para uno o pocos eventos localiza:

| Columna | Significado |
|---|---|
| `E0_keV` | energía inicial $E_0$ |
| `Egamma_scattered_keV` | energía Monte Carlo $E'$ |
| `theta_deg` o `cos_theta` | ángulo de scattering |
| `electron_kinetic_energy_keV` | energía cinética del electrón |

Escoge un evento y:

1. anota $E_0$ y $\theta$;
2. calcula $E'$ ideal;
3. compara con $E'$ Monte Carlo;
4. describe el signo y tamaño de la diferencia sin convertir un caso en una conclusión estadística.

No exijas coincidencia exacta. El modelo Compton de Geant4 puede incluir electrones ligados y ensanchamiento Doppler. Una resolución instrumental artificial sería un efecto adicional y no se introduce en esta clase.

## 4. Detenerse antes del fit

No ejecutes todavía `make analyze-ex1b` como actividad principal. La linealización, el fit de $m_e c^2$, sus residuos y la interpretación de la incertidumbre pertenecen a Clase 2.

# Bloque D — Cierre conceptual

## La historia completa de un evento

$$
\begin{gathered}
\text{PARTÍCULA}\\
\downarrow\\
\sigma(E)\\
\downarrow\\
\lambda(E)\\
\downarrow\\
\text{número aleatorio}\\
\downarrow\\
\text{punto de interacción}\\
\downarrow\\
\text{proceso}\\
\downarrow\\
\text{estado final}\\
\downarrow\\
\text{nuevas energías, direcciones y tracks}
\end{gathered}
$$

Compton 1A y 1B son complementarios:

- 1A conecta sección eficaz total, supervivencia y distancia hasta la primera interacción;
- 1B conecta interacción, sección eficaz diferencial y cinemática del estado final.

## Primer contacto con la arquitectura de Geant4

Solo ahora asignamos nombres de software a partes del relato:

| Componente | Papel superficial en esta clase |
|---|---|
| `PrimaryGeneratorAction` | crea la partícula inicial |
| `DetectorConstruction` | define geometría y materiales |
| `PhysicsList` | selecciona procesos y modelos físicos |
| kernel de Geant4 | transporta, muestrea interacciones y crea estados finales |
| acciones de tracking, stepping y run | observan y registran lo ocurrido |

No es necesario estudiar todavía estas clases línea por línea, ni introducir sensitive detectors. Primero debe quedar clara la física que el software representa.

## Entrega mínima

Entrega únicamente:

1. la [hoja de trabajo](../../worksheets/class01.md) completa;
2. una captura de un WRL de 1A o 1B;
3. el cálculo manual de $T$, $\mu$ y $\lambda$ para un punto;
4. la comparación de un evento Compton con la cinemática ideal;
5. una respuesta corta: ¿cuál es la diferencia física entre 1A y 1B?

No se solicita un informe largo.

## Criterios de salida

Al finalizar debes poder responder, con tus propias palabras:

1. ¿Qué son $\sigma$, $\Sigma$ y $\lambda$ y qué unidades tienen?
2. ¿Por qué la distancia hasta la interacción es aleatoria?
3. ¿Cómo se muestrea una exponencial a partir de un uniforme?
4. ¿Qué diferencia existe entre sección eficaz total y diferencial?
5. ¿Qué representa una trayectoria y qué contiene un evento Monte Carlo?
6. ¿Cómo conecta una interacción microscópica con una trayectoria simulada?

## Nota para quien guía la clase

- Pida predicciones antes de mostrar cada ecuación o archivo.
- Abra WRL antes que CSV, y CSV antes que scripts de análisis.
- No muestre las gráficas FULL ni valores precisos durante la actividad.
- Si falta tiempo, preserve el cálculo manual de 1A y la inspección evento a evento de 1B.
- Reserve arquitectura detallada, likelihood, fits, residuos e incertidumbres para Clase 2.
