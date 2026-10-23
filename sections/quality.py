import pandas as pd
import streamlit as st
from utils import prep


def render(ctx):
    q, ay, cy = ctx["q"], ctx["ay"], ctx["cy"]
    st.header("3. Data quality and limitations")
    st.markdown("**The data look clean on paper, but a few precautions are needed before drawing conclusions.**")
    stable = len(set(q["communes_par_annee"].values())) == 1
    checks = pd.DataFrame([
        ("Missing values", str(q["n_manquants"]), "OK" if q["n_manquants"] == 0 else "To handle"),
        ("Duplicates (date × INSEE code)", str(q["n_doublons"]), "OK" if q["n_doublons"] == 0 else "To handle"),
        ("Negative values", str(q["n_negatifs"]), "OK" if q["n_negatifs"] == 0 else "To handle"),
        ("Days with commune data / expected days", f"{q['n_jours']} / {q['n_jours_attendus']}",
         "OK" if not q["jours_manquants"] else "1 day missing, left as is"),
        ("Communes present every year", f"{q['n_communes']} (stable: {'yes' if stable else 'no'})", "OK"),
        ("“Aggregate” rows (INSEE code < 1,000: region, départements)", str(q["n_agreges"]), "Excluded from the analysis"),
    ], columns=["Check", "Result", "Status"])
    st.dataframe(checks, hide_index=True, width="stretch")
    if q["jours_manquants"]:
        jm = ", ".join(pd.Timestamp(x).strftime("%d %b %Y") for x in q["jours_manquants"])
        st.caption(f"Day with no commune at all: {jm} (the file only contains the aggregate rows for that day). "
                   "I do not invent values: the day is simply absent from the averages (0.1% of the period).")
    a = ay[ay.ninsee == 0].groupby("annee")[["no2", "pm10"]].mean().mean()
    c = cy.groupby("annee")[["no2", "pm10"]].mean().mean()
    st.markdown("**Why I exclude the aggregate rows.** The file mixes communes with higher-level rows "
                f"(code 0 = region, 75, 77… = départements). The “region” row shows NO₂ at {prep.num(a.no2)} versus {prep.num(c.no2)} "
                "on average over communes. Hypothesis: these rows are population-weighted (closer to dense areas) rather than a simple "
                "mean of communes. Mixing the two levels would distort everything, so I drop them and say so.")
    with st.expander("Limitations and ethics (please read)", expanded=True):
        st.markdown(
            "- **Only 3 years** (2014-2016): weather varies a lot from year to year, so a 3-year decrease does not prove a trend.\n"
            "- **No causality**: I describe gaps, I do not explain their causes (traffic, weather, public policy).\n"
            "- **Index, not concentration**: values are Citeair sub-index points (integers, from 1 to about 120), so they cannot be compared with legal limits in µg/m³; "
            "averaging indices is a simplification. The exact definition should be confirmed in the dataset documentation.\n"
            "- **Commune means are not population-weighted**: they do not represent the average exposure of a resident.\n"
            "- **Band limits** (25, 50…) follow the usual Citeair scale and are shown as visual references only.\n"
            "- **Privacy**: data are aggregated at commune level, no individual data.")
