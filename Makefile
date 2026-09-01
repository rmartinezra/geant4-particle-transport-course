SHELL := /bin/bash
.DEFAULT_GOAL := help

VIS ?= 1
VIS_EVENTS ?= 10
VIS_SEED ?= 10101
SEED ?= 12345
FAST ?= 0
FULL ?= 0
JOBS ?= 2

ifeq ($(FULL),1)
  EVENTS_EX1A := 100000
  EVENTS_EX1B := 200000
  EVENTS_EX2 := 100000
  EVENTS_EX3 := 100000
  EVENTS_EX4 := 100000
else ifeq ($(FAST),1)
  EVENTS_EX1A := 3000
  EVENTS_EX1B := 3000
  EVENTS_EX2 := 300
  EVENTS_EX3 := 300
  EVENTS_EX4 := 3000
else
  EVENTS_EX1A := 10000
  EVENTS_EX1B := 10000
  EVENTS_EX2 := 2000
  EVENTS_EX3 := 2000
  EVENTS_EX4 := 10000
endif

.PHONY: help env-check class01-help class02-help prepare-class02 run-class02 validate-class02 analyze-class02 \
	build test all clean clean-generated check-repo \
 run-ex1a analyze-ex1a visualize-ex1a run-ex1b analyze-ex1b visualize-ex1b \
 run-ex2 analyze-ex2 visualize-ex2 run-ex3 analyze-ex3 visualize-ex3 \
 run-ex4 analyze-ex4 visualize-ex4 visualize-all

help:
	@echo "Curso Geant4 11.2.2"
	@echo "  make env-check    # preparación técnica de Clase 1; no ejecuta resultados"
	@echo "  make class01-help # ruta breve de trabajo para Clase 1"
	@echo "  make class02-help # producción FULL y análisis de Clase 2"
	@echo "  make run-class02  # genera 1A/1B FULL y ejecuta sus análisis"
	@echo "  make build | test | all | check-repo"
	@echo "  make run-ex1a ... run-ex4 [FAST=1|FULL=1] [VIS=0] [SEED=N]"
	@echo "  make analyze-ex1a ... analyze-ex4"
	@echo "  make visualize-ex1a ... visualize-ex4 [VIS_EVENTS>=10] [VIS_SEED=N]"

env-check:
	@BUILD_JOBS=$(JOBS) bash ./scripts/env_check.sh

class01-help:
	@echo "Antes de la clase:"
	@echo "  make env-check"
	@echo
	@echo "Práctica guiada 1A:"
	@echo "  make run-ex1a FAST=1"
	@echo
	@echo "Práctica guiada 1B:"
	@echo "  make run-ex1b FAST=1"
	@echo
	@echo "Salidas:"
	@echo "  generated/data/"
	@echo "  generated/logs/"
	@echo "  generated/visualization/"

class02-help:
	@echo "La Clase 2 usa una producción FULL nueva, sin repetir los WRL:"
	@echo "  Ex1A: 100000 eventos por cada uno de los seis espesores"
	@echo "  Ex1B: 200000 primeras interacciones Compton"
	@echo
	@echo "Producción y análisis completos:"
	@echo "  make run-class02 [SEED=N]"
	@echo
	@echo "Para separar las etapas:"
	@echo "  make prepare-class02 [SEED=N]"
	@echo "  make analyze-class02"
	@echo
	@echo "AVISO: prepare-class02 reemplaza los CSV FAST de 1A y 1B."
	@echo
	@echo "Salidas:"
	@echo "  generated/figures/ex1a/  generated/fits/ex1a/"
	@echo "  generated/figures/ex1b/  generated/fits/ex1b/"

build:
	@BUILD_JOBS=$(JOBS) bash ./scripts/build_all.sh

define maybe_vis
	@if [[ "$(VIS)" == "1" ]]; then \
	  echo "[VIS] Generando visualización VRML de $(VIS_EVENTS) eventos..."; \
	  $(MAKE) --no-print-directory visualize-$(1); \
	else echo "[VIS] Desactivada explícitamente (VIS=0)."; fi
endef

visualize-ex1a: build
	@python3 scripts/run_visualization.py ex1a --events $(VIS_EVENTS) --seed $(VIS_SEED)
visualize-ex1b: build
	@python3 scripts/run_visualization.py ex1b --events $(VIS_EVENTS) --seed $$(( $(VIS_SEED) + 100 ))
visualize-ex2: build
	@python3 scripts/run_visualization.py ex2 --events $(VIS_EVENTS) --seed $$(( $(VIS_SEED) + 200 ))
visualize-ex3: build
	@python3 scripts/run_visualization.py ex3 --events $(VIS_EVENTS) --seed $$(( $(VIS_SEED) + 300 ))
visualize-ex4: build
	@python3 scripts/run_visualization.py ex4 --events $(VIS_EVENTS) --seed $$(( $(VIS_SEED) + 400 ))

visualize-all: visualize-ex1a visualize-ex1b visualize-ex2 visualize-ex3 visualize-ex4

