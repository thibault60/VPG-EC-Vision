import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="VP SEO Dashboard", page_icon="✈️", layout="wide")

MONTH_LABELS = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

MANUAL_URL_MAPPING = {
    21271: "https://www.voyage-prive.com/login/index",
}

def rewrite_url(carambola_url):
    if pd.isna(carambola_url):
        return None
    prefix = "http://fr-carambola.bovpg.net//campaign/microsite/"
    slug = str(carambola_url).replace(prefix, "")
    if slug == "index":
        return f"https://www.voyage-prive.com/login/{slug}"
    return f"https://www.voyage-prive.com/offres/{slug}"

def url_label(url):
    """Retire le domaine — garde uniquement le chemin."""
    if pd.isna(url):
        return None
    return str(url).replace("https://www.voyage-prive.com/", "")

def parse_float(val):
    if pd.isna(val):
        return None
    try:
        return float(str(val).replace(",", "."))
    except ValueError:
        return None

def slug_from_url(url):
    if pd.isna(url):
        return None
    return str(url).replace("https://www.voyage-prive.com/offres/", "")\
                   .replace("https://www.voyage-prive.com/login/", "login/")

@st.cache_data
def load_data(tableau_file, carambola_file):
    df_cara = pd.read_excel(carambola_file)
    df_cara = df_cara[df_cara["Campaign id"] != 0].copy()
    df_cara["vp_url"] = df_cara["Campaign URL"].apply(rewrite_url)
    df_cara = df_cara[["Campaign id", "Campaign name", "vp_url"]].rename(
        columns={"Campaign id": "campaign_id", "Campaign name": "campaign_name"}
    )

    df_tab = pd.read_csv(tableau_file, sep=";")
    df_tab = df_tab.rename(columns={
        "Campaign Id (h1)": "campaign_id",
        "Measure Names": "metric",
        "Measure Values": "value",
        "Date granularity": "month",
        "Registration Year": "year"
    })
    df_tab = df_tab[df_tab["metric"].isin(["TTV", "Bookings"])].copy()
    df_tab = df_tab[df_tab["campaign_id"].notna()].copy()
    df_tab["campaign_id"] = df_tab["campaign_id"].astype(int)
    df_tab["value"] = df_tab["value"].apply(parse_float)
    df_tab = df_tab[(df_tab["year"] == 2025) & (df_tab["month"].between(1, 12))].copy()
    df_tab["month_label"] = df_tab["month"].map(MONTH_LABELS)

    df = df_tab.merge(df_cara, on="campaign_id", how="left")

    # Appliquer le mapping manuel pour les IDs orphelins
    for cid, url in MANUAL_URL_MAPPING.items():
        mask = (df["campaign_id"] == cid) & df["vp_url"].isna()
        df.loc[mask, "vp_url"] = url

    df["slug"] = df["vp_url"].apply(slug_from_url)
    df["url_label"] = df["vp_url"].apply(url_label)
    # Fallback : ID si aucune URL trouvée
    df["url_label"] = df["url_label"].fillna("ID:" + df["campaign_id"].astype(str))
    return df

# ── UI ──
st.title("✈️ Voyage Privé · Dashboard SEO Performance")
st.markdown("Top pages par mois · TTV & Bookings")

with st.sidebar:
    st.header("📂 Fichiers de données")
    tableau_file = st.file_uploader("Export Tableau (CSV)", type=["csv"])
    carambola_file = st.file_uploader("Export Carambola (XLSX)", type=["xlsx"])
    st.divider()
    st.caption("Les fichiers ne sont pas stockés — traitement local.")

if not tableau_file or not carambola_file:
    st.info("👈 Charge les deux fichiers dans la sidebar pour commencer.")
    st.stop()

df = load_data(tableau_file, carambola_file)

with st.sidebar:
    st.header("🔧 Filtres")
    months_available = sorted(df["month"].unique())
    selected_months = st.multiselect(
        "Mois", options=months_available, default=months_available,
        format_func=lambda x: MONTH_LABELS[x]
    )
    top_n = st.slider("Top N pages", min_value=5, max_value=150, value=10)

df_filtered = df[df["month"].isin(selected_months)].copy()
ordered_month_labels = [MONTH_LABELS[m] for m in sorted(selected_months)]

# ── KPIs globaux ──
col1, col2 = st.columns(2)
total_ttv = df_filtered[df_filtered["metric"] == "TTV"]["value"].sum()
total_bkg = df_filtered[df_filtered["metric"] == "Bookings"]["value"].sum()
col1.metric("💶 TTV Total (période)", f"{total_ttv:,.0f} €")
col2.metric("🛎️ Bookings Total (période)", f"{int(total_bkg):,}")
st.divider()

# ──────────────────────────────────────────
# PRÉPARATION DES DONNÉES AGRÉGÉES
# ──────────────────────────────────────────

def get_agg(df_in):
    return (
        df_in.groupby(
            ["month", "month_label", "campaign_id", "campaign_name", "vp_url", "url_label", "slug"],
            dropna=False
        )["value"].sum().reset_index()
    )

