# Experimento 4 — Sección eficaz de fisión en U-235

## OBJETIVO

Reconstruir la sección eficaz `nFission` a partir de la primera distancia de fisión y censura derecha.

## QUÉ SIMULAR

Neutrones de 1 eV en U-235 isotópico puro con `G4HadronPhysicsQGSP_BIC_HP`, `NeutronHPFission` y `NeutronHPFissionXS`.

## QUÉ MEDIR

ID, energía, interacción, distancia, escape, exposición dentro del material y nombre de proceso. Ningún escape se elimina.

## QUÉ AJUSTAR

Likelihood exponencial censurada: `lambda_hat=exposición_total/N_fisiones`.

## QUÉ OBTENER

`Sigma=1/lambda` y `sigma_f=Sigma/n`. `G4HadronicProcessStore` se consulta solo después para exactamente `nFission`.

## VISUALIZACIÓN

La geometría visual usa 2 cm para observar fisiones y productos secundarios en 10 eventos; producción usa 0.5 cm para conservar una fracción útil de escapes censurados. No hay biasing.

## RESULTADOS ESPERADOS

`lambda≈0.30 cm` y `sigma_f≈68 barn` a 1 eV, con variación estadística.

## PREGUNTAS

¿Qué sesgo aparece si se eliminan escapes? ¿Por qué la configuración visual puede diferir en longitud sin cambiar la física?
