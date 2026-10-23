"""Data loading, cached download and pre-aggregation."""
import glob, json, os, re, sys
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")
SOURCES = os.path.join(ROOT, "data", "sources.json")
GEOJSON = os.path.join(ROOT, "data", "departements.geojson")
GEO_URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
VAL = ["no2", "pm10", "o3"]
TABLES = ["dep_daily", "commune_year", "agg_year"]


def fetch_and_cache():
    """Download the yearly CSV files listed in data/sources.json (if missing). See README."""
    import requests
    os.makedirs(RAW, exist_ok=True)
    with open(SOURCES) as f:
        urls = json.load(f).get("raw_files", {})
    for name, url in urls.items():
        dest = os.path.join(RAW, name)
        if not os.path.exists(dest) and url:
            r = requests.get(url, timeout=120); r.raise_for_status()
            with open(dest, "wb") as out: out.write(r.content)


def _read_raw():
    files = sorted(glob.glob(os.path.join(RAW, "*IDF_20[0-9][0-9].csv")))
    if not files:
        fetch_and_cache()
        files = sorted(glob.glob(os.path.join(RAW, "*IDF_20[0-9][0-9].csv")))
    if not files:
        raise FileNotFoundError("No raw CSV in data/raw/: see the README (Data section).")
    parts = []
    for f in files:
        d = pd.read_csv(f); d["annee"] = int(re.search(r"(20\d\d)\.csv$", f).group(1)); parts.append(d)
    d = pd.concat(parts, ignore_index=True)
    d["date"] = pd.to_datetime(d["date"], format="%d/%m/%Y")
    return d


def build_processed():
    """Quality checks + pre-aggregation (raw is ~50 MB, processed < 1 MB)."""
    raw = _read_raw()
    os.makedirs(PROC, exist_ok=True)
    is_agg = raw.ninsee < 1000
    quality = {
        "n_lignes": int(len(raw)), "n_manquants": int(raw[VAL].isna().sum().sum()),
        "n_doublons": int(raw.duplicated(["date", "ninsee"]).sum()),
        "n_agreges": int(is_agg.sum()), "n_negatifs": int((raw[VAL] < 0).sum().sum()),
        "n_communes": int(raw.loc[~is_agg, "ninsee"].nunique()),
        "n_jours": int(raw.loc[~is_agg, "date"].nunique()),  # days with at least one commune
        "n_jours_attendus": int(len(pd.date_range(raw.date.min(), raw.date.max()))),
        "jours_manquants": [str(x.date()) for x in sorted(set(pd.date_range(raw.date.min(), raw.date.max())) - set(raw.loc[~is_agg, "date"].unique()))],
        "jours_par_annee": {int(k): int(v) for k, v in raw[~is_agg].groupby("annee").date.nunique().items()},
        "date_min": str(raw.date.min().date()), "date_max": str(raw.date.max().date()),
        "min": {c: int(raw.loc[~is_agg, c].min()) for c in VAL}, "max": {c: int(raw.loc[~is_agg, c].max()) for c in VAL},  # communes only
        "communes_par_annee": {int(k): int(v) for k, v in raw[~is_agg].groupby("annee").ninsee.nunique().items()},
    }
    with open(os.path.join(PROC, "quality.json"), "w") as f: json.dump(quality, f, indent=1)
    com = raw[~is_agg].copy()
    com["dep"] = (com.ninsee // 1000).astype(int)
    g = com.groupby(["date", "dep"])
    dd = g[VAL].mean().round(2).join(g.size().rename("n_communes")).reset_index()
    dd["pm10_part_communes_gt50"] = (com.assign(x=com.pm10 > 50).groupby(["date", "dep"]).x.mean().values).round(4)
    dd.to_csv(os.path.join(PROC, "dep_daily.csv.gz"), index=False)
    cy = com.groupby(["ninsee", "dep", "annee"])[VAL].mean().round(2).reset_index()
    cy.to_csv(os.path.join(PROC, "commune_year.csv.gz"), index=False)
    ay = raw[is_agg].groupby(["ninsee", "annee"])[VAL].mean().round(2).reset_index()
    ay.to_csv(os.path.join(PROC, "agg_year.csv.gz"), index=False)


def load_tables():
    if not all(os.path.exists(os.path.join(PROC, f"{t}.csv.gz")) for t in TABLES):
        build_processed()
    dd = pd.read_csv(os.path.join(PROC, "dep_daily.csv.gz"), parse_dates=["date"])
    cy = pd.read_csv(os.path.join(PROC, "commune_year.csv.gz"))
    ay = pd.read_csv(os.path.join(PROC, "agg_year.csv.gz"))
    with open(os.path.join(PROC, "quality.json")) as f: q = json.load(f)
    return dd, cy, ay, q


def get_geojson():
    if not os.path.exists(GEOJSON):
        import requests
        r = requests.get(GEO_URL, timeout=60); r.raise_for_status()
        with open(GEOJSON, "w") as f: f.write(r.text)
    with open(GEOJSON) as f: return json.load(f)


if __name__ == "__main__":
    if "--build" in sys.argv: build_processed(); print("OK: tables written to data/processed/")
    else: fetch_and_cache(); print("OK: raw CSV files downloaded to data/raw/")