df_ttv_agg  = get_agg(df_filtered[df_filtered["metric"] == "TTV"])
df_bkg_agg  = get_agg(df_filtered[df_filtered["metric"] == "Bookings"])

# Top N par TTV (référence commune pour les graphiques merged)
df_ttv_global = (
    df_ttv_agg.groupby(["campaign_id", "campaign_name", "vp_url", "url_label"])["value"]
    .sum().reset_index().rename(columns={"value": "TTV"})
    .sort_values("TTV", ascending=False).head(top_n)
)
df_bkg_global = (
    df_bkg_agg.groupby(["campaign_id", "campaign_name", "vp_url", "url_label"])["value"]
    .sum().reset_index().rename(columns={"value": "Bookings"})
)

# Fusion sur les top IDs TTV
top_ids = df_ttv_global["campaign_id"].tolist()
df_merged_global = df_ttv_global.merge(df_bkg_global, on=["campaign_id", "campaign_name", "vp_url", "url_label"], how="left")
df_merged_global["Bookings"] = df_merged_global["Bookings"].fillna(0)
df_merged_global = df_merged_global.sort_values("TTV", ascending=True)  # pour bar horizontal

# ──────────────────────────────────────────
# GRAPHIQUES MERGED TTV + BOOKINGS
# ──────────────────────────────────────────

st.subheader(f"📊 Top {top_n} URLs · TTV & Bookings (période sélectionnée)")

# ── Bar chart double axe ──
fig_bar = make_subplots(specs=[[{"secondary_y": True}]])

fig_bar.add_trace(
    go.Bar(
        y=df_merged_global["url_label"],
        x=df_merged_global["TTV"],
        name="TTV (€)",
        orientation="h",
        marker_color="#1d6fa4",
        opacity=0.85,
        text=df_merged_global["TTV"].map(lambda x: f"{x:,.0f} €"),
        textposition="outside",
    ),
    secondary_y=False
)

fig_bar.add_trace(
    go.Bar(
        y=df_merged_global["url_label"],
        x=df_merged_global["Bookings"],
        name="Bookings",
        orientation="h",
        marker_color="#f4a840",
        opacity=0.85,
        text=df_merged_global["Bookings"].map(lambda x: f"{int(x):,}"),
        textposition="outside",
    ),
    secondary_y=True
)

fig_bar.update_layout(
    barmode="group",
    height=max(450, top_n * 45),
    title=f"Top {top_n} URLs · TTV (bleu, axe bas) vs Bookings (orange, axe haut)",
    yaxis=dict(tickfont=dict(size=10)),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    margin=dict(l=20, r=120, t=60, b=20)
)
fig_bar.update_xaxes(title_text="TTV (€)", secondary_y=False)
fig_bar.update_xaxes(title_text="Bookings", secondary_y=True)

st.plotly_chart(fig_bar, use_container_width=True)

# ── Line chart évolution mensuelle double axe ──
st.subheader(f"📈 Évolution mensuelle · Top {top_n} URLs · TTV & Bookings")

df_ttv_trend = df_ttv_agg[df_ttv_agg["campaign_id"].isin(top_ids)].copy()
df_bkg_trend = df_bkg_agg[df_bkg_agg["campaign_id"].isin(top_ids)].copy()

fig_line = make_subplots(specs=[[{"secondary_y": True}]])

colors = px.colors.qualitative.Plotly
for i, cid in enumerate(top_ids):
    color = colors[i % len(colors)]
    row_ttv = df_ttv_trend[df_ttv_trend["campaign_id"] == cid].sort_values("month")
    row_bkg = df_bkg_trend[df_bkg_trend["campaign_id"] == cid].sort_values("month")
    label = df_merged_global[df_merged_global["campaign_id"] == cid]["url_label"].values
    label = label[0] if len(label) else str(cid)

    fig_line.add_trace(
        go.Scatter(
            x=row_ttv["month_label"], y=row_ttv["value"],
            name=f"TTV · {label}", mode="lines+markers",
            line=dict(color=color, dash="solid"),
            legendgroup=label, showlegend=True
        ),
        secondary_y=False
    )
    fig_line.add_trace(
        go.Scatter(
            x=row_bkg["month_label"], y=row_bkg["value"],
            name=f"Bkg · {label}", mode="lines+markers",
            line=dict(color=color, dash="dot"),
            legendgroup=label, showlegend=True
        ),
        secondary_y=True
    )

fig_line.update_layout(
    height=560,
    xaxis=dict(
        categoryorder="array",
        categoryarray=ordered_month_labels,
        tickfont=dict(size=11)
    ),
    legend=dict(orientation="h", yanchor="top", y=-0.25, font=dict(size=9)),
    margin=dict(b=160)
)
fig_line.update_yaxes(title_text="TTV (€)", secondary_y=False)
fig_line.update_yaxes(title_text="Bookings", secondary_y=True)
st.plotly_chart(fig_line, use_container_width=True)

# ── Heatmaps côte à côte ──
st.subheader("🗓️ Heatmaps · Mois × Destinations")
col_h1, col_h2 = st.columns(2)

