import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import requests
import os

st.set_page_config(page_title="VP SEO Dashboard", page_icon="🗺️", layout="wide")




# ──────────────────────────────────────────
# CATÉGORISATION GPT DES URLS
# ──────────────────────────────────────────

# Ordre : du plus spécifique au plus général
# Chaque tuple : (catégorie, [patterns slug])
CATEGORY_RULES = [
    ("All inclusive",   ["all-inclusive", "tout-compris", "tout-inclus", "tout-inclus",
                         "vacances-et-sejours-all-inclusive", "bali-tout-compris",
                         "voyage-tout-compris", "voyage-tout-inclus", "derniere-minute-tout-inclus",
                         "week-end-tout-compris", "sejours-tout-compris", "voyage-derniere-minute-tout-inclus"]),
    ("Circuit",         ["circuit-", "autotour", "circuits-", "voyage-organise-"]),
    ("Dernière minute", ["last-minute", "derniere-minute", "dernieres-minutes",
                         "depart-demain", "derniere-chance", "croisieres-sur-le-nil-last-minute"]),
    ("Vol + Hôtel",     ["vol-hotel", "vols-plus-hotels", "vol-plus-hotel"]),
    ("Hôtel",           ["hotel-", "hotels-", "hotel-en-", "hotel-a-", "hotel-au-",
                         "hotel-all-inclusive"]),
    ("Meilleurs",       ["top-", "meilleurs-hotels", "meilleurs-hotels-clubs",
                         "les-meilleurs", "top-5-", "top-9-", "top-10-"]),
    ("Où partir",       ["ou-partir", "Ou-partir", "ou-partir-", "quand-partir"]),
    ("Que faire",       ["que-faire"]),
    ("Séjour",          ["sejour-", "sejours-", "offres-sejours", "sejour-a-", "sejour-au-",
                         "sejour-en-", "sejours-en-", "sejours-aux-", "sejours-de-luxe",
                         "sejour-et-voyage-"]),
    ("Ski",             ["ski-"]),
    ("Ventes privées",  ["vente-privee", "ventes-privees", "promo-", "bon-plan",
                         "bons-plans", "bons-plan", "offres-black-friday",
                         "sejour-et-voyage-pas-cher", "vente-privee-pour", "promo-vacances"]),
    ("Vacances",        ["vacances-", "vacance-", "vacances-famille", "vacances-pas-cheres"]),
    ("Week-end",        ["week-end-", "week-ends-", "week-end-a-", "week-end-au-",
                         "week-end-tout-compris"]),
    ("Voyage",          ["voyage-", "voyages-", "voyage-au-", "voyage-en-",
                         "voyage-aux-", "voyage-dans-"]),
    ("Combiné",         ["combine-", "combined-"]),
    ("Croisière",       ["croisiere", "nil-last-minute"]),
    ("Home / Login",    ["login", "login/index"]),
    ("Autre",           ["voyage-pirates", "offres-black-friday"]),
]

def categorize_url_rules(url):
    """Catégorisation par règles — retourne None si non reconnu (→ envoi à GPT)."""
    if not url or not isinstance(url, str):
        return "Autre"
    # Cas spécial login
    if "login" in url:
        return "Home / Login"
    slug = url.lower().split("/offres/")[-1] if "/offres/" in url else url.lower()
    for cat, patterns in CATEGORY_RULES:
        for p in patterns:
            if slug.startswith(p.lower()) or p.lower() in slug:
                return cat
    return None  # → GPT traitera ce cas

