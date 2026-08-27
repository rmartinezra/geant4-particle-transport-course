# Antes de la clase

La Clase 2 usa los eventos producidos en las prácticas Compton 1A y 1B para construir estimadores, incertidumbres, ajustes y diagnósticos. El entorno técnico es el mismo de la Clase 1: imagen Docker fijada en Geant4 11.2.2 y resultados persistentes en `generated/`.

Comprueba primero qué archivos tienes:

```bash
docker compose run --rm geant4-course make class02-help

test -s generated/data/ex1a/transmission_scan.csv
test -s generated/data/ex1b/compton_events.csv
```

Si alguno falta, genera una muestra rápida sin repetir la visualización:

```bash
docker compose run --rm geant4-course make run-ex1a FAST=1 VIS=0
docker compose run --rm geant4-course make run-ex1b FAST=1 VIS=0
```

No consultes todavía los [resultados de referencia](../expected_results.md). Primero registra tus decisiones en la [hoja de trabajo](../../worksheets/class02.md), ejecuta los ajustes y examina los residuos.

# Clase 2 — Del evento al resultado físico

## Pregunta central

> ¿Cómo se transforma una colección de eventos Monte Carlo en una estimación física defendible, con incertidumbre y controles de calidad?

La secuencia de trabajo será:

```text
pregunta → observable → modelo probabilístico → estimador
         → incertidumbre → residuos → comparación posterior → conclusión
```

Al terminar debes poder:

1. identificar la unidad estadística de un CSV;
2. distinguir observable, parámetro y referencia;
3. justificar una likelihood o una función de ajuste;
4. propagar incertidumbres a magnitudes derivadas;
5. leer residuos sin confundir fluctuación con sesgo;
6. comunicar configuración, resultado y limitaciones de forma reproducible.

## Organización orientativa

| Bloque | Tema | Duración orientativa |
|---|---|---:|
| A | Del CSV al modelo estadístico | 25–30 min |
| B | Compton 1A: likelihood binomial y sección eficaz | 40–45 min |
| C | Compton 1B: ajuste cinemático y residuos | 40–45 min |
| D | Reproducibilidad, comparación y entrega | 20–25 min |

# Bloque A — Del CSV al modelo estadístico

## 1. La fila no siempre representa lo mismo

Antes de calcular una media, pregunta qué representa una fila:

- en `transmission_scan.csv`, cada fila resume miles de fotones para un espesor;
- en `compton_events.csv`, cada fila representa una primera interacción Compton;
- una columna puede ser un conteo, una fracción, una energía, una dirección o metadatos.

La incertidumbre correcta depende de esa estructura. No es válido tratar seis fracciones de transmisión como si fueran seis eventos individuales ni tratar tres mil interacciones como si fueran tres mil configuraciones distintas.

## 2. Observable, parámetro y referencia

Mantén separados tres niveles:

