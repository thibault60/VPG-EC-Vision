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

# Palette commune
palette = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Light24
df_donut = df_merged_global.sort_values("TTV", ascending=False).reset_index(drop=True)
df_donut["color"] = [palette[i % len(palette)] for i in range(len(df_donut))]

col_donut, col_bkg_table = st.columns([1, 1])

with col_donut:
    fig_donut = go.Figure(go.Pie(
        labels=df_donut["url_label"],
        values=df_donut["TTV"],
        hole=0.45,
        marker=dict(colors=df_donut["color"]),
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>TTV : %{value:,.0f} €<br>Part : %{percent}<extra></extra>",
        sort=False
    ))
    fig_donut.update_layout(
        title=f"TTV · Top {top_n} URLs",
        height=600,
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_bkg_table:
    st.markdown(f"**Bookings · Top {top_n} URLs**")
    df_bkg_display = df_donut[["url_label", "Bookings", "TTV", "color"]].copy()
    df_bkg_display = df_bkg_display.sort_values("Bookings", ascending=False).reset_index(drop=True)

    rows_html = ""
    for _, row in df_bkg_display.iterrows():
        dot = f'<span style="display:inline-block;width:11px;height:11px;border-radius:50%;background:{row["color"]};margin-right:6px;vertical-align:middle"></span>'
        rows_html += f"<tr><td>{dot}{row['url_label']}</td><td style='text-align:right'><b>{int(row['Bookings']):,}</b></td><td style='text-align:right;color:#888'>{row['TTV']:,.0f} €</td></tr>"

    table_html = f"""
    <style>
    .bkg-table {{width:100%;border-collapse:collapse;font-size:12.5px}}
    .bkg-table th {{text-align:left;padding:6px 8px;border-bottom:2px solid #ddd;color:#555;font-size:12px}}
    .bkg-table td {{padding:4px 8px;border-bottom:1px solid #f0f0f0}}
    .bkg-table tr:hover td {{background:#f7f7f7}}
    </style>
    <div style="max-height:560px;overflow-y:auto">
    <table class="bkg-table">
      <thead><tr><th>URL</th><th style="text-align:right">Bookings</th><th style="text-align:right">TTV (€)</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table></div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

# ── Bar columns évolution mensuelle — 2 barres par mois (TTV + Bookings) ──
st.subheader(f"📈 Évolution mensuelle · Top {top_n} URLs · TTV & Bookings")

# Agréger toutes les URLs du top en un total par mois
df_ttv_monthly = (
    df_ttv_agg[df_ttv_agg["campaign_id"].isin(top_ids)]
    .groupby(["month", "month_label"])["value"].sum()
    .reset_index().rename(columns={"value": "TTV (€)"})
)
df_bkg_monthly = (
    df_bkg_agg[df_bkg_agg["campaign_id"].isin(top_ids)]
    .groupby(["month", "month_label"])["value"].sum()
    .reset_index().rename(columns={"value": "Bookings"})
)
df_monthly = df_ttv_monthly.merge(df_bkg_monthly, on=["month", "month_label"], how="outer").sort_values("month")

fig_ev = go.Figure()
fig_ev.add_trace(go.Bar(
    x=df_monthly["month_label"],
    y=df_monthly["TTV (€)"],
    name="TTV (€)",
    marker_color="#1d6fa4",
    yaxis="y1",
))
fig_ev.add_trace(go.Bar(
    x=df_monthly["month_label"],
    y=df_monthly["Bookings"],
    name="Bookings",
    marker_color="#f4a840",
    yaxis="y2",
))
fig_ev.update_layout(
    barmode="group",
    height=550,
    xaxis=dict(
        categoryorder="array",
        categoryarray=ordered_month_labels,
        tickfont=dict(size=12),
        tickangle=-30,
    ),
    yaxis=dict(title="TTV (€)", titlefont=dict(color="#1d6fa4"), tickfont=dict(color="#1d6fa4")),
    yaxis2=dict(title="Bookings", titlefont=dict(color="#f4a840"), tickfont=dict(color="#f4a840"),
                overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
    margin=dict(t=40, b=60, l=60, r=60),
)
st.plotly_chart(fig_ev, use_container_width=True)


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

fig_month = go.Figure()
fig_month.add_trace(go.Bar(
    y=df_month_merged["url_label"], x=df_month_merged["TTV"],
    name="TTV (€)", orientation="h", marker_color="#1d6fa4", opacity=0.85
))
fig_month.add_trace(go.Bar(
    y=df_month_merged["url_label"], x=df_month_merged["Bookings"],
    name="Bookings", orientation="h", marker_color="#f4a840", opacity=0.85
))
fig_month.update_layout(
    barmode="group",
    height=max(400, top_n * 45),
    title=f"Top {top_n} URLs · {MONTH_LABELS[selected_month_detail]}",
    yaxis=dict(tickfont=dict(size=10)),
    xaxis=dict(title="Valeur"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    margin=dict(l=20, r=40, t=60, b=20)
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
