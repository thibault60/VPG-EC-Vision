import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="VP SEO Dashboard",
    page_icon="✈️",
    layout="wide"
)

MONTH_LABELS = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

def rewrite_url(carambola_url):
    if pd.isna(carambola_url):
        return None
    prefix = "http://fr-carambola.bovpg.net//campaign/microsite/"
    slug = str(carambola_url).replace(prefix, "")
    if slug == "index":
        return f"https://www.voyage-prive.com/login/{slug}"
    return f"https://www.voyage-prive.com/offres/{slug}"

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
    df["slug"] = df["vp_url"].apply(slug_from_url)
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
        "Mois",
        options=months_available,
        default=months_available,
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

# ── Onglets TTV / Bookings ──
tab_ttv, tab_bkg = st.tabs(["💶 Top TTV", "🛎️ Top Bookings"])

for tab, metric_name, unit in [(tab_ttv, "TTV", "€"), (tab_bkg, "Bookings", "")]:
    with tab:
        df_metric = df_filtered[df_filtered["metric"] == metric_name].copy()

        df_agg = (
            df_metric.groupby(
                ["month", "month_label", "campaign_id", "campaign_name", "vp_url", "slug"],
                dropna=False
            )["value"].sum().reset_index()
        )

        df_global = (
            df_agg.groupby(["campaign_id", "campaign_name", "vp_url", "slug"])["value"]
            .sum().reset_index()
            .sort_values("value", ascending=False)
            .head(top_n)
        )

        # Bar chart
        fig_global = px.bar(
            df_global.sort_values("value"),
            x="value", y="vp_url", orientation="h",
            title=f"Top {top_n} URLs · {metric_name} cumulé (période sélectionnée)",
            labels={"value": f"{metric_name} {unit}", "vp_url": "URL"},
            color="value", color_continuous_scale="Blues",
            height=max(400, top_n * 28)
        )
        fig_global.update_layout(coloraxis_showscale=False)
        fig_global.update_yaxes(tickfont=dict(size=10))
        st.plotly_chart(fig_global, use_container_width=True)

        # Line chart évolution
        top_ids = df_global["campaign_id"].tolist()
        df_trend = df_agg[df_agg["campaign_id"].isin(top_ids)].copy()

        fig_trend = px.line(
            df_trend.sort_values("month"),
            x="month_label", y="value", color="vp_url", markers=True,
            title=f"Évolution mensuelle · Top {top_n} URLs · {metric_name}",
            labels={"value": f"{metric_name} {unit}", "month_label": "Mois", "vp_url": "URL"},
            category_orders={"month_label": ordered_month_labels}
        )
        fig_trend.update_layout(
            height=520,
            legend=dict(orientation="h", yanchor="top", y=-0.3, font=dict(size=10))
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # Heatmap — Mois (ordonnées) × Destinations (abscisses)
        st.subheader(f"🗓️ Heatmap {metric_name} · Mois × Destinations")
        df_heat = df_agg[df_agg["campaign_id"].isin(top_ids)].copy()
        df_heat["slug"] = df_heat["slug"].fillna(df_heat["campaign_id"].astype(str))

        pivot = df_heat.pivot_table(
            index="month_label",   # lignes = mois
            columns="slug",        # colonnes = destinations
            values="value",
            aggfunc="sum",
            fill_value=0
        )
        ordered_rows = [MONTH_LABELS[m] for m in sorted(selected_months) if MONTH_LABELS[m] in pivot.index]
        pivot = pivot.loc[ordered_rows]
        pivot = pivot[pivot.sum(axis=0).sort_values(ascending=False).index]

        fig_heat = px.imshow(
            pivot,
            text_auto=".0f",
            color_continuous_scale="Blues",
            title=f"Heatmap {metric_name} — lignes = mois · colonnes = destinations",
            labels=dict(x="Destination", y="Mois", color=metric_name),
            aspect="auto"
        )
        fig_heat.update_layout(
            height=max(300, len(pivot) * 50),
            xaxis_tickangle=-45,
            xaxis_tickfont=dict(size=10)
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        # Tableau détaillé
        st.subheader(f"📋 Tableau · Top {top_n} URLs")
        df_table = df_global[["campaign_id", "campaign_name", "vp_url", "value"]].copy()
        df_table.columns = ["ID", "Nom campagne", "URL VP", metric_name]
        st.dataframe(df_table, use_container_width=True, hide_index=True)

# ── Vue par mois ──
st.divider()
st.subheader("📅 Vue détaillée par mois")

selected_month_detail = st.selectbox(
    "Choisir un mois",
    options=sorted(selected_months),
    format_func=lambda x: MONTH_LABELS[x]
)

df_month = df_filtered[df_filtered["month"] == selected_month_detail]
col_ttv, col_bkg = st.columns(2)

for col, metric_name, unit in [(col_ttv, "TTV", "€"), (col_bkg, "Bookings", "")]:
    with col:
        st.markdown(f"**{metric_name}**")
        df_m = (
            df_month[df_month["metric"] == metric_name]
            .groupby(["campaign_id", "campaign_name", "vp_url"])["value"]
            .sum().reset_index()
            .sort_values("value", ascending=False)
            .head(top_n)
        )
        fig = px.bar(
            df_m.sort_values("value"),
            x="value", y="vp_url", orientation="h",
            color="value", color_continuous_scale="Teal",
            labels={"value": f"{metric_name} {unit}", "vp_url": "URL"},
            height=max(350, top_n * 28)
        )
        fig.update_layout(coloraxis_showscale=False)
        fig.update_yaxes(tickfont=dict(size=10))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            df_m[["campaign_name", "vp_url", "value"]].rename(
                columns={"campaign_name": "Campagne", "vp_url": "URL VP", "value": metric_name}
            ),
            hide_index=True, use_container_width=True
        )

# ── Tableau récap fusionné TTV + Bookings ──
st.divider()
st.subheader("📊 Tableau récap · TTV + Bookings (toute la période sélectionnée)")

df_ttv_all = (
    df_filtered[df_filtered["metric"] == "TTV"]
    .groupby(["campaign_id", "campaign_name", "vp_url"])["value"]
    .sum().reset_index().rename(columns={"value": "TTV (€)"})
)
df_bkg_all = (
    df_filtered[df_filtered["metric"] == "Bookings"]
    .groupby(["campaign_id", "campaign_name", "vp_url"])["value"]
    .sum().reset_index().rename(columns={"value": "Bookings"})
)

df_recap = df_ttv_all.merge(df_bkg_all, on=["campaign_id", "campaign_name", "vp_url"], how="outer")
df_recap["TTV (€)"] = df_recap["TTV (€)"].fillna(0)
df_recap["Bookings"] = df_recap["Bookings"].fillna(0)
df_recap["TTV / Booking (€)"] = (
    df_recap["TTV (€)"] / df_recap["Bookings"].replace(0, float("nan"))
).round(0)
df_recap = df_recap.sort_values("TTV (€)", ascending=False)

st.caption(f"Top {top_n} pages triées par TTV décroissant")

df_recap_display = df_recap.head(top_n).copy()
df_recap_display["TTV (€)"] = df_recap_display["TTV (€)"].map(lambda x: f"{x:,.0f}")
df_recap_display["Bookings"] = df_recap_display["Bookings"].map(lambda x: f"{int(x):,}")
df_recap_display["TTV / Booking (€)"] = df_recap_display["TTV / Booking (€)"].map(
    lambda x: f"{x:,.0f}" if pd.notna(x) else "-"
)
df_recap_display = df_recap_display.rename(columns={
    "campaign_id": "ID", "campaign_name": "Nom campagne", "vp_url": "URL VP"
})
st.dataframe(df_recap_display, use_container_width=True, hide_index=True)

csv = df_recap.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Exporter le récap complet (CSV)",
    data=csv,
    file_name="vp_seo_recap.csv",
    mime="text/csv"
)
