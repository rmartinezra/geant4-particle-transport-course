# syntax=docker/dockerfile:1
ARG DEBIAN_VERSION=bookworm-slim

FROM debian:${DEBIAN_VERSION} AS geant4-builder
ARG GEANT4_VERSION=11.2.2
ARG GEANT4_SOURCE_SHA256=0b0cfce14e9143079c4440d27ee21f889c4c4172ac5ee7586746b940ffcf812a
ARG BUILD_JOBS=2

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates cmake curl g++ make ninja-build libexpat1-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN curl -L --fail --retry 3 \
      -o geant4.tar.gz \
      "https://github.com/Geant4/geant4/archive/refs/tags/v${GEANT4_VERSION}.tar.gz" \
    && echo "${GEANT4_SOURCE_SHA256}  geant4.tar.gz" | sha256sum -c - \
    && tar -xzf geant4.tar.gz \
    && cmake -S "geant4-${GEANT4_VERSION}" -B geant4-build -G Ninja \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/opt/geant4 \
      -DCMAKE_INSTALL_LIBDIR=lib \
      -DGEANT4_BUILD_MULTITHREADED=OFF \
      -DGEANT4_INSTALL_DATA=OFF \
      -DGEANT4_INSTALL_EXAMPLES=OFF \
      -DGEANT4_USE_GDML=OFF \
      -DGEANT4_USE_HDF5=OFF \
      -DGEANT4_USE_FREETYPE=OFF \
      -DGEANT4_USE_OPENGL_X11=OFF \
      -DGEANT4_USE_QT=OFF \
      -DGEANT4_USE_RAYTRACER_X11=OFF \
      -DGEANT4_USE_VTK=OFF \
      -DGEANT4_USE_XM=OFF \
      -DGEANT4_USE_SYSTEM_EXPAT=ON \
      -DGEANT4_USE_SYSTEM_ZLIB=ON \
    && cmake --build geant4-build --parallel "${BUILD_JOBS}" \
    && cmake --install geant4-build \
    && test "$(/opt/geant4/bin/geant4-config --version)" = "${GEANT4_VERSION}" \
    && test -s /opt/geant4/lib/libG4VRML.so \
    && rm -rf geant4.tar.gz "geant4-${GEANT4_VERSION}" geant4-build

# Descarga oficial; el MD5 está fijado por G4DatasetDefinitions.cmake de 11.2.2.
# Solo se conservan las 21 tablas de U-235 realmente usadas por este curso.
ARG G4NDL_VERSION=4.7.1
ARG G4NDL_MD5=54f0ed3995856f02433d42ec96d70bc6
RUN curl -L --fail --retry 3 \
      -o G4NDL.tar.gz \
      "https://geant4-data.web.cern.ch/datasets/G4NDL.${G4NDL_VERSION}.tar.gz" \
    && echo "${G4NDL_MD5}  G4NDL.tar.gz" | md5sum -c - \
    && tar -tzf G4NDL.tar.gz | awk '/\/92_235_Uranium\.z$/' > u235-files.txt \
    && test "$(wc -l < u235-files.txt)" -eq 21 \
    && mkdir -p /opt/g4data \
    && tar -xzf G4NDL.tar.gz -C /opt/g4data -T u235-files.txt \
    && rm -f G4NDL.tar.gz u235-files.txt

# Tabla compacta y obligatoria para la inicialización de G4NuclideTable.
ARG G4ENSDFSTATE_VERSION=2.3
ARG G4ENSDFSTATE_MD5=6f18fce8f217e7aaeaa3711be9b2c7bf
RUN curl -L --fail --retry 3 \
      -o G4ENSDFSTATE.tar.gz \
      "https://geant4-data.web.cern.ch/datasets/G4ENSDFSTATE.${G4ENSDFSTATE_VERSION}.tar.gz" \
    && echo "${G4ENSDFSTATE_MD5}  G4ENSDFSTATE.tar.gz" | md5sum -c - \
    && tar -xzf G4ENSDFSTATE.tar.gz -C /opt/g4data \
    && test -s "/opt/g4data/G4ENSDFSTATE${G4ENSDFSTATE_VERSION}/ENSDFSTATE.dat" \
    && rm -f G4ENSDFSTATE.tar.gz

