import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="VP SEO Dashboard", page_icon="✈️", layout="wide")

# ── Logo Primelis (affiché dans l'en-tête) ──
_LOGO_B64 = "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"
_logo_col1, _logo_col2 = st.columns([6, 1])
with _logo_col2:
    st.markdown(
        '<img src="data:image/jpeg;base64,' + _LOGO_B64 + '" style="width:100%;max-width:90px;border-radius:6px;float:right">',
        unsafe_allow_html=True
    )
with _logo_col1:
    pass


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

# ── Bar columns évolution mensuelle ──
st.subheader(f"📈 Évolution mensuelle · Top {top_n} URLs · TTV & Bookings")

col_ev1, col_ev2 = st.columns(2)

for ev_col, df_trend_src, metric_label, color_scale in [
    (col_ev1, df_ttv_agg, "TTV (€)", "Blues"),
    (col_ev2, df_bkg_agg, "Bookings", "Oranges"),
]:
    with ev_col:
        df_t = df_trend_src[df_trend_src["campaign_id"].isin(top_ids)].copy()
        df_t["url_label"] = df_t["url_label"].fillna("ID:" + df_t["campaign_id"].astype(str))
        df_t = df_t.sort_values("month")
        fig_ev = px.bar(
            df_t,
            x="month_label",
            y="value",
            color="url_label",
            barmode="group",
            title=metric_label,
            labels={"value": metric_label, "month_label": "Mois", "url_label": "URL"},
            category_orders={"month_label": ordered_month_labels},
            height=950,
        )
        fig_ev.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.18, font=dict(size=9)),
            margin=dict(b=200),
            xaxis_tickangle=-30,
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
