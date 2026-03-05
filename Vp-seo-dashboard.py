import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(
    page_title="VP SEO Dashboard",
    page_icon="✈️",
    layout="wide"
)

# ──────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────

MONTH_LABELS = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

def rewrite_url(carambola_url: str) -> str:
    """Réécrit une URL Carambola en URL Voyage Privé."""
    if pd.isna(carambola_url):
        return None
    prefix = "http://fr-carambola.bovpg.net//campaign/microsite/"
    slug = str(carambola_url).replace(prefix, "")
    if slug == "index":
        return f"https://www.voyage-prive.com/login/{slug}"
    return f"https://www.voyage-prive.com/offres/{slug}"

def parse_float(val):
    """Parse les valeurs numériques avec virgule comme séparateur décimal."""
    if pd.isna(val):
        return None
    try:
        return float(str(val).replace(",", "."))
    except ValueError:
        return None

# ──────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ──────────────────────────────────────────

@st.cache_data
def load_data(tableau_file, carambola_file):
    # --- Carambola ---
    df_cara = pd.read_excel(carambola_file)
    df_cara = df_cara[df_cara["Campaign id"] != 0].copy()
    df_cara["vp_url"] = df_cara["Campaign URL"].apply(rewrite_url)
    df_cara = df_cara[["Campaign id", "Campaign name", "vp_url"]].rename(
        columns={"Campaign id": "campaign_id", "Campaign name": "campaign_name"}
    )

    # --- Tableau ---
    df_tab = pd.read_csv(tableau_file, sep=";")
    df_tab = df_tab.rename(columns={
        "Campaign Id (h1)": "campaign_id",
        "Measure Names": "metric",
        "Measure Values": "value",
        "Date granularity": "month",
        "Registration Year": "year"
    })

    # Garder seulement TTV et Bookings
    df_tab = df_tab[df_tab["metric"].isin(["TTV", "Bookings"])].copy()

    # Garder seulement les lignes avec un campaign_id
    df_tab = df_tab[df_tab["campaign_id"].notna()].copy()
    df_tab["campaign_id"] = df_tab["campaign_id"].astype(int)

    # Parser les valeurs
    df_tab["value"] = df_tab["value"].apply(parse_float)

    # Garder seulement 2025 et les mois 1-12
    df_tab = df_tab[
        (df_tab["year"] == 2025) &
        (df_tab["month"].between(1, 12))
    ].copy()

    df_tab["month_label"] = df_tab["month"].map(MONTH_LABELS)

    # --- Merge ---
    df = df_tab.merge(df_cara, on="campaign_id", how="left")

    return df

# ──────────────────────────────────────────
# INTERFACE
# ──────────────────────────────────────────

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

# ──────────────────────────────────────────
# FILTRES
# ──────────────────────────────────────────

with st.sidebar:
    st.header("🔧 Filtres")

    months_available = sorted(df["month"].unique())
    selected_months = st.multiselect(
        "Mois",
        options=months_available,
        default=months_available,
        format_func=lambda x: MONTH_LABELS[x]
    )

    top_n = st.slider("Top N pages", min_value=5, max_value=30, value=10)

df_filtered = df[df["month"].isin(selected_months)].copy()

# ──────────────────────────────────────────
# MÉTRIQUES GLOBALES
# ──────────────────────────────────────────

col1, col2 = st.columns(2)

total_ttv = df_filtered[df_filtered["metric"] == "TTV"]["value"].sum()
total_bkg = df_filtered[df_filtered["metric"] == "Bookings"]["value"].sum()

col1.metric("💶 TTV Total (période)", f"{total_ttv:,.0f} €")
col2.metric("🛎️ Bookings Total (période)", f"{int(total_bkg):,}")

st.divider()

# ──────────────────────────────────────────
# TOP PAGES PAR MOIS
# ──────────────────────────────────────────

tab_ttv, tab_bkg = st.tabs(["💶 Top TTV", "🛎️ Top Bookings"])