# Datasets completos que los cinco flujos realmente consultan. Se mantienen
# separados del install de Geant4 para que sus versiones/checksums sean visibles.
ARG G4EMLOW_VERSION=8.5
ARG G4EMLOW_MD5=146d0625d8d39f294056e1618271bc46
ARG G4PHOTONEVAPORATION_VERSION=5.7
ARG G4PHOTONEVAPORATION_MD5=81ff27deb23af4aa225423e6b3a06b39
ARG G4RADIOACTIVEDECAY_VERSION=5.6
ARG G4RADIOACTIVEDECAY_MD5=acc1dbeb87b6b708b2874ced729a3a8f
ARG G4PARTICLEXS_VERSION=4.0
ARG G4PARTICLEXS_MD5=d82a4d171d50f55864e28b6cd6f433c0
RUN curl -L --fail --retry 3 -o G4EMLOW.tar.gz \
      "https://geant4-data.web.cern.ch/datasets/G4EMLOW.${G4EMLOW_VERSION}.tar.gz" \
    && echo "${G4EMLOW_MD5}  G4EMLOW.tar.gz" | md5sum -c - \
    && tar -xzf G4EMLOW.tar.gz -C /opt/g4data \
    && rm -f G4EMLOW.tar.gz \
    && curl -L --fail --retry 3 -o PhotonEvaporation.tar.gz \
      "https://geant4-data.web.cern.ch/datasets/G4PhotonEvaporation.${G4PHOTONEVAPORATION_VERSION}.tar.gz" \
    && echo "${G4PHOTONEVAPORATION_MD5}  PhotonEvaporation.tar.gz" | md5sum -c - \
    && tar -xzf PhotonEvaporation.tar.gz -C /opt/g4data \
    && rm -f PhotonEvaporation.tar.gz \
    && curl -L --fail --retry 3 -o RadioactiveDecay.tar.gz \
      "https://geant4-data.web.cern.ch/datasets/G4RadioactiveDecay.${G4RADIOACTIVEDECAY_VERSION}.tar.gz" \
    && echo "${G4RADIOACTIVEDECAY_MD5}  RadioactiveDecay.tar.gz" | md5sum -c - \
    && tar -xzf RadioactiveDecay.tar.gz -C /opt/g4data \
    && rm -f RadioactiveDecay.tar.gz \
    && curl -L --fail --retry 3 -o G4PARTICLEXS.tar.gz \
      "https://geant4-data.web.cern.ch/datasets/G4PARTICLEXS.${G4PARTICLEXS_VERSION}.tar.gz" \
    && echo "${G4PARTICLEXS_MD5}  G4PARTICLEXS.tar.gz" | md5sum -c - \
    && tar -xzf G4PARTICLEXS.tar.gz -C /opt/g4data \
    && rm -f G4PARTICLEXS.tar.gz

FROM debian:${DEBIAN_VERSION} AS runtime
ARG BUILD_JOBS=2
RUN apt-get update && apt-get install -y --no-install-recommends \
      cmake g++ make ninja-build python3 python3-numpy python3-scipy \
      python3-matplotlib libexpat1 zlib1g \
    && rm -rf /var/lib/apt/lists/* /root/.cache

COPY --from=geant4-builder /opt/geant4 /opt/geant4
COPY --from=geant4-builder /opt/g4data /opt/g4data

ENV PATH="/opt/geant4/bin:${PATH}" \
    LD_LIBRARY_PATH="/opt/geant4/lib" \
    CMAKE_PREFIX_PATH="/opt/geant4" \
    G4LEDATA="/opt/g4data/G4EMLOW8.5" \
    G4LEVELGAMMADATA="/opt/g4data/PhotonEvaporation5.7" \
    G4RADIOACTIVEDATA="/opt/g4data/RadioactiveDecay5.6" \
    G4PARTICLEXSDATA="/opt/g4data/G4PARTICLEXS4.0" \
    G4NEUTRONHPDATA="/opt/g4data/G4NDL4.7.1" \
    G4ENSDFSTATEDATA="/opt/g4data/G4ENSDFSTATE2.3" \
    MPLBACKEND="Agg" \
    PYTHONDONTWRITEBYTECODE="1"

# Prueba de construcción y VRML2FILE durante el build, sin X11/Qt/OpenGL.
COPY . /tmp/course-smoke
RUN cmake -S /tmp/course-smoke/exercises/01_compton/A_cross_section \
      -B /tmp/course-smoke/build -G Ninja \
      -DGeant4_DIR=/opt/geant4/lib/cmake/Geant4 \
      -DWITH_GEANT4_UIVIS=ON -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /tmp/course-smoke/build --parallel "${BUILD_JOBS}" \
    && mkdir /tmp/vrml-test \
    && cd /tmp/vrml-test \
    && ( /tmp/course-smoke/build/TestEm13 \
         /tmp/course-smoke/exercises/01_compton/A_cross_section/macros/visualization.mac \
         > vrml.log 2>&1 || { status=$?; cat vrml.log; exit "${status}"; } ) \
    && test "$(find . -name '*.wrl' -type f -size +0c | wc -l)" -ge 1 \
    && head -n 1 "$(find . -name '*.wrl' -type f -size +0c | head -n 1)" | grep -q '^#VRML V2.0 utf8' \
    && grep -q 'VRML2FILE' vrml.log \
    && rm -rf /tmp/course-smoke /tmp/vrml-test

LABEL org.opencontainers.image.title="Curso de transporte de partículas con Geant4" \
      org.opencontainers.image.description="Cinco módulos docentes reproducibles con Geant4 11.2.2, análisis Python y visualización VRML2FILE" \
      org.opencontainers.image.source="https://github.com/rmartinezra/geant4-particle-transport-course" \
      org.opencontainers.image.url="https://hub.docker.com/r/rmartinezmaple/geant4-particle-transport-course" \
      org.opencontainers.image.version="11.2.2" \
      org.opencontainers.image.licenses="Geant4"

WORKDIR /workspace
CMD ["make", "help"]
