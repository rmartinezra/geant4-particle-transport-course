# Clase 2 — Hoja de trabajo

Nombre: ________________________________________

Fecha: _________________________________________

Commit del repositorio: ____________________________________________________

Modo de producción requerido: `FULL=1`

Seed base de Clase 2: _______________________________________________________

Trabaja primero con tus datos y consulta los resultados de referencia únicamente cuando la hoja lo indique.

## Parte A — Plan de análisis

### Unidad estadística

¿Qué representa una fila de `transmission_scan.csv`?

____________________________________________________________________________

¿Qué representa una fila de `compton_events.csv`?

____________________________________________________________________________

### Tres niveles

Completa:

| Práctica | Observable | Parámetro ajustado | Magnitud derivada o comparación |
|---|---|---|---|
| 1A | __________________ | __________________ | _______________________________ |
| 1B | __________________ | __________________ | _______________________________ |

### Incertidumbres

Escribe dos fuentes incluidas en el análisis actual:

1. _________________________________________________________________________
2. _________________________________________________________________________

Escribe tres fuentes que no están incluidas automáticamente:

1. _________________________________________________________________________
2. _________________________________________________________________________
3. _________________________________________________________________________

## Parte B — Compton 1A

### Auditoría del CSV

Archivo analizado: __________________________________________________________

Número de espesores: __________________

Eventos por espesor: __________________ (esperado: 100 000)

Material: _____________________________

Energía: _________________________ keV

Para una fila, registra:

$x=$ __________________ cm

$N_0=$ __________________

$N_{\mathrm{trans}}=$ __________________

$N_{\mathrm{interacted}}=$ __________________

$T=$ __________________

¿Se cumple $N_{\mathrm{trans}}+N_{\mathrm{interacted}}=N_0$? ______________

Describe la tendencia de $T$ con $x$:

____________________________________________________________________________

### Modelo

Completa:

$$
K_i\sim\underline{\hspace{4cm}}(N_i,p_i)
$$

$$
p_i=\underline{\hspace{4cm}}(-\mu x_i)
$$

¿Por qué el ajuste principal debe conservar $N_i$ y $K_i$, en vez de usar únicamente seis valores de $T_i$?

____________________________________________________________________________

____________________________________________________________________________

### Resultado principal

Método: ____________________________________________________________________

$\widehat\mu=$ __________________ $\pm$ __________________ cm⁻¹

$\widehat\lambda=$ ______________ $\pm$ __________________ cm

$\widehat\sigma=$ _______________ $\pm$ __________________ barn/átomo

Densidad numérica usada:

$n=$ __________________________________ átomos/cm³

Escribe las relaciones de propagación:

$$
s_\lambda=\underline{\hspace{7cm}}
$$

$$
s_\sigma=\underline{\hspace{7cm}}
$$

### Comparación de métodos

| Método | $\mu$ [cm⁻¹] | Incertidumbre [cm⁻¹] | Comentario |
|---|---:|---:|---|
| Likelihood binomial | __________ | __________ | __________________ |
| Exponencial ponderado | __________ | __________ | __________________ |
| Lineal en $\ln T$ | __________ | __________ | __________________ |

¿Los tres resultados FULL son compatibles dentro de sus incertidumbres? Explica sin promediarlos:

____________________________________________________________________________

____________________________________________________________________________

### Residuos

$\chi^2_{\mathrm{Pearson}}=$ __________________

Grados de libertad: __________________

$\chi^2/\mathrm{dof}=$ __________________

Máximo $|r_i|=$ __________________

Describe el gráfico `transmission_residuals.png`:

- ¿Está centrado alrededor de cero? ________________________________________
- ¿Hay tendencia con el espesor? ___________________________________________
- ¿Hay un punto que domine? ________________________________________________

Conclusión provisional de 1A, todavía sin mirar la referencia:

____________________________________________________________________________

____________________________________________________________________________

## Parte C — Compton 1B

### Auditoría de eventos

Archivo analizado: __________________________________________________________

Número de eventos: __________________ (esperado: 200 000)

$E_0=$ __________________ keV

Procesos encontrados: ______________________________________________________

