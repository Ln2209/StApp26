# The air I breathe in Île-de-France: is it getting better? (2014 - 2016)

Individual project - Data Storytelling Dashboard with Streamlit (EFREI, 2026).

Author: Hélène Li

Deployed app: http://localhost:8501  

**Audience:** a resident of Île-de-France. **Story arc:** hook → context → analysis (overview, where/when) →
data quality & limitations → key takeaways and next steps.

## Run it (from a clean checkout)

```bash
pip install -r requirements.txt
streamlit run app.py          # or: make install && make run
```

The app reads the small pre-aggregated tables in `data/processed/` (< 1 MB), so it starts immediately.
The department boundaries (`data/departements.geojson`) are included; if missing they are downloaded once
from <https://github.com/gregoiredavid/france-geojson> and cached.

## Data

- **Dataset:** "Indices Qualité de l'air (Citeair) journaliers par polluant sur l'Île-de-France, les départements, les communes franciliennes
  et les arrondissements parisiens" - daily Citeair sub-index of NO₂, PM10 and O₃ per commune, years 2014, 2015, 2016
  (one CSV per year: `indices_QA_commune_IDF_<year>.csv`).
- **Values are index points, not concentrations (µg/m³):** integers from 1 to about 120 on the Citeair scale
  (usually 0-25 very low, 25-50 low, 50-75 medium, 75-100 high, above 100 very high; to confirm in the dataset documentation).
- **Portal:** data.gouv.fr - dataset page: https://www.data.gouv.fr/datasets/indices-qualite-de-lair-citeair-journaliers-par-polluant-sur-lile-de-france-les-departements-les-communes-franciliennes-et-les-arrondissements-parisiens/informations
- **License:** Open Data Commons Open Database License (ODbL) — http://opendatacommons.org/licenses/odbl/summary/ (attribution required; keep the same license for derived databases).
- **Raw files are not bundled** (about 50 MB). To rebuild the processed tables from scratch:
  put the three CSVs in `data/raw/` (or fill the URLs in `data/sources.json`), then run `make data`.
- Processing (`utils/io.py`): quality checks, removal of aggregate rows (INSEE code < 1,000), daily means per département
  (weighted by number of communes), annual means per commune.

## Project structure

```
app.py                 # page setup, sidebar filters, narrative order
sections/              # intro.py, overview.py, deep_dives.py, quality.py, conclusions.py
utils/io.py            # fetch_and_cache(), build_processed(), load_tables()
utils/prep.py          # filters and aggregations
utils/viz.py           # chart functions (one consistent style)
constants.py           # labels, thresholds, colours (no random sampling: fully deterministic)
data/processed/        # pre-aggregated tables + quality report
```

## Features checklist

- Sidebar: pollutant, date range, départements.
- KPI header tied to the filters; 6 interactive Plotly visuals with hover (seasonal lines, daily series with annotated peak,
  choropleth map, small multiples, before/after dumbbell, heatmap, box plot).
- Data quality section: missing values, duplicates, negatives, day coverage, aggregate rows, with documented decisions.
- Performance: `st.cache_data` on loading, filtering and insights; pre-aggregation (1.4 M rows → ~9 k).
- Accessibility: every chart has a text description, axes and units are labelled, colour-blind-safe sequential palettes.

## Limitations

Only 3 years (weather varies); no causal claims; values are sub-index points, so they cannot be compared with legal limits in µg/m³ and averaging indices is a
simplification; commune means are not population-weighted; band limits are visual references only; 1 day (2014-10-20) has no commune data.
