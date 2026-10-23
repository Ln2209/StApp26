import streamlit as st
from constants import UNIT
from utils import prep


def _band(x):
    return "very low" if x < 25 else "low" if x < 50 else "medium" if x < 75 else "high" if x < 100 else "very high"


def _tops(d):
    return ", ".join(f"{y}: {m}" for y, m in d.items())


def render(ctx):
    st.header("4. Key takeaways")
    I = ctx["insights"]
    st.markdown("**Over the whole period and the whole region (independent of the filters):**")
    st.success(
        f"1. **It is going down, slowly.** From 2014 to 2016, NO₂ falls by {prep.num(abs(I['no2_pct']))}% and PM10 by {prep.num(abs(I['pm10_pct']))}%.\n\n"
        f"2. **Where you live matters more than the year.** In 2016, mean NO₂ is {prep.num(I['no2_hi_v'])} {UNIT} in {I['no2_hi']} versus "
        f"{prep.num(I['no2_lo_v'])} {UNIT} in {I['no2_lo']} (×{prep.num(I['no2_ratio'])}).\n\n"
        f"3. **Pollutants do not follow the same rhythm.** Ozone follows the sun (highest month each year: {_tops(I['o3_top_by_year'])}). "
        f"PM10 behaves more like episodes (highest month: {_tops(I['pm10_top_by_year'])}), with a daily peak of "
        f"{prep.num(I['pm10_day_v'], 0)} {UNIT} on {I['pm10_day']:%d %b %Y}.")
    st.markdown("**What it means for a resident**")
    st.markdown(
        "- Look at **your own département** rather than the regional average: the gap between Paris/inner suburbs and outer suburbs is sharpest for NO₂, a pollutant emitted mostly by traffic.\n"
        "- Watch **pollution episodes** for particles rather than annual means only.\n"
        f"- Keep in mind that **a low average hides bad days**: in 2016 the regional means are NO₂ {prep.num(I['mean16']['no2'], 0)} ({_band(I['mean16']['no2'])}), "
        f"PM10 {prep.num(I['mean16']['pm10'], 0)} ({_band(I['mean16']['pm10'])}) and O₃ {prep.num(I['mean16']['o3'], 0)} ({_band(I['mean16']['o3'])}), "
        f"yet single commune-days reach {I['max_commune_day']['pm10']} for PM10 ({_band(I['max_commune_day']['pm10'])} band on the usual Citeair scale).")
    st.markdown("**Next steps**")
    st.markdown("- Add recent years to confirm the trend.\n- Weight by population to measure real exposure.\n"
                "- Cross with low-emission zones and traffic (other datasets on data.gouv.fr).")