Máximo residuo absoluto del balance completo de energía: _____________ keV

¿Qué columnas verifican que las direcciones sean unitarias?

____________________________________________________________________________

### Modelo no lineal

Parámetro libre: ______________________________

Unidades: _____________________________________

Restricción física aplicada: __________________

$\widehat M_{\mathrm{no\ lineal}}=$ __________ $\pm$ __________ keV

¿Qué se minimiza en este ajuste?

____________________________________________________________________________

### Linealización

Define:

$$
X=\underline{\hspace{7cm}}
$$

$$
Y=\underline{\hspace{7cm}}
$$

Relación entre pendiente y masa:

$$
\text{pendiente}=\underline{\hspace{7cm}}
$$

$\widehat M_{\mathrm{lineal}}=$ ______________ $\pm$ ______________ keV

$\widehat M_{\mathrm{intercepto\ libre}}=$ ____ $\pm$ ______________ keV

Intercepto libre: __________________ keV⁻¹

¿Qué pregunta diagnóstica responde permitir un intercepto distinto de cero?

____________________________________________________________________________

____________________________________________________________________________

### Residuos cinemáticos

Media de $E_\gamma'-E_\mathrm{fit}'$: __________________ keV

RMS: __________________ keV

Máximo absoluto: __________________ keV

Describe por separado:

- centro de los residuos: __________________________________________________
- anchura: _________________________________________________________________
- colas: ___________________________________________________________________
- dependencia con $\theta$: ________________________________________________

¿Por qué una nube no nula puede existir incluso sin resolución instrumental artificial?

____________________________________________________________________________

____________________________________________________________________________

### Resolución opcional

Si ejecutaste el smearing:

Resolución relativa de energía: __________________

Resolución angular: __________________ grados

Seed: __________________

Cambio en $\widehat M$: ____________________________________________________

Cambio en su incertidumbre: ________________________________________________

Cambio en los residuos: ____________________________________________________

## Parte D — Comparación posterior

Solo ahora consulta los resultados de referencia.

| Magnitud | Resultado propio | Referencia | Diferencia relativa |
|---|---:|---:|---:|
| $\sigma$ Compton 1A | __________ | __________ | __________ % |
| $m_ec^2$ Compton 1B | __________ | __________ | __________ % |

¿La referencia se utilizó como entrada, restricción o criterio para repetir seeds?

`Sí` / `No`

La respuesta correcta para este flujo debe ser `No`. Si marcaste `Sí`, explica qué debes rehacer:

____________________________________________________________________________

## Parte E — Reproducibilidad y comunicación

### Registro mínimo

- [ ] Commit anotado.
- [ ] Geant4 11.2.2 confirmado.
- [ ] Producción `FULL=1` confirmada.
- [ ] 100 000 eventos por espesor confirmados en 1A.
- [ ] 200 000 eventos confirmados en 1B.
- [ ] Número de eventos registrado.
- [ ] Seeds de simulación registradas.
- [ ] Seed de smearing registrada, si aplica.
- [ ] CSV de entrada identificado.
- [ ] Resúmenes de fits conservados.
- [ ] Figuras principales conservadas.
- [ ] Figuras de residuos conservadas.
- [ ] Referencias consultadas solo al final.

### Conclusión de 1A

En tres o cuatro frases incluye observable, modelo, resultado con incertidumbre, residuos y limitación principal:

____________________________________________________________________________

____________________________________________________________________________

____________________________________________________________________________

### Conclusión de 1B

En tres o cuatro frases incluye observable, modelo, resultado con incertidumbre, residuos y limitación principal:

____________________________________________________________________________

____________________________________________________________________________

____________________________________________________________________________

## Entrega mínima

- [ ] Hoja completa.
- [ ] Tabla de resultados de 1A y 1B.
- [ ] `transmission_vs_thickness.png`.
- [ ] `transmission_residuals.png`.
- [ ] `compton_energy_vs_angle.png` o `compton_linearized.png`.
- [ ] `compton_residuals.png`.
- [ ] Comparación entre métodos.
- [ ] Registro de reproducibilidad.
- [ ] Conclusiones y limitaciones.
