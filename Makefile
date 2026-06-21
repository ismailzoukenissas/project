# ════════════════════════════════════════════════════════════
# Makefile — Performance Opérationnelle des Compagnies Aériennes
# Pipeline complet : CSV bruts → Parquet → dbt → Marts → Dashboards
# ════════════════════════════════════════════════════════════

# ─── Variables ──────────────────────────────────────────────
PYTHON      := venv/Scripts/python
PIP         := venv/Scripts/pip
DBT_DIR     := dbt/airline_dbt
STREAMLIT   := venv/Scripts/streamlit

# ─── Couleurs terminal ──────────────────────────────────────
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m

.DEFAULT_GOAL := help

# ════════════════════════════════════════════════════════════
.PHONY: help
help: ## Affiche cette aide
	@echo "$(YELLOW)Pipeline Performance Aerienne — Commandes disponibles$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ════════════════════════════════════════════════════════════
# SETUP
# ════════════════════════════════════════════════════════════

.PHONY: venv
venv: ## Crée l'environnement virtuel Python
	python -m venv venv
	@echo "$(GREEN)Environnement virtuel créé.$(NC) Active-le avec : venv\Scripts\activate"

.PHONY: install
install: ## Installe toutes les dépendances Python
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dépendances installées.$(NC)"

.PHONY: setup
setup: venv install dbt_init ## Installation complète (venv + deps + dbt)

# ════════════════════════════════════════════════════════════
# PHASE 1 — AUDIT (L2)
# ════════════════════════════════════════════════════════════

.PHONY: audit
audit: ## Audit des schémas multi-annuels (10 CSV)
	@echo "$(YELLOW)[1/8] Audit des schémas...$(NC)"
	$(PYTHON) src/audit_schema.py

# ════════════════════════════════════════════════════════════
# PHASE 2 — CONVERSION CSV → PARQUET (L3)
# ════════════════════════════════════════════════════════════

.PHONY: convert
convert: ## Convertit les 10 CSV en Parquet (ZSTD)
	@echo "$(YELLOW)[2/8] Conversion CSV → Parquet...$(NC)"
	$(PYTHON) src/conversion/csv_to_parquet.py

# ════════════════════════════════════════════════════════════
# PHASE 3 — DBT (L4, L5, L6)
# ════════════════════════════════════════════════════════════

.PHONY: dbt_init
dbt_init: ## Initialise le projet dbt (première fois uniquement)
	cd $(DBT_DIR) && dbt init airline_dbt

.PHONY: dbt_debug
dbt_debug: ## Vérifie la connexion dbt ↔ DuckDB
	cd $(DBT_DIR) && dbt debug

.PHONY: dbt_seed
dbt_seed: ## Charge dim_carrier.csv (L5)
	@echo "$(YELLOW)[3/8] Chargement seed dim_carrier...$(NC)"
	cd $(DBT_DIR) && dbt seed

.PHONY: dbt_run
dbt_run: ## Lance tous les modèles dbt (staging + intermediate + gold)
	@echo "$(YELLOW)[4/8] Exécution des modèles dbt...$(NC)"
	cd $(DBT_DIR) && dbt run

.PHONY: dbt_run_ax3
dbt_run_ax3: ## Lance uniquement le mart AX3
	cd $(DBT_DIR) && dbt run --select mart_merger_impact

.PHONY: dbt_run_ax4
dbt_run_ax4: ## Lance uniquement les marts AX4
	cd $(DBT_DIR) && dbt run --select mart_otp_monthly mart_seasonality

.PHONY: dbt_test
dbt_test: ## Lance les tests dbt
	@echo "$(YELLOW)[5/8] Tests dbt...$(NC)"
	cd $(DBT_DIR) && dbt test

.PHONY: dbt_docs
dbt_docs: ## Génère et ouvre la documentation dbt (lineage)
	cd $(DBT_DIR) && dbt docs generate && dbt docs serve

# ════════════════════════════════════════════════════════════
# PHASE 4 — EXPORT GOLD (pour notebooks / dashboards)
# ════════════════════════════════════════════════════════════

