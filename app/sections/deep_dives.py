import streamlit as st
from constants import UNIT
from utils import prep, viz, io
from sections.overview import alt


@st.cache_data
def _geo():
    return io.get_geojson()


def render(ctx):
    pol, label, dd, cy = ctx["pol"], ctx["label"], ctx["dd"], ctx["cy"]
    st.header("2. Where and when? The gaps that matter")
    if dd.empty:
        return
    dm = prep.dep_mean(dd, pol).sort_values(pol)
    lo, hi = dm.iloc[0], dm.iloc[-1]
    st.markdown(f"**The gap between départements is clear: {hi.departement} is at {prep.num(hi[pol])} {UNIT} versus "
                f"{prep.num(lo[pol])} {UNIT} in {lo.departement} (×{prep.num(hi[pol] / lo[pol])}).**")
    a, b = st.columns(2)
    a.plotly_chart(viz.choropleth(dm, pol, label, _geo()), **ctx["plot_kw"])
    a.caption("Chart description: map of the Île-de-France départements coloured by mean level; the darker, the higher. "
              f"The darkest is {hi.departement}, the lightest is {lo.departement}.")
    dy = prep.dep_year(dd, pol)
    b.plotly_chart(viz.small_multiples(dy, pol, label), **ctx["plot_kw"])
    ranks = dy.assign(r=dy.groupby("annee")[pol].rank()).pivot(index="dep", columns="annee", values="r")
    same = bool((ranks.nunique(axis=1) == 1).all())
    b.caption("Chart description: one bar chart per year, départements sorted by their mean over the whole period; "
              + ("the actual ranking is identical every year." if same else "the actual ranking differs slightly in some years (two départements swap places)."))
    st.caption("Means of communes, not weighted by population: a very rural département weighs as much per commune as a dense one.")

    st.subheader("Before / after: who improves the most?")
    yrs = sorted(dd.date.dt.year.unique())
    if len(yrs) >= 2:
        y0, y1 = yrs[0], yrs[-1]
        ct = prep.change_table(cy, pol, ctx["deps"], y0, y1)
        st.plotly_chart(viz.dumbbell(ct, pol, label, y0, y1), **ctx["plot_kw"])
        s = ct.sort_values("delta_pct"); best, worst = s.iloc[0], s.iloc[-1]
        alt(f"for each département, one dot for {y0} and one for {y1} joined by a line; the largest decrease is in "
            f"{best.departement} ({best.delta_pct:+.0f}%), the smallest change in {worst.departement} ({worst.delta_pct:+.0f}%).")
    else:
        st.info("Select at least two years in the period to see the before / after view.")

    st.subheader("When in the year?")
    st.plotly_chart(viz.heatmap(prep.dep_month(dd, pol), pol, label), **ctx["plot_kw"])
    alt(f"grid of départements × months; the darker the cell, the higher {label}. The most loaded season shows up as dark columns.")
