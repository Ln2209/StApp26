import streamlit as st
from constants import POLL_HELP, POLLUTANTS, SOURCE_TEXT, LICENSE_TEXT


def render():
    st.title("The air I breathe in Île-de-France: is it getting better?")
    st.caption(f"Source: {SOURCE_TEXT} - {LICENSE_TEXT}")
    st.markdown("**Who is this for?** A resident of Île-de-France who wonders whether the air in their region, and in their "
                "département, improved between 2014 and 2016, and where it is the most polluted.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Three questions to guide the reading**")
        st.markdown("1. Did the air improve between 2014 and 2016?\n2. Is it the same everywhere in the region?\n"
                    "3. When in the year is the air the most loaded?")
    with c2:
        st.markdown("**The three pollutants in one sentence**")
        for k, v in POLL_HELP.items():
            st.markdown(f"- **{POLLUTANTS[k]}**: {v}")
    st.info("**What do the numbers mean?** Each value is a daily **Citeair sub-index** for one pollutant in one commune: a unitless scale "
            "where higher means more polluted (roughly 0-25 very low, 25-50 low, 50-75 medium, 75-100 high, above 100 very high). "
            "They are index points, not concentrations in µg/m³.")
    st.caption("Use the sidebar on the left: pollutant, period and départements. Every chart and number updates.")