@st.cache_data(ttl=86400, show_spinner=False)
def categorize_urls_gpt(urls_tuple, openai_key):
    """Envoie les URLs non catégorisées à GPT en batch et retourne {url: {type, destination}}."""
    urls = list(urls_tuple)
    
    # Catégorisation par règles d'abord — None = non reconnu → GPT
    result = {}
    to_gpt = []
    for url in urls:
        cat = categorize_url_rules(url)
        slug = url.lower().split("/offres/")[-1] if "/offres/" in url else url.lower().split("voyage-prive.com/")[-1]
        dest = extract_destination_rules(slug)
        if cat is not None:
            result[url] = {"type": cat, "destination": dest}
        else:
            to_gpt.append(url)

    # Récupère la clé Claude depuis st.secrets ou le champ manuel
    _openai_key = openai_key
    if not _openai_key:
        try:
            _openai_key = st.secrets["openai"]["api_key"]
        except Exception:
            pass

    if not to_gpt or not _openai_key:
        for url in to_gpt:
            slug = url.lower().split("/offres/")[-1] if "/offres/" in url else ""
            result[url] = {"type": "Voyage", "destination": extract_destination_rules(slug)}
        return result

    # Batch Claude pour les URLs ambiguës
    batch_size = 30
    for i in range(0, len(to_gpt), batch_size):
        batch = to_gpt[i:i+batch_size]
        prompt = """Tu es un expert SEO voyage. Pour chaque URL ci-dessous, retourne un JSON avec:
- "type": une des valeurs: All inclusive, Circuit, Dernière minute, Hôtel, Meilleurs, Où partir, Quand partir, Séjour, Ski, Vacances, Ventes privées, Vol + Hôtel, Voyage, Week-end, Que faire, Combiné, Croisière, Autre
- "destination": le pays ou la région principale (ex: "France", "Maroc", "Maldives", "Europe"), ou null si générique

URLs:
""" + "\n".join(batch) + """

Réponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans explication :
{"url1": {"type": "...", "destination": "..."}, "url2": {...}}"""

        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {_openai_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "response_format": {"type": "json_object"},
                },
                timeout=30
            )
            raw = resp.json()["choices"][0]["message"]["content"].strip()
            parsed = json.loads(raw)
            result.update(parsed)
        except Exception:
            for url in batch:
                slug = url.lower().split("/offres/")[-1] if "/offres/" in url else ""
                result[url] = {"type": "Voyage", "destination": extract_destination_rules(slug)}

    return result

def extract_destination_rules(slug):
    """Extrait la destination depuis le slug par règles simples."""
    slug = slug.lower()
    destinations = {
        "France": ["france", "corse", "paris", "bordeaux", "lyon", "guyane", "martinique", "guadeloupe", "antilles", "reunion"],
        "Maroc": ["maroc", "marrakech", "agadir", "casablanca"],
        "Espagne": ["espagne", "barcelone", "madrid", "seville", "majorque", "mallorca", "minorque", "ibiza", "canaries", "lanzarote", "fuerteventura", "tenerife", "andalousie"],
        "Grèce": ["grece", "crete", "santorin", "mykonos", "rhodes", "corfou", "iles-grecques"],
        "Italie": ["italie", "rome", "venise", "sardaigne", "sicile", "pouilles", "cinque-terre", "capri", "amalfi", "florence"],
        "Egypte": ["egypte", "hurghada", "charm-el-cheikh", "louxor"],
        "Maldives": ["maldives"],
        "Thaïlande": ["thailande", "bangkok", "phuket", "koh-samui"],
        "Dubai": ["dubai", "emirats-arabes"],
        "Turquie": ["turquie", "istanbul", "cappadoce", "antalya", "bodrum"],
        "Tunisie": ["tunisie", "djerba", "hammamet"],
        "Portugal": ["portugal", "lisbonne", "porto", "madere", "acores"],
        "Mexique": ["mexique", "cancun", "playa-del-carmen", "riviera-maya"],
        "Bali": ["bali"],
        "Japon": ["japon", "tokyo", "kyoto", "osaka"],
        "Kenya": ["kenya"],
        "Zanzibar": ["zanzibar"],
        "Seychelles": ["seychelles"],
        "Île Maurice": ["ile-maurice", "mauric"],
        "Sri Lanka": ["sri-lanka"],
        "Jordanie": ["jordanie", "petra"],
        "Croatie": ["croatie", "dubrovnik"],
        "Islande": ["islande", "reykjavik"],
        "Laponie": ["laponie", "abisko"],
        "Norvège": ["norvege"],
        "Suisse": ["suisse", "geneve"],
        "Belgique": ["belgique", "bruxelles"],
        "Albanie": ["albanie"],
        "Cuba": ["cuba", "la-havane"],
        "Bahamas": ["bahamas"],
        "Pérou": ["perou", "lima", "machu-picchu"],
        "Malaisie": ["malaisie", "kuala-lumpur"],
        "Namibie": ["namibie"],
        "Tanzanie": ["tanzanie"],
        "Afrique du Sud": ["afrique-du-sud", "cape-town"],
        "Cap-Vert": ["cap-vert", "sal"],
        "Hawaii": ["hawaii"],
        "Punta Cana": ["punta-cana"],
        "Budapest": ["budapest"],
        "Prague": ["prague"],
        "Amsterdam": ["amsterdam"],
        "Londres": ["londres", "london"],
        "New York": ["new-york"],
        "Rome": ["rome"],
        "Barcelone": ["barcelone"],
        "Istanbul": ["istanbul"],
        "Finlande": ["finlande"],
        "Europe": ["europe"],
        "Afrique": ["afrique"],
        "USA": ["usa", "etats-unis", "amerique"],
    }
    for dest, keywords in destinations.items():
        for kw in keywords:
            if kw in slug:
                return dest
    return None

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

    # Lecture CSV — séparateur ";"
    df_tab = pd.read_csv(tableau_file, sep=";", engine="python")
    df_tab.columns = df_tab.columns.str.strip()

    if "Campaign Id (h1)" not in df_tab.columns:
        raise ValueError(
            "MAUVAIS_FICHIER: Ce fichier Tableau est un export agrégé (par Channel), "
            "pas un export par campagne. Il manque la colonne 'Campaign Id (h1)'. "
            f"Colonnes trouvées : {list(df_tab.columns)}"
        )

    df_tab = df_tab.rename(columns={
        "Campaign Id (h1)": "campaign_id",
        "Measure Names":    "metric",
        "Measure Values":   "value",
        "Date granularity": "month",
        "Registration Year":"year"
    })
    df_tab = df_tab[df_tab["metric"].isin(["TTV", "Bookings", "TTV per lead Net"])].copy()
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
_VP_LOGO_B64 = "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"
st.markdown(
    '<div style="display:flex;align-items:center;gap:14px;margin-bottom:8px">'
    '<img src="data:image/png;base64,' + _VP_LOGO_B64 + '" style="height:52px;border-radius:6px">'
    '<span style="font-size:1.8rem;font-weight:700">Voyage Privé · Dashboard SEO Performance</span>'
    '</div>',
    unsafe_allow_html=True
)
st.markdown("Top pages par mois · TTV & Bookings")

