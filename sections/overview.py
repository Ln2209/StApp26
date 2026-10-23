import streamlit as st
from constants import REF_ANNUAL, REF_DAILY, DAILY_KPI_THRESHOLD, UNIT
from utils import prep, viz


def alt(text):
    st.caption("Chart description: " + text)


def render(ctx):
    pol, label, dd = ctx["pol"], ctx["label"], ctx["dd"]
    st.header("1. Overview")
    k = prep.kpis(dd, pol)
    if k is None:
        st.warning("No data for this selection."); return
    seas = prep.monthly(dd, pol)
    st.markdown(f"**In short: over the selected period, {label} averages {prep.num(k['mean'])} {UNIT}, "
                f"and the most exposed area is {k['top'].departement}.**")
    c = st.columns(4)
    with c[0], st.container(border=True):
        st.metric(f"Mean {label}", f"{prep.num(k['mean'])} {UNIT}", help="Mean over the selected communes and period.")
    with c[1], st.container(border=True):
        if k["delta"]:
            d, pct, y0, y1 = k["delta"]
            st.metric(f"Change {y0} → {y1}", f"{prep.num(d)} {UNIT}", f"{pct:+.1f}%", delta_color="inverse",
                      help="Compares the first and last complete years of the period. A decrease is shown in green.")
        else:
            st.metric("Change", "n/a", help="Select at least two complete years to see the change.")
    with c[2], st.container(border=True):
        th = DAILY_KPI_THRESHOLD.get(pol)
        if th:
            n = int((k["reg"][pol] > th).sum())
            st.metric(f"Days above {th} {UNIT}", f"{n} / {k['ndays']}",
                      help="Days when the regional mean sub-index is above 25, the upper limit of the 'very low' band of the Citeair scale.")
        else:
            st.metric("Daily peak", f"{prep.num(k['reg'][pol].max())} {UNIT}")
    with c[3], st.container(border=True):
        st.metric("Most exposed département", k["top"].departement, f"{prep.num(k['top'][pol])} {UNIT}", delta_color="off")

    st.subheader("A year in curves")
    st.plotly_chart(viz.seasonal(seas, pol, label, REF_ANNUAL[pol]), **ctx["plot_kw"])
    alt(ctx["seasonal_alt"](seas))
    st.subheader("Day by day")
    st.plotly_chart(viz.daily_series(k["reg"], pol, label, REF_DAILY[pol]), **ctx["plot_kw"])
    alt(f"line chart of the daily mean of {label} from {ctx['start']:%d %b %Y} to {ctx['end']:%d %b %Y}, with its 7-day rolling mean "
        f"and the highest peak annotated. Dashed lines mark the Citeair band limits (25 and 50).")
    st.caption("How to read the values: they are Citeair sub-index points (a unitless scale, roughly 0 to 100+), not concentrations in µg/m³. "
               "Dashed lines mark the band limits (0-25 very low, 25-50 low, 50-75 medium, 75-100 high, above 100 very high; to confirm in the dataset documentation).")