| Nivel | Ejemplo 1A | Ejemplo 1B |
|---|---|---|
| Observable | $N_{\mathrm{trans}}$ de $N_0$ | $(\theta,E_\gamma')$ por evento |
| Parámetro ajustado | $\mu$ | $M=m_e c^2$ |
| Magnitud derivada | $\lambda=1/\mu$, $\sigma=\mu/n$ | comparación de $M$ con una referencia |

La referencia de Geant4 o el valor tabulado de $m_e c^2$ no entra en el fit. Se consulta después para evaluar el resultado.

## 3. Qué significa una incertidumbre

En esta clase, una incertidumbre de ajuste cuantifica cuánto fluctuaría el estimador bajo el modelo y el tamaño de muestra usados. No incluye automáticamente:

- incertidumbre del espesor o de la densidad;
- calibración de energía o ángulo;
- elección de la lista física;
- aproximaciones del modelo;
- sesgos de selección;
- resolución instrumental, salvo que se añada explícitamente.

Escribe siempre qué fuentes están incluidas y cuáles no.

## 4. Los residuos son una pregunta, no un adorno

Un valor ajustado puede parecer razonable y aun así dejar estructura en los residuos. Examina:

- centrado alrededor de cero;
- tendencia con la variable independiente;
- cambios de anchura;
- puntos extremos;
- agrupaciones o curvatura.

Un residuo grande no demuestra por sí solo que Geant4 esté mal. Puede revelar una fluctuación, una transformación poco conveniente, una aproximación ideal incompleta o una fuente de resolución no modelada.

## Pausa de diseño

Antes de ejecutar el análisis, completa en la hoja:

1. ¿Cuál es la unidad estadística de cada archivo?
2. ¿Qué parámetro quieres recuperar?
3. ¿Qué distribución o función conecta datos y parámetro?
4. ¿Qué gráfico de residuos permitiría detectar una estructura no explicada?

# Bloque B — Compton 1A: de conteos a sección eficaz

## 1. Auditar los datos antes del fit

Inspecciona cabecera y primeras filas:

```bash
docker compose run --rm geant4-course \
  bash -lc "head generated/data/ex1a/transmission_scan.csv"
```

Comprueba para cada espesor:

$$
N_{\mathrm{trans}}+N_{\mathrm{interacted}}=N_0
$$

$$
T=\frac{N_{\mathrm{trans}}}{N_0}
$$

Predice también si $T$ debería crecer o decrecer con $x$. Una inversión pequeña puede ser fluctuación; una tendencia sistemática contraria exigiría revisar datos y código.

## 2. Modelo probabilístico

Para el espesor $x_i$, el número transmitido se modela como

$$
K_i\sim\mathrm{Binomial}(N_i,p_i)
$$

con

$$
p_i=\exp(-\mu x_i)
$$

La likelihood conjunta es

$$
L(\mu)=\prod_i
\binom{N_i}{K_i}
p_i^{K_i}(1-p_i)^{N_i-K_i}
$$

y, salvo una constante que no depende de $\mu$, la log-likelihood es

$$
\ell(\mu)=
\sum_i\left[
K_i\ln p_i+(N_i-K_i)\ln(1-p_i)
\right]
$$

El análisis minimiza $-\ell(\mu)$ con la restricción física $\mu>0$.

## 3. Incertidumbre de $\mu$

Para este modelo, la información de Fisher esperada es

$$
I(\mu)=\sum_i
\frac{N_i x_i^2p_i}{1-p_i}
$$

y la aproximación usada por el script es

$$
s_\mu\approx\frac{1}{\sqrt{I(\widehat\mu)}}
$$

La expresión aprovecha directamente que cada punto procede de conteos binomiales. Esta es la razón para preferir la likelihood como ajuste principal frente a ajustar fracciones sin conservar $N_i$.

## 4. Ejecutar el análisis

```bash
docker compose run --rm geant4-course make analyze-ex1a
```

Revisa:

```text
generated/fits/ex1a/summary_A.txt
generated/figures/ex1a/transmission_vs_thickness.png
generated/figures/ex1a/log_transmission_vs_thickness.png
generated/figures/ex1a/transmission_residuals.png
```

El resumen informa tres estimaciones de $\mu$:

1. máxima verosimilitud binomial, resultado principal;
2. ajuste ponderado de $T=\exp(-\mu x)$;
3. ajuste lineal ponderado de $\ln T=-\mu x$.

No promedies automáticamente los tres valores. Compáralos como diagnóstico: utilizan transformaciones y aproximaciones distintas sobre los mismos datos.

## 5. Propagar a $\lambda$ y $\sigma$

Una vez obtenido $\widehat\mu$:

$$
\widehat\lambda=\frac{1}{\widehat\mu}
$$

$$
s_\lambda\approx
\left|\frac{d\lambda}{d\mu}\right|s_\mu
=\frac{s_\mu}{\widehat\mu^2}
$$

Con densidad numérica $n$:

$$
\widehat\sigma=\frac{\widehat\mu}{n}
$$

$$
s_\sigma=\frac{s_\mu}{n}
$$

Comprueba dimensiones:

```text
mu       : cm^-1
lambda   : cm
n        : átomos cm^-3
sigma    : cm^2 átomo^-1
1 barn   : 10^-24 cm^2
```

## 6. Residuos de Pearson

Para cada espesor, el script calcula

$$
r_i=
\frac{K_i-N_i\widehat p_i}
{\sqrt{N_i\widehat p_i(1-\widehat p_i)}}
$$

con $\widehat p_i=\exp(-\widehat\mu x_i)$. El gráfico muestra $r_i$ frente a $x_i$ y líneas orientativas en $\pm2$.

No conviertas esas líneas en una regla mecánica. Con pocos espesores, interesa más buscar estructura coherente que contar cuántos puntos cruzan un umbral.

Discute:

1. ¿Los residuos alternan alrededor de cero o presentan una tendencia?
2. ¿Un espesor domina visualmente el desacuerdo?
3. ¿Cambiar de FAST a FULL debería reducir la dispersión típica?
4. ¿Una incertidumbre menor garantiza que el modelo sea correcto?

# Bloque C — Compton 1B: recuperar una escala de energía

## 1. Auditar eventos

```bash
docker compose run --rm geant4-course \
  bash -lc "head generated/data/ex1b/compton_events.csv"
```

Comprueba:

- `process_name` debe ser `compt`;
- $0<E_\gamma'\le E_0$;
- $-1\le\cos\theta\le1$;
- las direcciones inicial y final deben ser unitarias;
- el producto escalar de direcciones debe coincidir con `cos_theta`;
- energía del gamma, electrón, depósito local y otros secundarios deben cerrar el balance dentro de la precisión guardada.

Estas comprobaciones ocurren antes del fit. Si fallan, el script se detiene en lugar de producir una figura convincente con datos inconsistentes.

## 2. Modelo cinemático

Para un electrón libre inicialmente en reposo:

$$
E_\gamma'(\theta;M)=
\frac{E_0M}{M+E_0(1-\cos\theta)}
$$

donde

$$
M=m_ec^2
$$

se trata como parámetro libre y positivo.

El ajuste no lineal minimiza la suma de residuos cuadrados en energía:

$$
S(M)=\sum_j
\left[
E_{\gamma,j}'-E_\gamma'(\theta_j;M)
\right]^2
$$

La curva ideal organiza la correlación, pero los eventos de Geant4 pueden dispersarse alrededor de ella por electrones ligados y ensanchamiento Doppler.

## 3. Linealización

La relación también puede escribirse como

$$
X=1-\cos\theta,
\qquad
Y=\frac{1}{E_\gamma'}-\frac{1}{E_0}
$$

de modo que

$$
Y=\frac{X}{M}
$$

El ajuste físico pasa por el origen y tiene pendiente $1/M$. El script añade un ajuste con intercepto libre como diagnóstico:

$$
Y=aX+b
$$

Un $b$ compatible con cero apoya la forma esperada, pero no sustituye la inspección de residuos ni prueba por sí solo que todas las hipótesis sean exactas.

## 4. Ejecutar el análisis

```bash
docker compose run --rm geant4-course make analyze-ex1b
```

O ejecuta ambas prácticas de la clase:

```bash
docker compose run --rm geant4-course make analyze-class02
```

Revisa:

```text
generated/fits/ex1b/summary_B.txt
generated/figures/ex1b/compton_energy_vs_angle.png
generated/figures/ex1b/compton_linearized.png
generated/figures/ex1b/compton_residuals.png
generated/figures/ex1b/compton_angle_distribution.png
```

## 5. Interpretar los residuos

El residuo no lineal de cada evento es

$$
r_j=E_{\gamma,j}'-
E_\gamma'(\theta_j;\widehat M)
$$

El gráfico superpone los eventos y la mediana por intervalos angulares. Busca dos cosas distintas:

- **centro:** si la mediana se aleja de cero de forma sistemática;
- **anchura y colas:** si la dispersión cambia con $\theta$ o aparecen eventos extremos.

Una nube ancha pero centrada puede ser compatible con una relación media adecuada y física atómica adicional. Una tendencia del centro indicaría que un único $M$ no describe igualmente todas las regiones angulares.

## 6. Incertidumbre del ajuste

El script estima la varianza residual y la combina con la sensibilidad del modelo a $M$ mediante el Jacobiano del ajuste. La incertidumbre resultante describe la precisión del parámetro dentro de esta muestra y este modelo.

No la presentes como incertidumbre experimental total de la masa del electrón. Aquí no se han incluido calibraciones, alineación, aceptación ni resolución instrumental real.

## 7. Experimento opcional de resolución

Después de guardar el resultado ideal, puedes añadir un smearing artificial solo durante el análisis. Usa rutas distintas para no sobrescribir el resultado principal:

```bash
docker compose run --rm geant4-course bash -lc '
python3 exercises/01_compton/B_kinematics/analysis/analyze_compton.py \
  --input generated/data/ex1b/compton_events.csv \
  --summary generated/fits/ex1b/summary_B_smeared.txt \
  --figure-dir generated/figures/ex1b_smeared \
  --energy-resolution-frac 0.02 \
  --angular-resolution-deg 1.0 \
  --seed 314159'
```

Predice antes de ejecutar:

1. ¿Cambiará el centro del estimador o principalmente su incertidumbre?
2. ¿Qué ocurrirá con la anchura de los residuos?
3. ¿Por qué la seed del smearing debe registrarse?

# Bloque D — Reproducibilidad y comunicación

## 1. Qué conservar

Una entrega reproducible debe identificar:

- commit del repositorio;
- imagen y versión de Geant4;
- `FAST=1`, modo normal o `FULL=1`;
- número de eventos y seeds;
- CSV de entrada;
- script y opciones de análisis;
- resumen del fit;
- figuras principales y residuos;
- decisión sobre cuándo se consultó la referencia.

Consulta el commit con:

```bash
git rev-parse HEAD
```

Los JSON de metadatos y logs bajo `generated/` complementan esa información.

## 2. FAST no significa física diferente

`FAST=1` reduce el número de eventos. Es útil para aprender el flujo y detectar errores, pero produce incertidumbres mayores y residuos más variables. `FULL=1` conserva la configuración física y aumenta la estadística de producción.

No repitas corridas hasta obtener por casualidad el resultado más cercano a la referencia. Define la configuración y la seed antes de mirar el valor ajustado.

## 3. Comparación posterior

Solo después de cerrar el ajuste:

1. registra tu resultado sin modificarlo;
2. consulta la referencia;
3. calcula diferencia absoluta y relativa;
4. compara la diferencia con la incertidumbre declarada;
5. discute fuentes no incluidas antes de afirmar acuerdo o desacuerdo.

Una diferencia porcentual pequeña no corrige un análisis mal planteado, y una fluctuación visible no invalida automáticamente el modelo.

## 4. Plantilla de conclusión

Una conclusión breve puede seguir esta estructura:

> A partir de [observable] y usando [modelo/likelihood], obtuvimos [parámetro] con [incertidumbre y unidades]. Los residuos [descripción concreta]. La comparación posterior con [referencia] muestra [diferencia], dentro de un análisis que incluye [fuentes] pero no incluye [limitaciones].

## Entrega mínima

Entrega:

1. [hoja de trabajo de la Clase 2](../../worksheets/class02.md);
2. tabla corta con los resultados de 1A y 1B, unidades e incertidumbres;
3. figura principal y figura de residuos de cada práctica;
4. comparación entre los tres métodos de 1A;
5. comparación entre ajuste no lineal y lineal de 1B;
6. un párrafo de reproducibilidad y otro de limitaciones;
7. comparación con referencias realizada únicamente al final.

## Criterios de salida

Al finalizar debes poder explicar:

1. por qué 1A se modela con conteos binomiales;
2. por qué ajustar $\ln T$ no es idéntico a maximizar la likelihood;
3. cómo se propaga $s_\mu$ a $s_\lambda$ y $s_\sigma$;
4. qué revela un residuo de Pearson;
5. qué parámetro representa la pendiente de la linealización Compton;
6. por qué los eventos no caen exactamente sobre la curva de electrón libre;
7. qué incluye y qué excluye cada incertidumbre reportada;
8. cómo una seed, una versión y un commit hacen reproducible el resultado.