with st.sidebar:
    st.header("📂 Fichiers de données")
    tableau_file   = st.file_uploader("Export Tableau (CSV)",    type=["csv"])
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

    st.caption("Mois")
    selected_months = []
    for m in months_available:
        if st.checkbox(MONTH_LABELS[m], value=True, key=f"month_cb_{m}"):
            selected_months.append(m)
    if not selected_months:
        selected_months = months_available

    top_n = st.slider("Nombre de pages à analyser", min_value=5, max_value=500, value=50, step=5)

    st.divider()
    st.header("🤖 Catégorisation GPT")
    _has_secret_key = bool(st.secrets.get("openai", {}).get("api_key", ""))
    if _has_secret_key:
        st.success("✅ Clé OpenAI configurée")
        openai_key = st.secrets["openai"]["api_key"]
    else:
        openai_key = st.text_input("Clé API OpenAI (optionnel)", type="password",
            help="Ou ajoute [openai] api_key dans st.secrets")
    if st.button("🤖 Lancer la catégorisation IA", use_container_width=True):
        st.session_state["run_categorization"] = True
    if st.button("🗑️ Réinitialiser", use_container_width=True):
        st.session_state["run_categorization"] = False
        st.session_state.pop("cats_cache", None)
        st.cache_data.clear()
    enable_cat = st.session_state.get("run_categorization", False)

    st.divider()
    st.header("🗂️ Filtres catégories")



df_filtered = df[df["month"].isin(selected_months)].copy()
ordered_month_labels = [MONTH_LABELS[m] for m in sorted(selected_months)]

# ── Catégorisation des URLs ──
# Catégorisation sur TOUTES les URLs du dataset (pas filtrées par mois)
all_urls_full = df["vp_url"].dropna().unique().tolist()

if enable_cat:
    if "cats_cache" not in st.session_state:
        with st.spinner("Catégorisation des URLs..."):
            st.session_state["cats_cache"] = categorize_urls_gpt(tuple(all_urls_full), openai_key or "")
    cats = st.session_state["cats_cache"]
    df_filtered["type_page"]   = df_filtered["vp_url"].map(lambda u: cats.get(u, {}).get("type", "Autre") if isinstance(u, str) else "Autre")
    df_filtered["destination"] = df_filtered["vp_url"].map(lambda u: cats.get(u, {}).get("destination") if isinstance(u, str) else None)
else:
    df_filtered["type_page"]   = df_filtered["vp_url"].apply(lambda u: categorize_url_rules(u) or "Voyage")
    df_filtered["destination"] = df_filtered["vp_url"].apply(
        lambda u: extract_destination_rules(u.lower().split("/offres/")[-1] if isinstance(u, str) and "/offres/" in u else "") if isinstance(u, str) else None
    )

# Mise à jour dynamique des filtres sidebar
all_types = sorted(df_filtered["type_page"].dropna().unique().tolist())
all_dests = sorted(df_filtered["destination"].dropna().unique().tolist())

ALL_KNOWN_TYPES = sorted(set([cat for cat, _ in CATEGORY_RULES]))

with st.sidebar:
    filter_type = st.multiselect(
        "Schéma de recherche",
        options=all_types if all_types else ALL_KNOWN_TYPES,
        key="filter_type_dyn"
    )
    filter_dest = st.multiselect("Destination", options=all_dests, key="filter_dest_dyn")

