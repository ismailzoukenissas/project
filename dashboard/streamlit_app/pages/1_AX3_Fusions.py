import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb

st.set_page_config(page_title="AX3 — Fusions", page_icon="🔀", layout="wide")

st.title("🔀 AX3 — Impact des Fusions et Consolidation Sectorielle")

# ─── Chargement des données ───────────────────────────────────

@st.cache_data
def load_merger():
    con = duckdb.connect()
    # Utilisation du chemin relatif (sans {BASE})
    return con.execute("""
        SELECT * FROM read_parquet('data/gold/mart_merger_impact.parquet')
    """).df()

@st.cache_data
def load_parquet():
    con = duckdb.connect()
    # Lecture directe du fichier agrégé généré à l'étape 1
    return con.execute("""
        SELECT * FROM read_parquet('data/gold/mart_timeline.parquet')
    """).df()

df_merger  = load_merger()
df_timeline = load_parquet()

# ─── Filtres sidebar ─────────────────────────────────────────
st.sidebar.header("Filtres AX3")

carriers_fusion = ['AA','CO','FL','UA','US','WN']
carriers_sel = st.sidebar.multiselect(
    "Carriers à afficher",
    options=carriers_fusion,
    default=carriers_fusion
)

# ─── KPIs ────────────────────────────────────────────────────
st.markdown("### 📊 Indicateurs clés")
col1, col2, col3, col4 = st.columns(4)

df_post = df_merger[df_merger['fusion_periode']=='post']
df_pre  = df_merger[df_merger['fusion_periode']=='pre']

with col1:
    st.metric("OTP moyen PRE-fusion",
              f"{df_pre['otp_pct'].mean():.1f}%")
with col2:
    st.metric("OTP moyen DURING-fusion",
              f"{df_merger[df_merger['fusion_periode']=='during']['otp_pct'].mean():.1f}%",
              delta=f"{df_merger[df_merger['fusion_periode']=='during']['otp_pct'].mean() - df_pre['otp_pct'].mean():.1f}%")
with col3:
    st.metric("OTP moyen POST-fusion",
              f"{df_post['otp_pct'].mean():.1f}%",
              delta=f"{df_post['otp_pct'].mean() - df_pre['otp_pct'].mean():.1f}%")
with col4:
    st.metric("Carriers fusionnés analysés", "6")

st.markdown("---")

# ─── Graphique 1 : OTP Timeline ──────────────────────────────
st.markdown("### 📈 OTP Timeline — Évolution sur 10 ans")

df_line = df_timeline[df_timeline['OP_UNIQUE_CARRIER'].isin(carriers_sel)]

fig1 = px.line(
    df_line,
    x='YEAR',
    y='otp_pct',
    color='OP_UNIQUE_CARRIER',
    markers=True,
    title='OTP annuel par carrier fusionné (2009-2018)',
    labels={'otp_pct':'OTP %', 'YEAR':'Année', 'OP_UNIQUE_CARRIER':'Carrier'},
    color_discrete_map={
        'AA':'#1f77b4','CO':'#ff7f0e','FL':'#d62728',
        'UA':'#2ca02c','US':'#9467bd','WN':'#FFD700'
    }
)

# Annotations fusions
fusions = [(2010,'UA+CO'), (2011,'WN+FL'), (2013,'AA+US')]
for annee, label in fusions:
    fig1.add_vline(x=annee, line_dash='dash', line_color='gray',
                   annotation_text=label, annotation_position='top')

fig1.update_layout(height=450, hovermode='x unified')
st.plotly_chart(fig1, use_container_width=True)

st.info("""
**Lecture :** Les lignes pointillées grises marquent les dates de fusion.
On observe que WN (Southwest) touche son minimum à ~75% en 2014,
un an après la fusion AA+US Airways qui a perturbé tout le secteur.
""")

st.markdown("---")

# ─── Graphique 2 : Pre During Post ───────────────────────────
st.markdown("### 📊 OTP avant, pendant et après fusion")

df_pdp = df_merger[df_merger['carrier_key'].isin(carriers_sel)].copy()

ordre = ['pre','during','post']
df_pdp['fusion_periode'] = pd.Categorical(
    df_pdp['fusion_periode'], categories=ordre, ordered=True
)
df_avg = df_pdp.groupby(['carrier_key','fusion_periode'])['otp_pct'].mean().reset_index()
df_avg = df_avg.sort_values('fusion_periode')

fig2 = px.bar(
    df_avg,
    x='carrier_key',
    y='otp_pct',
    color='fusion_periode',
    barmode='group',
    title='OTP moyen — avant / pendant / après fusion',
    labels={'otp_pct':'OTP %','carrier_key':'Carrier','fusion_periode':'Période'},
    color_discrete_map={'pre':'#2196F3','during':'#FF5722','post':'#4CAF50'},
    category_orders={'fusion_periode':['pre','during','post']}
)
fig2.update_layout(height=400, yaxis_range=[75,88])
st.plotly_chart(fig2, use_container_width=True)

st.info("""
**Lecture :** AA (American) affiche 79.3% pendant la période DURING
contre 80% en PRE — dégradation limitée mais confirmée.
FL (AirTran) montre une amélioration pendant l'intégration dans Southwest.
""")

st.markdown("---")

# ─── Graphique 3 : Carriers actifs ───────────────────────────
st.markdown("### 📉 Consolidation — Nombre de carriers actifs par année")

df_actifs = df_timeline.groupby('YEAR')['OP_UNIQUE_CARRIER'].nunique().reset_index()
df_actifs.columns = ['YEAR','nb_carriers']

fig3 = px.bar(
    df_actifs,
    x='nb_carriers',
    y='YEAR',
    orientation='h',
    title='Nombre de carriers fusionnés actifs par année',
    labels={'nb_carriers':'Nombre de carriers','YEAR':'Année'},
    color='nb_carriers',
    color_continuous_scale='Blues'
)
fig3.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig3, use_container_width=True)

st.info("""
**Lecture :** De 6 carriers actifs en 2009-2011 à seulement 3 en 2016-2018.
Chaque marche descendante correspond à une fusion finalisée.
""")

st.markdown("---")

# ─── Graphique 4 : Effet Domino ──────────────────────────────
st.markdown("### 🌊 Effet Domino — LATE\_AIRCRAFT par carrier")

df_domino = df_merger[df_merger['carrier_key'].isin(carriers_sel)].copy()
df_domino_year = df_domino.groupby(['carrier_key','YEAR'])['pct_late_aircraft'].mean().reset_index()

fig4 = px.line(
    df_domino_year,
    x='YEAR',
    y='pct_late_aircraft',
    color='carrier_key',
    markers=True,
    title="Part des retards LATE_AIRCRAFT par carrier (2009-2018)",
    labels={'pct_late_aircraft':'% Late Aircraft','YEAR':'Année','carrier_key':'Carrier'},
    color_discrete_map={
        'AA':'#1f77b4','CO':'#ff7f0e','FL':'#d62728',
        'UA':'#2ca02c','US':'#9467bd','WN':'#FFD700'
    }
)

for annee, label in fusions:
    fig4.add_vline(x=annee, line_dash='dot', line_color='gray',
                   annotation_text=label)

fig4.update_layout(height=400)
st.plotly_chart(fig4, use_container_width=True)

st.info("""
**Lecture :** WN (Southwest, jaune) maintient structurellement ~50-55%
d'effet domino sur toute la période — son modèle point-to-point dense
amplifie les cascades de retards. AA (bleu) monte de 32% à 42% pendant
sa période de faillite puis redescend après la fusion.
""")
