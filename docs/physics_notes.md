# Notas de física y política de referencias

## Principio común

La magnitud principal siempre se reconstruye de eventos. Una referencia interna de Geant4 o Highland se evalúa después y nunca selecciona, corrige, normaliza o recorta datos Monte Carlo.

## Compton A

$T=N_{\mathrm{trans}}/N_0$ se ajusta con una likelihood binomial a $\exp(-\mu x)$. Después se calculan $\lambda=1/\mu$ y $\sigma=\mu/n$, con unidades explícitas. Solo entonces se lee la referencia de `G4EmCalculator`.

## Compton B

Se ajustan la relación angular y

$$
\frac{1}{E'}-\frac{1}{E_0}=\frac{1-\cos\theta}{m_e c^2}
$$

El parámetro $m_e c^2$ es libre. El modelo Compton de Geant4 puede incluir electrones ligados y Doppler broadening: los eventos no tienen que caer exactamente sobre la curva ideal de un electrón libre inicialmente en reposo.

La incertidumbre del fit es dispersión estadística del modelo Monte Carlo, no una medición experimental de la incertidumbre de la masa del electrón. La referencia física de $510.999\ \mathrm{keV}$, los efectos del modelo y una eventual resolución instrumental artificial son conceptos distintos.

En los WRL docentes, el gamma dispersado y el electrón de retroceso se dibujan como vectores de dirección escalados. Sus orientaciones proceden del estado final de la primera interacción; sus longitudes visuales no representan rangos ni caminos libres.

## MCS

Las direcciones simuladas producen $\theta_x$, $\theta_y$ y $\theta_{\mathrm{total}}$. Se guardan media, desviación estándar, RMS y cuantiles $q_{16}/q_{50}/q_{84}$. El estimador principal es $\sigma_{\mathrm{core}}=(q_{84}-q_{16})/2$; los exponentes de espesor y momento quedan libres. Highland aparece únicamente como comparación posterior en Python.

## Pérdida de energía

Se distinguen $E_{\mathrm{in}}-E_{\mathrm{out}}$ del primario, depósito local y energía transferida a secundarios. Cada configuración informa $N$, media, desviación estándar, SEM, mediana, $q_{16}$ y $q_{84}$. Las colas radiativas largas hacen que la media converja lentamente incluso con muchos eventos; no se ocultan ni se aumenta $N$ para hacerlas desaparecer.

## Fisión

El blanco es U-235 isotópico puro, el primario es un neutrón de $1\ \mathrm{eV}$ y solo queda activo `nFission`. Geant4 11.2.2 usa `G4HadronPhysicsQGSP_BIC_HP`, `NeutronHPFission` y `NeutronHPFissionXS` de G4NDL 4.7.1.

Un escape es censura derecha. El estimador no agrupado es $\widehat{\lambda}=\sum\mathrm{exposiciones}/N_{\mathrm{fisiones}}$; cada escape aporta toda su distancia dentro del material. Después se obtiene $\Sigma=1/\lambda$ y $\sigma=\Sigma/n$.
