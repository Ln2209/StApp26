"""Light cleaning, filters and aggregations (all pure functions, cache-friendly)."""
import numpy as np
import pandas as pd
from constants import DEP_NAMES, DEP_ZONE


def add_labels(df):
    df = df.copy()
    df["departement"] = df["dep"].map(DEP_NAMES)
    df["zone"] = df["dep"].map(DEP_ZONE)
    return df


def wmean(df, col):
    """Mean weighted by number of communes (= simple mean over communes)."""
    return float(np.average(df[col], weights=df["n_communes"])) if len(df) else float("nan")


def filter_daily(dd, deps, start, end):
    m = dd.dep.isin(deps) & (dd.date >= pd.Timestamp(start)) & (dd.date <= pd.Timestamp(end))
    return dd[m]


def region_daily(dd, pol):
    g = dd.assign(w=dd[pol] * dd.n_communes).groupby("date")
    out = (g.w.sum() / g.n_communes.sum()).rename(pol).reset_index()
    out["rolling_7d"] = out[pol].rolling(7, center=True, min_periods=4).mean()
    return out


def monthly(dd, pol):
    d = dd.assign(w=dd[pol] * dd.n_communes, annee=dd.date.dt.year, mois=dd.date.dt.month)
    g = d.groupby(["annee", "mois"])
    return (g.w.sum() / g.n_communes.sum()).rename(pol).reset_index()


def dep_year(dd, pol):
    d = dd.assign(w=dd[pol] * dd.n_communes, annee=dd.date.dt.year)
    g = d.groupby(["dep", "annee"])
    out = (g.w.sum() / g.n_communes.sum()).rename(pol).reset_index()
    return add_labels(out)


def dep_mean(dd, pol):
    d = dd.assign(w=dd[pol] * dd.n_communes)
    g = d.groupby("dep")
    return add_labels((g.w.sum() / g.n_communes.sum()).rename(pol).reset_index())


def dep_month(dd, pol):
    d = dd.assign(w=dd[pol] * dd.n_communes, mois=dd.date.dt.month)
    g = d.groupby(["dep", "mois"])
    return add_labels((g.w.sum() / g.n_communes.sum()).rename(pol).reset_index())


def kpis(dd, pol):
    """KPIs tied to the sidebar filters."""
    if dd.empty:
        return None
    reg = region_daily(dd, pol)
    ym = (dd.assign(annee=dd.date.dt.year, w=dd[pol] * dd.n_communes)
            .groupby("annee").apply(lambda g: g.w.sum() / g.n_communes.sum(), include_groups=False))
    full = [y for y in ym.index if dd[dd.date.dt.year == y].date.nunique() >= 300]
    delta = None
    if len(full) >= 2:
        delta = (ym[full[-1]] - ym[full[0]], (ym[full[-1]] / ym[full[0]] - 1) * 100, full[0], full[-1])
    top = dep_mean(dd, pol).sort_values(pol).iloc[-1]
    return {"mean": wmean(dd, pol), "reg": reg, "delta": delta, "top": top, "ndays": reg.shape[0]}


def change_table(cy, pol, deps, y0, y1):
    c = cy[cy.dep.isin(deps)]
    a = c[c.annee == y0].groupby("dep")[pol].mean(); b = c[c.annee == y1].groupby("dep")[pol].mean()
    out = pd.DataFrame({"debut": a, "fin": b}).reset_index()
    out["delta_pct"] = (out.fin / out.debut - 1) * 100
    return add_labels(out)


def num(x, d=1):
    """Format a number with d decimals."""
    return f"{x:.{d}f}"
