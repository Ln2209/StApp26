import pandas as pd
import streamlit as st

from constants import POLLUTANTS, DEP_NAMES, MONTHS_FULL
from utils import io, prep
from sections import intro, overview, deep_dives, quality, conclusions

st.set_page_config(page_title="Air quality in Île-de-France 2014-2016", page_icon="🌫️", layout="wide")


@st.cache_data(show_spinner="Loading data…")
def get_data():
    return io.load_tables()


@st.cache_data
def compute_insights():
    dd, cy, ay, q = get_data()
    reg = cy.groupby("annee")[["no2", "pm10", "o3"]].mean()
    i = {"no2_pct": (reg.loc[2016, "no2"] / reg.loc[2014, "no2"] - 1) * 100, "pm10_pct": (reg.loc[2016, "pm10"] / reg.loc[2014, "pm10"] - 1) * 100}
    d16 = prep.dep_year(dd.assign(), "no2"); d16 = d16[d16.annee == 2016].sort_values("no2")
    i.update(no2_lo=d16.iloc[0].departement, no2_lo_v=d16.iloc[0].no2, no2_hi=d16.iloc[-1].departement, no2_hi_v=d16.iloc[-1].no2)
    i["no2_ratio"] = i["no2_hi_v"] / i["no2_lo_v"]
    for p in ("pm10", "o3"):
        m = prep.monthly(dd, p); mm = m.groupby("mois")[p].mean()
        i[f"{p}_peak_month"] = MONTHS_FULL[int(mm.idxmax()) - 1]; i[f"{p}_peak_v"] = mm.max()
        i[f"{p}_top_by_year"] = {int(y): MONTHS_FULL[int(g.loc[g[p].idxmax(), "mois"]) - 1] for y, g in m.groupby("annee")}
    i["mean16"] = {p: float(reg.loc[2016, p]) for p in ("no2", "pm10", "o3")}
    i["max_commune_day"] = q["max"]
    r = prep.region_daily(dd, "pm10"); top = r.loc[r.pm10.idxmax()]
    i["pm10_day"], i["pm10_day_v"] = top.date, top.pm10
    return i


@st.cache_data
def filtered(deps, start, end):
    dd, *_ = get_data()
    return prep.filter_daily(dd, list(deps), start, end)


dd_all, cy_all, ay_all, quality_report = get_data()
insights = compute_insights()

with st.sidebar:
    st.image("efrei.jpeg", width=140)
    st.markdown(
        "**Hélène LI**  \n"
        "Program : Data Storytelling Dashboard with Streamlit 2026  \n"
        "Year : 2026-2027  \n"
        "Email : helene.li@efrei.net  \n"
        "LinkedIn : https://www.linkedin.com/in/hélène-li \n"
        "GitHub : https://github.com/Ln2209/StApp26.git  \n"
        "Course: Data visualization & Analysis \n"
        "Project proposed by Prof. Mano Mathew"
    )
    st.header("Filters")
    pol = st.selectbox("Pollutant", list(POLLUTANTS), format_func=POLLUTANTS.get,
                       help="Citeair sub-index of NO₂ (traffic), PM10 (particles) or O₃ (ozone, higher in summer).")
    dmin, dmax = dd_all.date.min().date(), dd_all.date.max().date()
    rng = st.date_input("Period", value=(dmin, dmax), min_value=dmin, max_value=dmax,
                        help="Pick a start date and an end date.")
    deps = st.multiselect("Départements", list(DEP_NAMES), default=list(DEP_NAMES), format_func=DEP_NAMES.get,
                          help="75 = Paris; 92, 93, 94 = inner suburbs; 77, 78, 91, 95 = outer suburbs.")
    st.divider()
    st.caption("Data: data.gouv.fr. The takeaway figures at the end do not depend on these filters.")

if not isinstance(rng, (tuple, list)) or len(rng) != 2:
    st.info("Select an end date in the sidebar to continue."); st.stop()
if not deps:
    st.warning("Select at least one département."); st.stop()
start, end = rng
dd = filtered(tuple(sorted(deps)), start, end)
if dd.empty:
    st.warning("No data for this selection."); st.stop()

try:
    import inspect
    plot_kw = {"width": "stretch"} if "width" in inspect.signature(st.plotly_chart).parameters else {"use_container_width": True}
except Exception:
    plot_kw = {"use_container_width": True}


def seasonal_alt(m):
    t = m.loc[m.groupby("annee")[pol].idxmax()]
    tops = ", ".join(f"{int(r.annee)}: {MONTHS_FULL[int(r.mois) - 1]}" for r in t.itertuples())
    return (f"one line per year, one point per month. Highest month by year: {tops}. "
            "Dashed lines: Citeair band limits (25 and 50).")


ctx = dict(pol=pol, label=POLLUTANTS[pol], dd=dd, cy=cy_all, ay=ay_all, q=quality_report, deps=deps, start=pd.Timestamp(start), end=pd.Timestamp(end),
           insights=insights, plot_kw=plot_kw, seasonal_alt=seasonal_alt)
intro.render()
overview.render(ctx)
deep_dives.render(ctx)
quality.render(ctx)
conclusions.render(ctx)
