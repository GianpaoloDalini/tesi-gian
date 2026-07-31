# ============================================================================
#  Comandi standard del progetto. Eseguire dalla radice del repository.
# ============================================================================
.PHONY: help thesis watch clean install lint test figures freeze

help:  ## Elenca i comandi disponibili
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	 awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

thesis:  ## Compila la tesi in PDF (thesis/build/main.pdf)
	cd thesis && latexmk -pdf -interaction=nonstopmode main.tex

watch:  ## Ricompila automaticamente a ogni salvataggio
	cd thesis && latexmk -pdf -pvc -interaction=nonstopmode main.tex

clean:  ## Rimuove gli artefatti di compilazione LaTeX
	cd thesis && latexmk -C

install:  ## Installa il package Python in editable mode
	pip install -e ".[dev]"

lint:  ## Controlla e formatta il codice Python
	ruff check --fix src tests
	ruff format src tests

test:  ## Esegue i test
	pytest -q

figures:  ## Rigenera le figure della tesi dai risultati sperimentali
	python -m tesi_gan.cli export-figures

freeze:  ## Blocca le versioni esatte delle dipendenze (per i run remoti)
	pip freeze > requirements-lock.txt