if filter_type:
    df_filtered = df_filtered[df_filtered["type_page"].isin(filter_type)]
if filter_dest:
    df_filtered = df_filtered[df_filtered["destination"].isin(filter_dest)]

# ── KPIs globaux ──
col1, col2 = st.columns(2)
total_ttv = df_filtered[df_filtered["metric"] == "TTV"]["value"].sum()
total_bkg = df_filtered[df_filtered["metric"] == "Bookings"]["value"].sum()
col1.metric("💶 TTV Total (période)", f"{total_ttv:,.0f} €")
col2.metric("🛎️ Bookings Total (période)", f"{int(total_bkg):,}")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Top URLs",
    "📅 Vue par mois",
    "🌍 Par destination",
    "🗂️ Par type de page",
])

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
df_tpl_agg  = get_agg(df_filtered[df_filtered["metric"] == "TTV per lead Net"])

# IDs à épingler (toujours présents, même TTV=0)
_pinned_ids = list(MANUAL_URL_MAPPING.keys())

# Agrégation complète TTV + Bookings
_ttv_all = (
    df_ttv_agg.groupby(["campaign_id", "campaign_name", "vp_url", "url_label"])["value"]
    .sum().reset_index().rename(columns={"value": "TTV"})
)
_bkg_all = (
    df_bkg_agg.groupby(["campaign_id", "campaign_name", "vp_url", "url_label"])["value"]
    .sum().reset_index().rename(columns={"value": "Bookings"})
)
_all = _ttv_all.merge(_bkg_all, on=["campaign_id", "campaign_name", "vp_url", "url_label"], how="outer").fillna(0)

# Exclure les zéros — mais garder les IDs épinglés
_active = _all[(_all["TTV"] > 0) | (_all["Bookings"] > 0)]
_pinned_rows = _all[_all["campaign_id"].isin(_pinned_ids)]
_all_clean = pd.concat([_active, _pinned_rows]).drop_duplicates(subset=["campaign_id"])

# Épinglés en premier, puis top N par TTV sur le reste
_pinned_df = _all_clean[_all_clean["campaign_id"].isin(_pinned_ids)]
_rest_df = _all_clean[~_all_clean["campaign_id"].isin(_pinned_ids)].sort_values("TTV", ascending=False).head(top_n)

df_ttv_global = pd.concat([_pinned_df, _rest_df]).drop_duplicates(subset=["campaign_id"])
df_bkg_global = _bkg_all  # garde tout pour les merges ultérieurs

# Fusion finale
top_ids = df_ttv_global["campaign_id"].tolist()
df_merged_global = df_ttv_global.copy()
df_merged_global = df_merged_global.sort_values("TTV", ascending=True)  # pour bar horizontal

# ──────────────────────────────────────────
# GRAPHIQUES MERGED TTV + BOOKINGS
# ──────────────────────────────────────────

with tab1:
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

ev_mode = st.radio(
    "Afficher :",
    options=["TTV + Bookings", "TTV uniquement", "Bookings uniquement"],
    horizontal=True,
    label_visibility="collapsed"
)

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

# Palette commune par URL (même ordre que le donut)
palette = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24 + px.colors.qualitative.Light24
url_labels_ordered = (
    df_ttv_agg[df_ttv_agg["campaign_id"].isin(top_ids)]
    .groupby(["campaign_id", "url_label"])["value"].sum()
    .reset_index().sort_values("value", ascending=False)["url_label"]
    .fillna("ID:" + df_ttv_agg["campaign_id"].astype(str))
    .tolist()
)
color_map = {lbl: palette[i % len(palette)] for i, lbl in enumerate(url_labels_ordered)}

fig_ev = make_subplots(specs=[[{"secondary_y": True}]])

# ── Barres empilées TTV par URL (axe gauche) ──
if ev_mode in ("TTV + Bookings", "TTV uniquement"):
    for cid in top_ids:
        lbl = df_merged_global[df_merged_global["campaign_id"] == cid]["url_label"].values
        lbl = lbl[0] if len(lbl) else "ID:" + str(cid)
        color = color_map.get(lbl, "#888")
        row_ttv = df_ttv_agg[df_ttv_agg["campaign_id"] == cid].sort_values("month")
        fig_ev.add_trace(go.Bar(
            x=row_ttv["month_label"],
            y=row_ttv["value"],
            name=lbl,
            marker=dict(color=color),
            legendgroup=lbl,
            showlegend=True,
            hovertemplate="<b>%{fullData.name}</b><br>TTV : %{y:,.0f} €<extra></extra>"
        ), secondary_y=False)