run-ex1a: build
	$(call maybe_vis,ex1a)
	@echo "[MC] Ex1A: $(EVENTS_EX1A) eventos por espesor"
	@python3 exercises/01_compton/A_cross_section/scripts/run_scan.py \
	  --executable build/ex1a/TestEm13 --events $(EVENTS_EX1A) --seed $(SEED) \
	  --output generated/data/ex1a/transmission_scan.csv --logs-dir generated/logs/ex1a --force

analyze-ex1a:
	@python3 exercises/01_compton/A_cross_section/analysis/analyze_transmission.py \
	  --input generated/data/ex1a/transmission_scan.csv \
	  --summary generated/fits/ex1a/summary_A.txt --figure-dir generated/figures/ex1a

run-ex1b: build
	$(call maybe_vis,ex1b)
	@echo "[MC] Ex1B: $(EVENTS_EX1B) eventos"
	@python3 exercises/01_compton/B_kinematics/scripts/run_compton.py \
	  --executable build/ex1b/TestEm14 --events $(EVENTS_EX1B) --seed $(SEED) \
	  --output generated/data/ex1b/compton_events.csv --logs-dir generated/logs/ex1b --force

analyze-ex1b:
	@python3 exercises/01_compton/B_kinematics/analysis/analyze_compton.py \
	  --input generated/data/ex1b/compton_events.csv \
	  --summary generated/fits/ex1b/summary_B.txt --figure-dir generated/figures/ex1b

prepare-class02: build
	@echo "[CLASS02] Producción FULL: Ex1A=100000 eventos/espesor; Ex1B=200000 eventos."
	@echo "[CLASS02] Se reemplazarán los CSV FAST existentes; los WRL no se regeneran."
	@echo "[MC] Ex1A FULL: 100000 eventos por espesor"
	@python3 exercises/01_compton/A_cross_section/scripts/run_scan.py \
	  --executable build/ex1a/TestEm13 --events 100000 --seed $(SEED) \
	  --output generated/data/ex1a/transmission_scan.csv \
	  --logs-dir generated/logs/ex1a --force
	@echo "[MC] Ex1B FULL: 200000 eventos"
	@python3 exercises/01_compton/B_kinematics/scripts/run_compton.py \
	  --executable build/ex1b/TestEm14 --events 200000 \
	  --seed $$(( $(SEED) + 1000 )) \
	  --output generated/data/ex1b/compton_events.csv \
	  --logs-dir generated/logs/ex1b --force

validate-class02:
	@python3 scripts/validate_class02_inputs.py

analyze-class02: validate-class02
	@$(MAKE) --no-print-directory analyze-ex1a
	@$(MAKE) --no-print-directory analyze-ex1b

run-class02: prepare-class02
	@$(MAKE) --no-print-directory analyze-class02
	@echo "[CLASS02] Producción FULL y análisis terminados."

run-ex2: build
	$(call maybe_vis,ex2)
	@echo "[MC] Ex2: $(EVENTS_EX2) eventos por configuración"
	@python3 exercises/02_multiple_scattering/scripts/run_mcs.py \
	  --executable build/ex2/TestEm5 --events $(EVENTS_EX2) --seed $(SEED) --jobs $(JOBS) \
	  --output-dir generated/data/ex2 --logs-dir generated/logs/ex2 --force

analyze-ex2:
	@python3 exercises/02_multiple_scattering/analysis/analyze_mcs.py \
	  --data-dir generated/data/ex2 --figures-dir generated/figures/ex2 \
	  --summary generated/fits/ex2/summary_mcs.txt

run-ex3: build
	$(call maybe_vis,ex3)
	@echo "[MC] Ex3: $(EVENTS_EX3) eventos por configuración"
	@python3 exercises/03_energy_loss/scripts/run_energy_loss.py \
	  --executable build/ex3/TestEm18 --events $(EVENTS_EX3) --seed $(SEED) --jobs $(JOBS) \
	  --output-dir generated/data/ex3 --logs-dir generated/logs/ex3 --force

analyze-ex3:
	@python3 exercises/03_energy_loss/analysis/analyze_energy_loss.py \
	  --data-dir generated/data/ex3 --figures-dir generated/figures/ex3 \
	  --summary generated/fits/ex3/summary_energy_loss.txt

run-ex4: build
	$(call maybe_vis,ex4)
	@echo "[MC] Ex4: $(EVENTS_EX4) neutrones sobre U-235"
	@python3 exercises/04_nuclear_cross_section/scripts/run_hadronic.py \
	  --executable build/ex4/Hadr03 --events $(EVENTS_EX4) --seed $(SEED) \
	  --output-dir generated/data/ex4 --logs-dir generated/logs/ex4 --force

analyze-ex4:
	@python3 exercises/04_nuclear_cross_section/analysis/analyze_hadronic.py \
	  --data-dir generated/data/ex4 --figures-dir generated/figures/ex4 \
	  --summary generated/fits/ex4/summary_hadronic.txt

all: run-ex1a analyze-ex1a run-ex1b analyze-ex1b run-ex2 analyze-ex2 run-ex3 analyze-ex3 run-ex4 analyze-ex4

test:
	@bash ./scripts/test_all.sh

check-repo:
	@python3 scripts/check_repo_clean.py

clean-generated:
	@bash ./scripts/clean_generated.sh

clean: clean-generated
	@if [[ -d build ]]; then find build -mindepth 1 -delete; fi
