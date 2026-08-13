# Datasets de Geant4 incluidos

La imagen no instala todos los datasets de Geant4. Las pruebas en un entorno sin variables de datos demostraron que los módulos electromagnéticos de este curso funcionan sin datasets externos con la física seleccionada. La fisión HP sí requiere G4NDL.

| Ejercicio | Dataset | Contenido incluido | Motivo |
|---|---|---|---|
| 1A/1B Compton | ninguno externo | — | `G4EmStandardPhysics` y `G4KleinNishinaModel` de esta configuración funcionan sin `G4LEDATA`. |
| 2 MCS | ninguno externo | — | transporte EM estándar de muones. |
| 3 pérdida de energía | ninguno externo | — | pérdida EM estándar de muones. |
| 4 fisión U-235 | G4NDL 4.7.1 | 21 archivos `92_235_Uranium.z` (5.63 MB) | `NeutronHPFission`/`NeutronHPFissionXS`; también se conservan las tablas U-235 de elasticidad, captura e inelástica cargadas durante la inicialización de HP. |

El Dockerfile verifica el MD5 oficial `54f0ed3995856f02433d42ec96d70bc6` del tarball G4NDL antes de extraer el subconjunto. La prueba aislada de producción y VRML no produjo excepciones de datasets.

Se excluyen G4EMLOW, PhotonEvaporation, RadioactiveDecay, G4PARTICLEXS, G4PII, RealSurface, G4SAIDDATA, G4ABLA, G4INCL, G4ENSDFSTATE y G4TENDL porque estos cinco flujos validados no los consultan.