for tab, metric_name, unit in [
    (tab_ttv, "TTV", "€"),
    (tab_bkg, "Bookings", "")
]:
    with tab:
        df_metric = df_filtered[df_filtered["metric"] == metric_name].copy()

        # Groupby par mois + page
        df_agg = (
            df_metric.groupby(["month", "month_label", "campaign_id", "campaign_name", "vp_url"], dropna=False)["value"]
            .sum()
            .reset_index()
        )

        # ── Graphique : Top global (toute la période sélectionnée) ──
        df_global = (
            df_agg.groupby(["campaign_id", "campaign_name", "vp_url"])["value"]
            .sum()
            .reset_index()
            .sort_values("value", ascending=False)
            .head(top_n)
        )
        df_global["label"] = df_global["campaign_name"].fillna(df_global["vp_url"].fillna(df_global["campaign_id"].astype(str)))

        fig_global = px.bar(
            df_global.sort_values("value"),
            x="value",
            y="label",
            orientation="h",
            title=f"Top {top_n} pages · {metric_name} cumulé (période sélectionnée)",
            labels={"value": f"{metric_name} {unit}", "label": "Page"},
            color="value",
            color_continuous_scale="Blues"
        )
        fig_global.update_layout(coloraxis_showscale=False, height=500)
        st.plotly_chart(fig_global, use_container_width=True)

        # ── Graphique : Évolution mensuelle des top pages ──
        top_ids = df_global["campaign_id"].tolist()
        df_trend = df_agg[df_agg["campaign_id"].isin(top_ids)].copy()
        df_trend["label"] = df_trend["campaign_name"].fillna(
            df_trend["vp_url"].fillna(df_trend["campaign_id"].astype(str))
        )

        fig_trend = px.line(
            df_trend.sort_values("month"),
            x="month_label",
            y="value",
            color="label",
            markers=True,
            title=f"Évolution mensuelle · Top {top_n} pages · {metric_name}",
            labels={"value": f"{metric_name} {unit}", "month_label": "Mois", "label": "Page"},
            category_orders={"month_label": [MONTH_LABELS[m] for m in sorted(selected_months)]}
        )
        fig_trend.update_layout(height=500, legend=dict(orientation="h", yanchor="bottom", y=-0.5))
        st.plotly_chart(fig_trend, use_container_width=True)

        # ── Heatmap : Top pages × Mois ──
        st.subheader(f"🗓️ Heatmap {metric_name} par page × mois")
        pivot = df_agg[df_agg["campaign_id"].isin(top_ids)].pivot_table(
            index="campaign_name",
            columns="month_label",
            values="value",
            aggfunc="sum",
            fill_value=0
        )
        # Ordonner les colonnes par numéro de mois
        ordered_cols = [MONTH_LABELS[m] for m in sorted(selected_months) if MONTH_LABELS[m] in pivot.columns]
        pivot = pivot[ordered_cols]
        pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]

        fig_heat = px.imshow(
            pivot,
            text_auto=True,
            color_continuous_scale="Blues",
            title=f"Heatmap {metric_name}",
            labels=dict(x="Mois", y="Page", color=metric_name)
        )
        fig_heat.update_layout(height=max(300, len(pivot) * 40))
        st.plotly_chart(fig_heat, use_container_width=True)

        # ── Tableau détaillé ──
        st.subheader(f"📋 Tableau détaillé · Top {top_n} pages")
        df_table = df_global[["campaign_id", "campaign_name", "vp_url", "value"]].copy()
        df_table.columns = ["ID", "Nom campagne", "URL VP", f"{metric_name} {unit}"]
        df_table[f"{metric_name} {unit}"] = df_table[f"{metric_name} {unit}"].map(
            lambda x: f"{x:,.0f}" if pd.notna(x) else "-"
        )
        st.dataframe(df_table, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────
# VUE MENSUELLE DÉTAILLÉE
# ──────────────────────────────────────────

st.divider()
st.subheader("📅 Vue détaillée par mois")

selected_month_detail = st.selectbox(
    "Choisir un mois",
    options=sorted(selected_months),
    format_func=lambda x: MONTH_LABELS[x]
)

df_month = df_filtered[df_filtered["month"] == selected_month_detail]

col_ttv, col_bkg = st.columns(2)

for col, metric_name, unit in [
    (col_ttv, "TTV", "€"),
    (col_bkg, "Bookings", "")
]:
    with col:
        st.markdown(f"**{metric_name}**")
        df_m = (
            df_month[df_month["metric"] == metric_name]
            .groupby(["campaign_id", "campaign_name", "vp_url"])["value"]
            .sum()
            .reset_index()
            .sort_values("value", ascending=False)
            .head(top_n)
        )
        df_m["label"] = df_m["campaign_name"].fillna(df_m["vp_url"].fillna(df_m["campaign_id"].astype(str)))
        fig = px.bar(
            df_m.sort_values("value"),
            x="value", y="label",
            orientation="h",
            color="value",
            color_continuous_scale="Teal",
            labels={"value": f"{metric_name} {unit}", "label": "Page"}
        )
        fig.update_layout(coloraxis_showscale=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            df_m[["campaign_name", "vp_url", "value"]].rename(
                columns={"campaign_name": "Campagne", "vp_url": "URL VP", "value": metric_name}
            ),
            hide_index=True, use_container_width=True
        )
