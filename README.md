# Performance Opérationnelle des Compagnies Aériennes Américaines (2009-2018)

Projet de Data Visualisation — Analyse de 65 millions de vols domestiques américains sur 10 ans.

**Responsabilité de cette équipe :**
- **AX3** — Impact des Fusions et de la Consolidation Sectorielle
- **AX4** — Saisonnalité, Cycles Économiques et Patterns de Ponctualité Long Terme



##  Contexte du projet

La décennie 2009-2018 est la plus transformatrice de l'histoire récente de l'aviation civile américaine — crise financière de 2008, vague de méga-fusions (United+Continental, Southwest+AirTran, American+US Airways), chute du prix du kérosène, puis saturation croissante des grands hubs.

Ce projet construit un observatoire comparatif de la performance opérationnelle (OTP) des compagnies aériennes américaines, basé sur le dataset **Airline Delay and Cancellation Data 2009-2018** (source BTS/DOT, ~68 millions de vols).



##  Structure du projet


airline_performance/
│
├── data/
│   ├── raw/                     # 10 fichiers CSV bruts (2009.csv → 2018.csv)
│   ├── parquet/                 # 10 fichiers Parquet compressés (ZSTD)
│   ├── gold/                    # 3 marts agrégés exportés en Parquet
│   └── airline.duckdb           # Base DuckDB locale (dbt)
│
├── src/
│   ├── audit_schema.py          # Audit des schémas multi-annuels (L2)
│   ├── conversion/
│   │   └── csv_to_parquet.py    # Conversion CSV → Parquet (L3)
│   ├── export_gold.py           # Export des marts dbt en Parquet
│   ├── export_csv_tableau.py    # Export CSV pour Tableau
│   ├── profiling_2015.py        # Rapport de profiling 2015 (L1)
│   └── generate_dictionnaire.py # Génération du dictionnaire de données (L7)
│
├── dbt/
│   └── airline_dbt/
│       ├── seeds/
│       │   └── dim_carrier.csv          # Référentiel carriers + fusions (L5)
│       ├── models/
│       │   ├── staging/
│       │   │   └── stg_flights.sql      # Couche Silver (L4)
│       │   ├── intermediate/
│       │   │   └── int_flights_enriched.sql
│       │   └── gold/
│       │       ├── mart_merger_impact.sql     # AX3
│       │       ├── mart_otp_monthly.sql       # AX4
│       │       └── mart_seasonality.sql       # AX4
│       ├── dbt_project.yml
│       └── tests/
│           └── schema_gold.yml
│
├── notebooks/
│   ├── 03_ax3_fusions.ipynb         # 6 visualisations AX3 (L8)
│   └── 04_ax4_saisonnalite.ipynb    # 7 visualisations AX4 (L8)
│
├── dashboard/
│   ├── tableau_data/                # CSV exportés pour Tableau
│   ├── airline_performance.twb      # Classeur Tableau (L9)
│   └── streamlit_app/
│       ├── app.py                            # Page d'accueil
│       └── pages/
│           ├── 1_AX3_Fusions.py              # Dashboard AX3 interactif
│           ├── 2_AX4_Saisonnalite.py         # Dashboard AX4 interactif
│           └── 3_AX4_Questions_Metier.py     # Q&A métier avec graphiques
│
├── rapport/
│   ├── profiling_2015.html          # Rapport ydata-profiling (L1)
│   ├── dictionnaire_donnees.md      # Dictionnaire de données (L7)
│   ├── rapport_recommandations.tex  # Source LaTeX du rapport (L10)
│   ├── rapport_recommandations.pdf  # Rapport final 13 pages (L10)
│   └── images/                      # Captures Tableau intégrées au rapport
│
├── DECISIONS.md                     # Décisions techniques issues de l'audit
├── requirements.txt                 # Dépendances Python
├── Makefile                         # Pipeline automatisé
└── README.md                        # Ce fichier




## Stack technique

| Catégorie | Outil | Rôle |
|---|---|---|
| Langage | Python 3.10+ | Orchestration du pipeline |
| Traitement | DuckDB | Requêtes SQL sur 65M de lignes |
| Format | Parquet (ZSTD) | Stockage compressé columnar |
| Transformation | dbt-core + dbt-duckdb | 4 modèles Gold/Silver |
| Profiling | ydata-profiling | Rapport qualité données |
| Analyse | Jupyter + Plotly | Notebooks EDA interactifs |
| Décomposition temporelle | statsmodels (STL) | Tendance/saisonnalité/résidu |
| Dashboard | Tableau Desktop | 9 feuilles, 2 dashboards |
| Dashboard web | Streamlit | Dashboard interactif navigateur |
| Rapport | LaTeX (Overleaf) | Rapport PDF 13 pages |

---

##  Installation