.PHONY: export_gold
export_gold: ## Exporte les marts dbt en fichiers Parquet
	@echo "$(YELLOW)[6/8] Export des marts Gold...$(NC)"
	$(PYTHON) src/export_gold.py

.PHONY: export_tableau
export_tableau: ## Exporte les marts en CSV pour Tableau
	$(PYTHON) src/export_csv_tableau.py

# ════════════════════════════════════════════════════════════
# PHASE 5 — PROFILING & DOCUMENTATION (L1, L7)
# ════════════════════════════════════════════════════════════

.PHONY: profiling
profiling: ## Génère le rapport de profiling sur 2015 (L1)
	@echo "$(YELLOW)[7/8] Génération rapport profiling 2015...$(NC)"
	$(PYTHON) src/profiling_2015.py

.PHONY: dictionnaire
dictionnaire: ## Génère le dictionnaire de données (L7)
	@echo "$(YELLOW)[8/8] Génération dictionnaire de données...$(NC)"
	$(PYTHON) src/generate_dictionnaire.py

# ════════════════════════════════════════════════════════════
# PHASE 6 — DASHBOARDS (L9)
# ════════════════════════════════════════════════════════════

.PHONY: dashboard
dashboard: ## Lance le dashboard Streamlit
	$(STREAMLIT) run dashboard/streamlit_app/app.py

.PHONY: notebooks
notebooks: ## Lance Jupyter Lab pour les notebooks EDA
	venv/Scripts/jupyter lab notebooks/

# ════════════════════════════════════════════════════════════
# PIPELINE COMPLET
# ════════════════════════════════════════════════════════════

.PHONY: run
run: audit convert dbt_seed dbt_run dbt_test export_gold export_tableau profiling dictionnaire ## Lance le pipeline complet de bout en bout
	@echo ""
	@echo "$(GREEN)═══════════════════════════════════════════$(NC)"
	@echo "$(GREEN)✅  Pipeline complet terminé avec succès !$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════$(NC)"
	@echo ""
	@echo "Prochaines étapes :"
	@echo "  make dashboard   → lancer le dashboard Streamlit"
	@echo "  make notebooks   → ouvrir les notebooks Jupyter"

.PHONY: run_ax3
run_ax3: audit convert dbt_seed dbt_run_ax3 export_gold ## Pipeline limité à l'AX3 (fusions)

.PHONY: run_ax4
run_ax4: audit convert dbt_seed dbt_run_ax4 export_gold ## Pipeline limité à l'AX4 (saisonnalité)

# ════════════════════════════════════════════════════════════
# UTILITAIRES
# ════════════════════════════════════════════════════════════

.PHONY: clean
clean: ## Supprime les fichiers générés (Parquet, DuckDB, target dbt)
	rm -rf data/parquet/*.parquet
	rm -rf data/gold/*.parquet
	rm -rf data/airline.duckdb
	rm -rf $(DBT_DIR)/target
	rm -rf $(DBT_DIR)/logs
	@echo "$(GREEN)Fichiers générés supprimés.$(NC)"

.PHONY: clean_all
clean_all: clean ## Supprime aussi l'environnement virtuel
	rm -rf venv
	@echo "$(GREEN)Environnement virtuel supprimé.$(NC)"

.PHONY: status
status: ## Affiche l'état des fichiers du pipeline
	@echo "$(YELLOW)CSV bruts        :$(NC)" $$(ls data/raw/*.csv 2>/dev/null | wc -l) "/ 10"
	@echo "$(YELLOW)Parquet annuels  :$(NC)" $$(ls data/parquet/*.parquet 2>/dev/null | wc -l) "/ 10"
	@echo "$(YELLOW)Marts Gold       :$(NC)" $$(ls data/gold/*.parquet 2>/dev/null | wc -l) "/ 3"
	@echo "$(YELLOW)Base DuckDB      :$(NC)" $$(test -f data/airline.duckdb && echo "✅ présente" || echo "❌ absente")

.PHONY: freeze
freeze: ## Sauvegarde les dépendances dans requirements.txt
	$(PIP) freeze > requirements.txt
	@echo "$(GREEN)requirements.txt mis à jour.$(NC)"
