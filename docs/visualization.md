# Visualización VRML2 headless

WRL es la extensión habitual de VRML. El driver `VRML2FILE` de Geant4 escribe geometría y trayectorias en un archivo de texto `#VRML V2.0 utf8`; no necesita servidor gráfico.

Cada `visualization.mac` abre explícitamente `VRML2FILE`, dibuja el volumen, activa almacenamiento de trayectorias, acumula eventos y hace `viewer/flush`. El script ejecuta la macro en un temporal, comprueba driver, cabecera y tamaño, selecciona la escena acumulada y la renombra de forma determinista.

Los archivos quedan en:

```text
generated/visualization/ex1a/compton_transmission_10events.wrl
generated/visualization/ex1b/compton_kinematics_10events.wrl
generated/visualization/ex2/muon_mcs_10events.wrl
generated/visualization/ex3/muon_energy_loss_10events.wrl
generated/visualization/ex4/neutron_fission_10events.wrl
```

Un visor VRML externo puede abrirlos; FreeWRL, view3dscene, MeshLab y ParaView son ejemplos, no requisitos. Ninguno se instala dentro del Docker.

Los WRL generados están ignorados por Git. Solo se publican unas pocas imágenes PNG derivadas de simulaciones reales.
