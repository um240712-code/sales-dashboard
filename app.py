import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sales Dashboard", layout="wide")

# ============ ألوانك هون ============
COLOR   = "#8B5CF6"
ACCENT  = "#F97316"
PINK    = "#EC4899"
BG      = "#000000"
CARD    = "#0D0D0D"
BORDER  = "#262626"
TEXT    = "#F5F5F5"
MUTED   = "#A78BFA"
# ====================================

CONTINENTS = ["Africa", "Antarctica", "Asia", "Europe",
              "North America", "Oceania", "South America"]

FLAG_COLORS = {
    "United States": "#B22234", "Canada": "#D52B1E", "Mexico": "#006847",
    "Germany": "#DD0000", "United Kingdom": "#3B5BDB", "France": "#0055A4",
    "Spain": "#C60B1E", "Saudi Arabia": "#006C35",
    "United Arab Emirates": "#00732F", "Japan": "#BC002D", "India": "#FF9933",
    "Jordan": "#CE1126", "Australia": "#00008B", "New Zealand": "#00247D",
    "Brazil": "#009C3B", "Argentina": "#74ACDF", "Chile": "#D52B1E",
    "Egypt": "#CE1126", "South Africa": "#007A4D", "Nigeria": "#008751",
    "Morocco": "#C1272D", "Antarctica": "#E5E7EB",
}

CONTINENT_COLORS = {
    "North America": "#3B82F6",
    "Europe":        "#8B5CF6",
    "Asia":          "#F59E0B",
    "Africa":        "#10B981",
    "Oceania":       "#06B6D4",
    "South America": "#EF4444",
    "Antarctica":    "#E5E7EB",
}

PRODUCT_COLORS = {
    "Smart Watch": "#F97316",
    "Sneakers":    "#EC4899",
    "Headphones":  "#8B5CF6",
    "Backpack":    "#10B981",
    "Sunglasses":  "#FACC15",
    "T-Shirt":     "#3B82F6",
    "Charger":     "#14B8A6",
}

st.markdown(f"""
<style>
.block-container {{padding-top: 2.5rem; max-width: 1300px;}}
section[data-testid="stSidebar"] {{
    background: {CARD};
    border-right: 1px solid {BORDER};
}}
div[data-testid="stMetric"] {{
    background: linear-gradient(145deg, {CARD}, {BG});
    border: 1px solid {BORDER};
    padding: 16px 20px; border-radius: 10px;
}}
div[data-testid="stMetricLabel"] p {{font-size: 0.85rem; color: {MUTED};}}
div[data-testid="stMetricValue"] {{color: {TEXT};}}
h1 {{
    font-weight: 600; letter-spacing: -0.5px; color: {TEXT};
    border-bottom: 3px solid {ACCENT}; display: inline-block;
    padding-bottom: 6px;
}}
</style>
""", unsafe_allow_html=True)

# ---------- Data ----------
df = pd.read_csv("sales.csv", parse_dates=["date"])
df["month"] = df["date"].dt.to_period("M").astype(str)

min_date = df["date"].min().date()
max_date = df["date"].max().date()

# ---------- Filters (Sidebar) ----------
with st.sidebar:
    st.markdown("### Analytics")

    conts = st.pills("Continent", CONTINENTS, selection_mode="multi", default=CONTINENTS)
    if not conts:
        conts = CONTINENTS
    pool = df[df["continent"].isin(conts)]

    search = st.text_input("Search country", placeholder="Type a country name")
    available = sorted(pool["country"].unique())
    if search:
        available = [c for c in available if search.lower() in c.lower()]
    chosen = st.multiselect("Country", available, placeholder="All countries")

    # ----- Period quick buttons -----
    period = st.pills(
        "Period",
        ["Last 30 days", "Last 3 months", "This year", "All", "Custom"],
        selection_mode="single",
        default="All",
    )
    if not period:
        period = "All"

    if period == "Custom":
        custom = st.date_input("Date range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)

data = pool[pool["country"].isin(chosen or available)]

# ---------- Apply period ----------
# الفترات محسوبة من آخر تاريخ موجود بالبيانات
if period == "Last 30 days":
    start, end = max_date - pd.Timedelta(days=29), max_date
elif period == "Last 3 months":
    start, end = (pd.Timestamp(max_date) - pd.DateOffset(months=3)).date(), max_date
elif period == "This year":
    start, end = pd.Timestamp(max_date.year, 1, 1).date(), max_date
elif period == "Custom" and isinstance(custom, (tuple, list)) and len(custom) == 2:
    start, end = custom
else:
    start, end = min_date, max_date

data = data[(data["date"].dt.date >= start) & (data["date"].dt.date <= end)]

# ---------- Header ----------
st.title("Global Sales Dashboard")
st.caption(f"Orders from {start:%d %b %Y} to {end:%d %b %Y}")

if len(data) == 0:
    st.warning("No data for the selected filters.")
    st.stop()

# ---------- Download button (Sidebar) ----------
with st.sidebar:
    st.download_button(
        "Download filtered data (CSV)",
        data=data.drop(columns=["month"]).to_csv(index=False).encode("utf-8-sig"),
        file_name="filtered_sales.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ---------- KPIs ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total revenue", f"${data['revenue'].sum():,.0f}")
k2.metric("Orders", f"{len(data):,}")
k3.metric("Average order", f"${data['revenue'].mean():,.1f}")
k4.metric("Countries", data["country"].nunique())

st.write("")


def style(fig):
    fig.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
        title_font_size=16,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT,
    )
    fig.update_xaxes(gridcolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER)
    return fig