# ── Ligne Bookings par URL (axe droit) ──
if ev_mode in ("TTV + Bookings", "Bookings uniquement"):
    for cid in top_ids:
        lbl = df_merged_global[df_merged_global["campaign_id"] == cid]["url_label"].values
        lbl = lbl[0] if len(lbl) else "ID:" + str(cid)
        color = color_map.get(lbl, "#888")
        row_bkg = df_bkg_agg[df_bkg_agg["campaign_id"] == cid].sort_values("month")
        show_legend = ev_mode == "Bookings uniquement"
        fig_ev.add_trace(go.Scatter(
            x=row_bkg["month_label"],
            y=row_bkg["value"],
            name=lbl,
            mode="lines+markers",
            line=dict(color=color, width=1.8, dash="dot"),
            marker=dict(color=color, size=5),
            legendgroup=lbl,
            showlegend=show_legend,
            hovertemplate="<b>%{fullData.name}</b><br>Bookings : %{y:,.0f}<extra></extra>"
        ), secondary_y=True)

    fig_ev.update_layout(
        barmode="stack",
        height=700,
        xaxis=dict(
            categoryorder="array",
            categoryarray=ordered_month_labels,
            tickangle=-30,
            tickfont=dict(size=11),
        ),
        legend=dict(orientation="h", yanchor="top", y=-0.2, font=dict(size=9)),
        margin=dict(t=40, b=180, l=60, r=60),
    )
    fig_ev.update_yaxes(title_text="TTV (€)", secondary_y=False)
    fig_ev.update_yaxes(title_text="Bookings", secondary_y=True, showgrid=False)
    st.plotly_chart(fig_ev, use_container_width=True)

    # ── Heatmaps par mois ──
    st.subheader("🗓️ Heatmap mensuelle")
    hm_col1, hm_col2 = st.columns(2)

    for hm_col, hm_metric, hm_label, hm_color in [
        (hm_col1, "TTV",      "TTV (€)",  "Blues"),
        (hm_col2, "Bookings", "Bookings", "Oranges"),
    ]:
        with hm_col:
            # Utilise vp_url (sans domaine) — exclut les lignes sans URL réelle
            _df_hm_src = df_filtered[df_filtered["metric"] == hm_metric].copy()
            _df_hm_src = _df_hm_src[_df_hm_src["vp_url"].notna()].copy()
            _df_hm_src["_url_display"] = _df_hm_src["vp_url"].str.replace(
                "https://www.voyage-prive.com/", "", regex=False
            )
            df_hm = (
                _df_hm_src
                .groupby(["_url_display", "month"])["value"].sum()
                .reset_index()
            )
            df_hm_piv = df_hm.pivot(index="_url_display", columns="month", values="value").fillna(0)
            # Trier par total décroissant, garder top_n
            df_hm_piv["_total"] = df_hm_piv.sum(axis=1)
            df_hm_piv = df_hm_piv.sort_values("_total", ascending=False).head(top_n).drop(columns="_total")
            # Renommer les colonnes en noms de mois
            df_hm_piv.columns = [MONTH_LABELS.get(c, str(c)) for c in df_hm_piv.columns]

            fig_hm = px.imshow(
                df_hm_piv,
                labels=dict(x="Mois", y="URL", color=hm_label),
                color_continuous_scale=hm_color,
                aspect="auto",
                title=f"Heatmap {hm_label} · Top {top_n} URLs",
                text_auto=".3s",
            )
            fig_hm.update_layout(
                height=max(400, top_n * 30),
                margin=dict(l=10, r=10, t=50, b=10),
                coloraxis_showscale=False,
                xaxis=dict(side="top"),
            )
            fig_hm.update_traces(textfont_size=9)
            st.plotly_chart(fig_hm, use_container_width=True)

