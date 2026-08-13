# Datasets de Geant4 incluidos

La imagen no instala todos los datasets de Geant4. La selección se obtuvo ejecutando los cinco módulos en un contenedor sin acceso a los datos del host y añadiendo únicamente la tabla identificada por cada fallo. Después se repitieron producción y VRML con el conjunto resultante.

| Ejercicio | Dataset | Contenido incluido | Motivo |
|---|---|---|---|
| Todos | G4ENSDFSTATE 2.3 | completo | Tabla compacta obligatoria para inicializar `G4NuclideTable`. |
| 1A/1B, 2, 3 y secundarios de 4 | G4EMLOW 8.5 | completo | Datos EM de bremsstrahlung, ionización, fluorescencia y el modelo Compton ligado/Doppler. |
| 2, 3 y 4 | PhotonEvaporation 5.7 | completo | Niveles nucleares y desexcitación que inicializan `G4DecayPhysics` y la física hadrónica. |
| 4 | RadioactiveDecay 5.6 | completo | Requerido al inicializar `G4RadioactiveDecayPhysics` en la lista de Hadr03. |
| 4 | G4PARTICLEXS 4.0 | completo | Secciones eficaces de los canales inelásticos construidos por la lista hadrónica. |
| 4 fisión U-235 | G4NDL 4.7.1 | 21 archivos `92_235_Uranium.z` (5.63 MB) | `NeutronHPFission`/`NeutronHPFissionXS`; también se conservan las tablas U-235 de elasticidad, captura e inelástica cargadas durante la inicialización de HP. |

El Dockerfile fija y verifica los MD5 que distribuye Geant4 11.2.2 para los seis paquetes antes de extraerlos. La prueba aislada de producción y VRML no produjo excepciones de datasets.

Se excluyen G4PII, RealSurface, G4SAIDDATA, G4ABLA, G4INCL y G4TENDL porque estos cinco flujos validados no los consultan. G4NDL no se conserva completo: se verifica el tarball oficial y se extrae el subconjunto isotópico comprobado.