for col, df_h, metric_name in [
    (col_h1, df_ttv_agg, "TTV"),
    (col_h2, df_bkg_agg, "Bookings")
]:
    with col:
        df_heat = df_h[df_h["campaign_id"].isin(top_ids)].copy()
        df_heat["slug"] = df_heat["slug"].fillna("ID:" + df_heat["campaign_id"].astype(str))
        pivot = df_heat.pivot_table(
            index="month_label", columns="slug",
            values="value", aggfunc="sum", fill_value=0
        )
        ordered_rows = [MONTH_LABELS[m] for m in sorted(selected_months) if MONTH_LABELS[m] in pivot.index]
        pivot = pivot.loc[ordered_rows]
        pivot = pivot[pivot.sum(axis=0).sort_values(ascending=False).index]
        fig_h = px.imshow(
            pivot, text_auto=".0f",
            color_continuous_scale="Blues" if metric_name == "TTV" else "Oranges",
            title=f"Heatmap {metric_name}",
            labels=dict(x="Destination", y="Mois", color=metric_name),
            aspect="auto"
        )
        fig_h.update_layout(
            height=max(300, len(pivot) * 50),
            xaxis_tickangle=-45,
            xaxis_tickfont=dict(size=9)
        )
        st.plotly_chart(fig_h, use_container_width=True)

# ── Vue par mois ──
st.divider()
st.subheader("📅 Vue détaillée par mois")

selected_month_detail = st.selectbox(
    "Choisir un mois", options=sorted(selected_months),
    format_func=lambda x: MONTH_LABELS[x]
)

df_month = df_filtered[df_filtered["month"] == selected_month_detail]

df_month_ttv = (
    df_month[df_month["metric"] == "TTV"]
    .groupby(["campaign_id", "campaign_name", "vp_url", "url_label"])["value"]
    .sum().reset_index().rename(columns={"value": "TTV"})
    .sort_values("TTV", ascending=False).head(top_n)
)
df_month_bkg = (
    df_month[df_month["metric"] == "Bookings"]
    .groupby(["campaign_id", "vp_url", "url_label"])["value"]
    .sum().reset_index().rename(columns={"value": "Bookings"})
)
df_month_merged = df_month_ttv.merge(df_month_bkg, on=["campaign_id", "vp_url", "url_label"], how="left")
df_month_merged["Bookings"] = df_month_merged["Bookings"].fillna(0)
df_month_merged = df_month_merged.sort_values("TTV", ascending=True)

fig_month = make_subplots(specs=[[{"secondary_y": True}]])
fig_month.add_trace(
    go.Bar(y=df_month_merged["url_label"], x=df_month_merged["TTV"],
           name="TTV (€)", orientation="h", marker_color="#1d6fa4", opacity=0.85),
    secondary_y=False
)
fig_month.add_trace(
    go.Bar(y=df_month_merged["url_label"], x=df_month_merged["Bookings"],
           name="Bookings", orientation="h", marker_color="#f4a840", opacity=0.85),
    secondary_y=True
)
fig_month.update_layout(
    barmode="group", height=max(400, top_n * 45),
    title=f"Top {top_n} URLs · {MONTH_LABELS[selected_month_detail]}",
    yaxis=dict(tickfont=dict(size=10)),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    margin=dict(l=20, r=80, t=60, b=20)
)
st.plotly_chart(fig_month, use_container_width=True)

st.dataframe(
    df_month_merged[["campaign_id", "campaign_name", "vp_url", "TTV", "Bookings"]]
    .rename(columns={"campaign_id": "ID", "campaign_name": "Campagne", "vp_url": "URL VP"}),
    hide_index=True, use_container_width=True
)

# ── Tableau récap fusionné ──
st.divider()
st.subheader("📊 Tableau récap · TTV + Bookings (toute la période sélectionnée)")

df_recap = df_merged_global.sort_values("TTV", ascending=False).copy()
df_recap["TTV / Booking (€)"] = (df_recap["TTV"] / df_recap["Bookings"].replace(0, float("nan"))).round(0)

df_recap_display = df_recap.head(top_n).copy()
df_recap_display["TTV (€)"]        = df_recap_display["TTV"].map(lambda x: f"{x:,.0f}")
df_recap_display["Bookings"]       = df_recap_display["Bookings"].map(lambda x: f"{int(x):,}")
df_recap_display["TTV / Booking (€)"] = df_recap_display["TTV / Booking (€)"].map(
    lambda x: f"{x:,.0f}" if pd.notna(x) else "-"
)
df_recap_display = df_recap_display.rename(columns={
    "campaign_id": "ID", "campaign_name": "Nom campagne", "vp_url": "URL VP"
})[["ID", "Nom campagne", "URL VP", "TTV (€)", "Bookings", "TTV / Booking (€)"]]

st.caption(f"Top {top_n} pages triées par TTV décroissant")
st.dataframe(df_recap_display, use_container_width=True, hide_index=True)

csv = df_recap[["campaign_id", "campaign_name", "vp_url", "TTV", "Bookings", "TTV / Booking (€)"]].to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Exporter le récap complet (CSV)",
    data=csv, file_name="vp_seo_recap.csv", mime="text/csv"
)