# ── Vue par mois ──
with tab2:
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
with tab3:
  _dest_cats = df_filtered[df_filtered["destination"].notna()].copy() if "destination" in df_filtered.columns else pd.DataFrame()
  if _dest_cats.empty:
    st.info("Active la catégorisation pour voir les données par destination.")
  else:
    _ttv_dest = _dest_cats[_dest_cats["metric"]=="TTV"].groupby("destination")["value"].sum().reset_index().sort_values("value", ascending=False)
    _bkg_dest = _dest_cats[_dest_cats["metric"]=="Bookings"].groupby("destination")["value"].sum().reset_index().sort_values("value", ascending=False)
    _tpl_dest = _dest_cats[_dest_cats["metric"]=="TTV per lead Net"].groupby("destination")["value"].mean().reset_index().sort_values("value", ascending=False)
    _col1, _col2, _col3 = st.columns(3)
    with _col1:
      fig_dest_ttv = px.bar(_ttv_dest, x="value", y="destination", orientation="h",
        title="TTV (€) par destination", labels={"value":"TTV (€)","destination":"Destination"},
        color="value", color_continuous_scale="Blues", height=max(400, len(_ttv_dest)*28))
      fig_dest_ttv.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
      st.plotly_chart(fig_dest_ttv, use_container_width=True)
    with _col2:
      fig_dest_bkg = px.bar(_bkg_dest, x="value", y="destination", orientation="h",
        title="Bookings par destination", labels={"value":"Bookings","destination":"Destination"},
        color="value", color_continuous_scale="Oranges", height=max(400, len(_bkg_dest)*28))
      fig_dest_bkg.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
      st.plotly_chart(fig_dest_bkg, use_container_width=True)
    with _col3:
      fig_dest_tpl = px.bar(_tpl_dest, x="value", y="destination", orientation="h",
        title="TTV / Lead (€) par destination", labels={"value":"TTV/Lead (€)","destination":"Destination"},
        color="value", color_continuous_scale="Greens", height=max(400, len(_tpl_dest)*28))
      fig_dest_tpl.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
      st.plotly_chart(fig_dest_tpl, use_container_width=True)
    # Évolution mensuelle par destination
    st.subheader("📈 Évolution mensuelle par destination")
    ev_dest_mode = st.radio("Métrique", ["TTV (€)", "Bookings"], horizontal=True, key="ev_dest_mode")
    _metric = "TTV" if ev_dest_mode == "TTV (€)" else "Bookings"
    _ev_dest = _dest_cats[_dest_cats["metric"]==_metric].groupby(["month","month_label","destination"])["value"].sum().reset_index()
    fig_ev_dest = px.bar(_ev_dest, x="month_label", y="value", color="destination", barmode="stack",
      labels={"value": ev_dest_mode, "month_label":"Mois", "destination":"Destination"},
      category_orders={"month_label": ordered_month_labels}, height=500)
    fig_ev_dest.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, font=dict(size=9)), margin=dict(b=180))
    st.plotly_chart(fig_ev_dest, use_container_width=True)

with tab4:
  _type_cats = df_filtered[df_filtered["type_page"].notna()].copy() if "type_page" in df_filtered.columns else pd.DataFrame()
  if _type_cats.empty:
    st.info("Active la catégorisation pour voir les données par type de page.")
  else:
    _hide_autre = st.checkbox("Masquer 'Autre'", value=True, key="hide_autre_tab4")
    if _hide_autre:
        _type_cats = _type_cats[_type_cats["type_page"] != "Autre"]
    _ttv_type = _type_cats[_type_cats["metric"]=="TTV"].groupby("type_page")["value"].sum().reset_index().sort_values("value", ascending=False)
    _bkg_type = _type_cats[_type_cats["metric"]=="Bookings"].groupby("type_page")["value"].sum().reset_index().sort_values("value", ascending=False)
    _tpl_type = _type_cats[_type_cats["metric"]=="TTV per lead Net"].groupby("type_page")["value"].mean().reset_index().sort_values("value", ascending=False)
    _col1t, _col2t, _col3t = st.columns(3)
    with _col1t:
      fig_type_ttv = px.bar(_ttv_type, x="value", y="type_page", orientation="h",
        title="TTV (€) par type de page", labels={"value":"TTV (€)","type_page":"Type"},
        color="value", color_continuous_scale="Blues", height=max(400, len(_ttv_type)*40))
      fig_type_ttv.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
      st.plotly_chart(fig_type_ttv, use_container_width=True)
    with _col2t:
      fig_type_bkg = px.bar(_bkg_type, x="value", y="type_page", orientation="h",
        title="Bookings par type de page", labels={"value":"Bookings","type_page":"Type"},
        color="value", color_continuous_scale="Oranges", height=max(400, len(_bkg_type)*40))
      fig_type_bkg.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
      st.plotly_chart(fig_type_bkg, use_container_width=True)
    with _col3t:
      fig_type_tpl = px.bar(_tpl_type, x="value", y="type_page", orientation="h",
        title="TTV / Lead (€) par type de page", labels={"value":"TTV/Lead (€)","type_page":"Type"},
        color="value", color_continuous_scale="Greens", height=max(400, len(_tpl_type)*40))
      fig_type_tpl.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
      st.plotly_chart(fig_type_tpl, use_container_width=True)
    # Évolution mensuelle par type
    st.subheader("📈 Évolution mensuelle par type de page")
    ev_type_mode = st.radio("Métrique", ["TTV (€)", "Bookings"], horizontal=True, key="ev_type_mode")
    _metric_t = "TTV" if ev_type_mode == "TTV (€)" else "Bookings"
    _ev_type = _type_cats[_type_cats["metric"]==_metric_t].groupby(["month","month_label","type_page"])["value"].sum().reset_index()
    fig_ev_type = px.bar(_ev_type, x="month_label", y="value", color="type_page", barmode="stack",
      labels={"value": ev_type_mode, "month_label":"Mois", "type_page":"Type"},
      category_orders={"month_label": ordered_month_labels}, height=500)
    fig_ev_type.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, font=dict(size=9)), margin=dict(b=180))
    st.plotly_chart(fig_ev_type, use_container_width=True)

