"""Chart functions: one consistent style, axes and units always labelled."""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from constants import MONTHS, UNIT, YEAR_COLORS, ZONE_COLORS

INK = "#1F2937"; GRID = "#E5E7EB"; WARN = "#B42318"; BAND = "#6B7280"


def style(fig, title, height=420):
    fig.update_layout(title=dict(text=title, x=0, xanchor="left", font=dict(size=16, color=INK)),
                      height=height, margin=dict(l=10, r=10, t=60, b=40), separators=".,",
                      font=dict(color=INK), plot_bgcolor="white", paper_bgcolor="white",
                      legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, title_text=""),
                      hoverlabel=dict(bgcolor="white", font_color=INK))
    fig.update_xaxes(gridcolor=GRID, linecolor="#9CA3AF"); fig.update_yaxes(gridcolor=GRID, linecolor="#9CA3AF")
    return fig


def _refs(fig, refs):
    for i, (name, v) in enumerate(refs.items()):
        col = WARN if v >= 50 else BAND
        fig.add_hline(y=v, line_dash="dash", line_color=col, line_width=1.5, annotation_text=name,
                      annotation_position="top left" if i == 0 else "bottom left",
                      annotation_font=dict(size=11, color=col), annotation_bgcolor="rgba(255,255,255,0.85)")


def daily_series(reg, pol, label, refs):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=reg.date, y=reg[pol], mode="lines", name="Daily mean",
                             line=dict(color="#B9CCE3", width=1), hovertemplate="%{x|%d %b %Y}<br>%{y:.1f} " + UNIT))
    fig.add_trace(go.Scatter(x=reg.date, y=reg["rolling_7d"], mode="lines", name="7-day rolling mean",
                             line=dict(color="#0B3C6F", width=2.5), hovertemplate="%{x|%d %b %Y}<br>%{y:.1f} " + UNIT))
    p = reg.loc[reg[pol].idxmax()]
    fig.add_annotation(x=p.date, y=p[pol], text=f"Peak: {p[pol]:.0f} {UNIT}<br>{p.date:%d %b %Y}", showarrow=True,
                       arrowhead=2, ax=70, ay=-10, font=dict(size=12), bgcolor="white", bordercolor="#9CA3AF")
    _refs(fig, refs)
    top = max(reg[pol].max() * 1.2, max(refs.values(), default=0) * 1.3)
    fig.update_xaxes(title="Date"); fig.update_yaxes(title=f"{label} sub-index ({UNIT}), mean over communes", range=[0, top])
    return style(fig, f"{label}: daily mean across Île-de-France")


def seasonal(m, pol, label, refs):
    fig = go.Figure()
    for y in sorted(m.annee.unique()):
        d = m[m.annee == y]
        fig.add_trace(go.Scatter(x=[MONTHS[i - 1] for i in d.mois], y=d[pol], mode="lines+markers", name=str(y),
                                 line=dict(color=YEAR_COLORS.get(y, "#444"), width=3), marker=dict(size=7),
                                 hovertemplate="%{x} " + str(y) + "<br>%{y:.1f} " + UNIT))
    _refs(fig, refs)
    fig.update_xaxes(title="Month", categoryorder="array", categoryarray=MONTHS)
    fig.update_yaxes(title=f"{label} sub-index ({UNIT}), monthly mean", rangemode="tozero")
    return style(fig, f"{label}: the same month, year after year")


def choropleth(d, pol, label, geo):
    """Map with no external basemap (white-bg): no network call from the browser."""
    d = d.assign(code=d.dep.astype(int).astype(str).str.zfill(2))
    fig = px.choropleth_map(d, geojson=geo, locations="code", featureidkey="properties.code", color=pol,
                            hover_name="departement", hover_data={"code": False, pol: ":.1f"},
                            color_continuous_scale="OrRd", map_style="white-bg", center={"lat": 48.7, "lon": 2.5},
                            zoom=6.7, opacity=0.9, labels={pol: f"{label} ({UNIT})"})
    fig.update_traces(marker_line_color="#6B7280", marker_line_width=1)
    fig.update_coloraxes(colorbar=dict(title=f"{label}<br>({UNIT})", thickness=14))
    return style(fig, f"Map: mean {label} by département", height=460)