### 1. Créer l'environnement virtuel

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
```

### 2. Installer les dépendances


pip install -r requirements.txt


### 3. Placer les données brutes

Télécharger le dataset Kaggle et placer les 10 fichiers CSV (`2009.csv` à `2018.csv`) dans `data/raw/`.



##  Pipeline complet

Lancer tout le pipeline en une seule commande :


make run


Ou étape par étape :
bash
make audit       # Audit des schémas (L2)
make convert      # CSV → Parquet (L3)
make dbt_seed      # Charger dim_carrier (L5)
make dbt_run       # Lancer les modèles dbt (L4, L6)
make dbt_test      # Tester les modèles dbt
make export_gold   # Exporter les marts en Parquet
make profiling     # Rapport profiling 2015 (L1)
make dictionnaire   # Dictionnaire de données (L7)
make dashboard      # Lancer le dashboard Streamlit


##  Les 4 axes du projet

| Axe | Description | Responsable |
|---|---|---|
| AX1 | Benchmarking OTP et ranking des compagnies sur 10 ans | Autre équipe |
| AX2 | Décomposition des 7 causes de retard par transporteur | Autre équipe |
| **AX3** | **Impact des fusions et de la consolidation sectorielle** | **Notre équipe** |
| **AX4** | **Saisonnalité, cycles économiques et patterns long terme** | **Notre équipe** |

---

## AX3 — Impact des Fusions sur la Performance

### Fusions analysées

| Fusion | Date | Codes | Intégration |
|---|---|---|---|
| United + Continental | Oct. 2010 | UA + CO → UA | 2010-2013 |
| Southwest + AirTran | Mai 2011 | WN + FL → WN | 2011-2015 |
| American + US Airways | Déc. 2013 | AA + US → AA | 2013-2015 |

### Visualisations produites

1. **OTP Timeline Fusions** — évolution annuelle de l'OTP par carrier avec annotations des dates de fusion
2. **OTP Pre During Post** — comparaison de l'OTP moyen avant/pendant/après chaque fusion
3. **Carriers Actifs par Année** — réduction du nombre de carriers fusionnés actifs (5→3)
4. **Effet Domino (LATE_AIRCRAFT)** — évolution de la part des retards en cascade par carrier

### Insights clés

- Les fusions causent une dégradation transitoire de l'OTP limitée à 2-3 points
- Southwest maintient structurellement le plus fort taux d'effet domino (~50-55%) en raison de son réseau point-to-point dense
- Le marché s'est consolidé de 5-6 carriers indépendants à 3 grands groupes entre 2009 et 2016



## AX4 — Saisonnalité, Cycles et Patterns Temporels

### Visualisations produites

1. **Heatmap OTP Année × Mois** — calendrier de ponctualité sur 10 ans
2. **OTP par heure de départ** — pattern horaire 0h-23h
3. **OTP par jour de la semaine** — pattern hebdomadaire
4. **Saisonnalité Weather vs NAS** — comparaison des causes par mois
5. **Tendance long terme** — régression linéaire OTP 2009-2018
6. **Page Questions Métier** — 6 questions business avec réponse chiffrée et graphique dédié

### Insights clés

- Les vols entre 5h et 6h du matin ont un OTP de ~92% contre ~75% pour les vols entre 17h et 20h
- Le Samedi est structurellement le meilleur jour (~84%), le Jeudi/Vendredi les pires (~80%)
- Le NAS (saturation ATC) domine toute l'année, avec un pic en Octobre
- Le Weather (météo extrême) pic en Janvier-Février
- La saisonnalité est stable sur 10 ans, indépendamment du contexte économique ou des fusions

---

## Livrables produits

| Réf. | Livrable | Format | Statut |
|---|---|---|---|
| L1 | Rapport de profiling 2015 | HTML
| L2 | Audit schémas multi-annuels | DECISIONS.md 
| L3 | Scripts conversion CSV → Parquet | Python 
| L4 | Scripts nettoyage Silver | dbt SQL 
| L5 | dim_carrier avec gestion des fusions | seed dbt 
| L6 | Projet dbt Gold complet | dbt 
| L7 | Dictionnaire de données | Markdown 
| L8 | Notebooks EDA (AX3 + AX4) | Jupyter
| L9 | Dashboard Observatoire | Tableau + Streamlit
| L10 | Rapport d'analyse et recommandations | PDF (LaTeX) 
| L11 | Dépôt Git structuré + Makefile | Git 
| L12 | Présentation orale + démo live | PowerPoint 


##  Synthèse des 6 recommandations

| # | Recommandation | Axe | Impact estimé |
|---|---|---|---|
| R1 | Buffer opérationnel pendant les fusions | AX3 | -0.8 pts dégradation |
| R2 | Réduction de l'effet domino (Southwest) | AX3 | +2 pts OTP |
| R3 | Dashboard de surveillance post-fusion | AX3 | Détection -4 semaines |
| R4 | Optimisation des créneaux de départ | AX4 | +3-4 pts OTP |
| R5 | Plans de contingence météo hivernaux | AX4 | -25% annulations météo |
| R6 | Lissage de la demande hebdomadaire | AX4 | +1-2 pts OTP Jeudi |

**Impact total estimé : +5 à +7 points d'OTP global sur un horizon de 24 mois.**

---

##  Lancer le dashboard Streamlit


streamlit run dashboard/streamlit_app/app.py


Le dashboard s'ouvre automatiquement avec 3 pages :
-  Accueil
-  AX3 — Fusions
- AX4 — Saisonnalité
-  AX4 — Questions Métier



##  Source des données

**Airline Delay and Cancellation Data, 2009-2018**
Source : Bureau of Transportation Statistics (BTS) / Department of Transportation (DOT)
Dataset Kaggle : [kaggle.com/datasets/yuanyuwendymu/airline-delay-and-cancellation-data-2009-2018](https://www.kaggle.com/datasets/yuanyuwendymu/airline-delay-and-cancellation-data-2009-2018)



## 👥 Équipe

Projet réalisé dans le cadre du **Projet 3 — Data Visualisation**, responsable des axes AX3 et AX4.