# ── Tableau récap (hors onglets, toujours visible) ──
st.divider()
st.subheader("📊 Tableau récap · TTV + Bookings (toute la période sélectionnée)")

# Merge catégories dans le récap AVANT le head(top_n)
df_recap = df_merged_global.sort_values("TTV", ascending=False).copy()
df_recap["TTV / Booking (€)"] = (df_recap["TTV"] / df_recap["Bookings"].replace(0, float("nan"))).round(0)

if "type_page" in df_filtered.columns:
    df_cats = df_filtered[["vp_url", "type_page", "destination"]].drop_duplicates("vp_url")
    df_recap = df_recap.merge(df_cats, on="vp_url", how="left")

# Appliquer top_n après le merge
df_recap_display = df_recap.head(top_n).copy()
df_recap_display["TTV (€)"]           = df_recap_display["TTV"].map(lambda x: f"{x:,.0f}")
df_recap_display["Bookings"]          = df_recap_display["Bookings"].map(lambda x: f"{int(x):,}")
df_recap_display["TTV / Booking (€)"] = df_recap_display["TTV / Booking (€)"].map(
    lambda x: f"{x:,.0f}" if pd.notna(x) else "-"
)

df_recap_display = df_recap_display.rename(columns={
    "campaign_id": "ID", "campaign_name": "Nom campagne", "vp_url": "URL VP"
})
extra_cols = []
if "type_page" in df_recap_display.columns:
    df_recap_display = df_recap_display.rename(columns={"type_page": "Type", "destination": "Destination"})
    extra_cols = ["Type", "Destination"]
df_recap_display = df_recap_display[["ID", "Nom campagne", "URL VP"] + extra_cols + ["TTV (€)", "Bookings", "TTV / Booking (€)"]]

st.caption(f"Top {top_n} pages triées par TTV décroissant")
st.dataframe(df_recap_display, use_container_width=True, hide_index=True)

col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    _csv_cols = ["campaign_id", "campaign_name", "vp_url", "TTV", "Bookings", "TTV / Booking (€)"]
    if "type_page" in df_recap.columns:
        _csv_cols += ["type_page", "destination"]
    csv = df_recap[_csv_cols].rename(columns={"type_page": "Schéma de recherche", "destination": "Destination"}).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Exporter CSV",
        data=csv, file_name="vp_seo_recap.csv", mime="text/csv"
    )