def small_multiples(dy, pol, label):
    """One panel per year; bars coloured by zone (single trace per panel, fixed category order)."""
    order = dy.groupby("departement")[pol].mean().sort_values().index.tolist()
    years = sorted(dy.annee.unique())
    fig = make_subplots(rows=1, cols=len(years), shared_yaxes=True, horizontal_spacing=0.03,
                        subplot_titles=[str(y) for y in years])
    zone_of = dy.drop_duplicates("departement").set_index("departement")["zone"]
    for i, y in enumerate(years, start=1):
        d = dy[dy.annee == y].set_index("departement").reindex(order)
        fig.add_trace(go.Bar(x=d[pol], y=order, orientation="h", marker_color=[ZONE_COLORS[zone_of[o]] for o in order],
                             text=[f"{v:.1f}" for v in d[pol]], textposition="outside", cliponaxis=False, showlegend=False,
                             hovertemplate="%{y}, " + str(y) + ": %{x:.1f} " + UNIT + "<extra></extra>"), row=1, col=i)
    fig.update_yaxes(categoryorder="array", categoryarray=order)
    fig.update_xaxes(range=[0, dy[pol].max() * 1.3])
    for z, c in ZONE_COLORS.items():  # legend entries (dummy traces)
        fig.add_trace(go.Bar(x=[None], y=[None], name=z, marker_color=c), row=1, col=1)
    fig.add_annotation(text=f"Mean annual {label} sub-index ({UNIT})", x=0.5, y=-0.17, xref="paper", yref="paper", showarrow=False)
    fig = style(fig, "One panel per year: départements ranked", height=480)
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.25, x=0), margin=dict(l=10, r=10, t=70, b=100))
    return fig


def dumbbell(ct, pol, label, y0, y1):
    ct = ct.sort_values("fin")
    fig = go.Figure()
    for _, r in ct.iterrows():
        fig.add_trace(go.Scatter(x=[r.debut, r.fin], y=[r.departement] * 2, mode="lines", showlegend=False,
                                 line=dict(color="#9CA3AF", width=3), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=ct.debut, y=ct.departement, mode="markers", name=str(y0), marker=dict(size=12, color=YEAR_COLORS[2014]),
                             hovertemplate="%{y} " + str(y0) + ": %{x:.1f} " + UNIT))
    fig.add_trace(go.Scatter(x=ct.fin, y=ct.departement, mode="markers", name=str(y1), marker=dict(size=12, color=YEAR_COLORS[2016]),
                             hovertemplate="%{y} " + str(y1) + ": %{x:.1f} " + UNIT))
    xm = ct[["debut", "fin"]].max(axis=1)
    fig.add_trace(go.Scatter(x=xm + xm.max() * 0.03, y=ct.departement, mode="text", showlegend=False, hoverinfo="skip",
                             text=[f"{v:+.0f}%" for v in ct.delta_pct], textposition="middle right", textfont=dict(size=12, color=INK)))
    fig.update_xaxes(title=f"Mean annual {label} sub-index ({UNIT})", range=[0, xm.max() * 1.15]); fig.update_yaxes(title="Département")
    return style(fig, f"Before / after: {y0} → {y1}, by département (change in %)", height=420)


def heatmap(dm, pol, label):
    order = dm.groupby("departement")[pol].mean().sort_values(ascending=False).index.tolist()
    p = dm.pivot(index="departement", columns="mois", values=pol).loc[order]
    fig = px.imshow(p.values, x=MONTHS, y=p.index, aspect="auto", color_continuous_scale="OrRd", text_auto=".0f",
                    labels=dict(x="Month", y="Département", color=f"{label} ({UNIT})"))
    fig.update_xaxes(title="Month (mean over the selected period)", side="bottom"); fig.update_yaxes(title="Département")
    return style(fig, f"{label}: where and when? (département × month)", height=420)


def distribution(cy, pol, label):
    fig = px.box(cy, x="annee", y=pol, color="annee", points=False, color_discrete_map={y: c for y, c in YEAR_COLORS.items()},
                 labels={"annee": "Year", pol: f"{label} ({UNIT})"})
    fig.update_layout(showlegend=False); fig.update_xaxes(type="category", title="Year")
    fig.update_yaxes(title=f"{label} sub-index, annual mean per commune ({UNIT})", rangemode="tozero")
    return style(fig, "Spread across communes, year by year", height=420)