# ---------- Trend (daily for short periods, monthly otherwise) ----------
if (end - start).days <= 92:
    data = data.assign(bucket=data["date"].dt.strftime("%Y-%m-%d"))
    trend_title = "Revenue by day"
else:
    data = data.assign(bucket=data["month"])
    trend_title = "Revenue by month"

monthly = data.groupby("bucket", as_index=False).agg(
    revenue=("revenue", "sum"), orders=("order_id", "count"))
monthly["orders_scaled"] = monthly["orders"] * monthly["revenue"].max() / monthly["orders"].max()

fig1 = px.area(monthly, x="bucket", y="revenue", title=trend_title,
               color_discrete_sequence=[COLOR])
fig1.add_scatter(x=monthly["bucket"], y=monthly["orders_scaled"], mode="lines+markers",
                 name="Orders", line=dict(color=PINK, width=2))
fig1.update_layout(showlegend=False)
fig1.update_xaxes(title=None)
fig1.update_yaxes(title=None)
st.plotly_chart(style(fig1), width="stretch")

# ---------- Countries and continents ----------
left, right = st.columns([3, 2])

top = (data.groupby("country", as_index=False)["revenue"].sum()
       .sort_values("revenue", ascending=False).head(10))
fig2 = px.bar(top, x="revenue", y="country", orientation="h",
              title="Top countries by revenue",
              color="country", color_discrete_map=FLAG_COLORS)
fig2.update_layout(showlegend=False)
fig2.update_xaxes(title=None)
fig2.update_yaxes(title=None, autorange="reversed")
left.plotly_chart(style(fig2), width="stretch")

by_cont = data.groupby("continent", as_index=False)["revenue"].sum()
fig3 = px.pie(by_cont, names="continent", values="revenue", hole=0.55,
              title="Revenue by continent",
              color="continent", color_discrete_map=CONTINENT_COLORS)
fig3.update_traces(textfont_color="#FFFFFF")
right.plotly_chart(style(fig3), width="stretch")

# ---------- Products ----------
prod = (data.groupby("product", as_index=False)["revenue"].sum()
        .sort_values("revenue", ascending=False))
fig4 = px.bar(prod, x="revenue", y="product", orientation="h",
              title="Revenue by product",
              color="product", color_discrete_map=PRODUCT_COLORS)
fig4.update_layout(showlegend=False)
fig4.update_xaxes(title=None)
fig4.update_yaxes(title=None, autorange="reversed")
st.plotly_chart(style(fig4), width="stretch")

# ---------- World map ----------
st.subheader("Sales map")

total_rev = data["revenue"].sum()
info = data.groupby("country").agg(
    revenue=("revenue", "sum"),
    orders=("order_id", "count"),
    avg_order=("revenue", "mean"),
).reset_index()
best = (data.groupby(["country", "product"])["revenue"].sum()
        .reset_index().sort_values("revenue")
        .groupby("country").tail(1).set_index("country")["product"])
info["top_product"] = info["country"].map(best)
info["share"] = info["revenue"] / total_rev * 100
info["color"] = info["country"].map(FLAG_COLORS).fillna(COLOR)

fig5 = px.choropleth(
    info, locations="country", locationmode="country names",
    color="country",
    color_discrete_map=dict(zip(info["country"], info["color"])),
    custom_data=["country", "revenue", "orders", "avg_order", "top_product", "share"],
)
fig5.update_traces(
    marker_line_color=BG, marker_line_width=0.6,
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "Revenue: $%{customdata[1]:,.0f}<br>"
        "Orders: %{customdata[2]:,}<br>"
        "Average order: $%{customdata[3]:,.1f}<br>"
        "Top product: %{customdata[4]}<br>"
        "Share of total: %{customdata[5]:.1f}%"
        "<extra></extra>"
    ),
)
fig5.update_layout(
    showlegend=False,
    height=760,
    hoverlabel=dict(bgcolor=CARD, bordercolor=COLOR, font_color=TEXT, font_size=14),
    geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False,
             landcolor=CARD, showocean=True, oceancolor=BG,
             showcountries=True, countrycolor=BORDER,
             projection_type="natural earth",
             lataxis_range=[-60, 85]),
)
st.plotly_chart(style(fig5), width="stretch")