with col_dl2:
    import io
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    def build_excel(df_recap_raw, df_ttv_agg, df_bkg_agg, df_tpl_agg, ordered_month_labels, MONTH_LABELS):
        wb = Workbook()
        _blue  = "1d6fa4"
        _green = "1a7a4a"
        _ora   = "f4a840"

        def style_header(ws, color):
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor=color)
                cell.alignment = Alignment(horizontal="center")

        def autowidth(ws, pad=4):
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = max(len(str(c.value or "")) for c in col) + pad

        # ── Onglet 1 : URLs ──
        ws1 = wb.active
        ws1.title = "URLs"
        has_cats = "type_page" in df_recap_raw.columns
        headers = ["ID", "Nom campagne", "URL VP"] + (["Schéma de recherche", "Destination"] if has_cats else []) + ["TTV (€)", "Bookings", "TTV / Booking (€)"]
        ws1.append(headers)
        style_header(ws1, _blue)
        for _, row in df_recap_raw.iterrows():
            tvb = row["TTV"] / row["Bookings"] if row["Bookings"] > 0 else None
            base = [int(row["campaign_id"]), row["campaign_name"], row["vp_url"]]
            cats = [row.get("type_page", ""), row.get("destination", "")] if has_cats else []
            ws1.append(base + cats + [round(row["TTV"], 0), int(row["Bookings"]), round(tvb, 0) if tvb else ""])
        autowidth(ws1)

        # ── Onglet 2 : Récap Schéma ──
        if has_cats and "type_page" in df_recap_raw.columns:
            ws_schema = wb.create_sheet("Récap Schéma")
            ws_schema.append(["Schéma de recherche", "TTV (€)", "Bookings", "TTV / Booking (€)", "TTV / Lead (€)"])
            style_header(ws_schema, _blue)
            _schema_ttv = df_recap_raw.groupby("type_page")["TTV"].sum()
            _schema_bkg = df_recap_raw.groupby("type_page")["Bookings"].sum()
            # TTV/lead from tpl_agg
            _tpl_by_schema = {}
            if not df_tpl_agg.empty and "type_page" in df_filtered.columns:
                _tpl_merged = df_tpl_agg.merge(df_filtered[["campaign_id","type_page"]].drop_duplicates(), on="campaign_id", how="left")
                _tpl_by_schema = _tpl_merged.groupby("type_page")["value"].mean().to_dict()
            for schema in _schema_ttv.index:
                ttv = round(_schema_ttv[schema], 0)
                bkg = int(_schema_bkg.get(schema, 0))
                tvb = round(ttv / bkg, 0) if bkg > 0 else ""
                tpl = round(_tpl_by_schema.get(schema, 0), 2) if schema in _tpl_by_schema else ""
                ws_schema.append([schema, ttv, bkg, tvb, tpl])
            autowidth(ws_schema)

            # ── Onglet 3 : Récap Destination ──
            ws_dest = wb.create_sheet("Récap Destination")
            ws_dest.append(["Destination", "TTV (€)", "Bookings", "TTV / Booking (€)", "TTV / Lead (€)"])
            style_header(ws_dest, _green)
            _dest_ttv = df_recap_raw.groupby("destination")["TTV"].sum()
            _dest_bkg = df_recap_raw.groupby("destination")["Bookings"].sum()
            _tpl_by_dest = {}
            if not df_tpl_agg.empty and "destination" in df_filtered.columns:
                _tpl_dest_m = df_tpl_agg.merge(df_filtered[["campaign_id","destination"]].drop_duplicates(), on="campaign_id", how="left")
                _tpl_by_dest = _tpl_dest_m.groupby("destination")["value"].mean().to_dict()
            for dest in _dest_ttv.index:
                ttv = round(_dest_ttv[dest], 0)
                bkg = int(_dest_bkg.get(dest, 0))
                tvb = round(ttv / bkg, 0) if bkg > 0 else ""
                tpl = round(_tpl_by_dest.get(dest, 0), 2) if dest in _tpl_by_dest else ""
                ws_dest.append([dest, ttv, bkg, tvb, tpl])
            autowidth(ws_dest)

        # ── Onglet 4 : TTV par mois ──
        ws2 = wb.create_sheet("TTV par mois")
        month_nums = sorted(set(df_ttv_agg["month"].tolist()))
        month_cols = [MONTH_LABELS[m] for m in month_nums]
        ws2.append(["URL"] + month_cols + ["TOTAL"])
        style_header(ws2, _blue)
        df_ttv_piv = df_ttv_agg.groupby(["vp_url", "month"])["value"].sum().reset_index()
        df_ttv_piv = df_ttv_piv.pivot(index="vp_url", columns="month", values="value").fillna(0)
        df_ttv_piv["TOTAL"] = df_ttv_piv.sum(axis=1)
        df_ttv_piv = df_ttv_piv.sort_values("TOTAL", ascending=False)
        for url, row2 in df_ttv_piv.iterrows():
            ws2.append([url] + [round(row2.get(m, 0), 0) for m in month_nums] + [round(row2["TOTAL"], 0)])
        autowidth(ws2)

        # ── Onglet 5 : Bookings par mois ──
        ws3 = wb.create_sheet("Bookings par mois")
        ws3.append(["URL"] + month_cols + ["TOTAL"])
        style_header(ws3, _ora)
        df_bkg_piv = df_bkg_agg.groupby(["vp_url", "month"])["value"].sum().reset_index()
        df_bkg_piv = df_bkg_piv.pivot(index="vp_url", columns="month", values="value").fillna(0)
        df_bkg_piv["TOTAL"] = df_bkg_piv.sum(axis=1)
        df_bkg_piv = df_bkg_piv.sort_values("TOTAL", ascending=False)
        for url, row3 in df_bkg_piv.iterrows():
            ws3.append([url] + [int(row3.get(m, 0)) for m in month_nums] + [int(row3["TOTAL"])])
        autowidth(ws3)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.read()

    xls_data = build_excel(df_recap, df_ttv_agg, df_bkg_agg, df_tpl_agg, ordered_month_labels, MONTH_LABELS)
    st.download_button(
        label="⬇️ Exporter Excel (5 onglets)",
        data=xls_data,
        file_name="vp_seo_recap.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
