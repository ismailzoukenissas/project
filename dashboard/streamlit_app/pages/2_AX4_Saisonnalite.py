import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb
import numpy as np

st.set_page_config(page_title="AX4 — Saisonnalité", page_icon="📅", layout="wide")

st.title("📅 AX4 — Saisonnalité, Cycles et Patterns Temporels")

BASE = r"C:\Users\izouk\OneDrive\Desktop\projet aeroport\airline_performance"

@st.cache_data
def load_monthly():
    con = duckdb.connect()
    return con.execute(f"""
        SELECT * FROM read_parquet('{BASE}/data/gold/mart_otp_monthly.parquet')
    """).df()

@st.cache_data
def load_seasonality():
    con = duckdb.connect()
    return con.execute(f"""
        SELECT * FROM read_parquet('{BASE}/data/gold/mart_seasonality.parquet')
    """).df()

df_monthly    = load_monthly()
df_seasonality = load_seasonality()

# ─── KPIs ────────────────────────────────────────────────────
st.markdown("### 📊 Indicateurs clés")
col1, col2, col3, col4 = st.columns(4)

hourly = df_seasonality.groupby('dep_hour')['otp_pct'].mean()
best_hour = hourly.idxmax()
worst_hour = hourly.idxmin()

with col1:
    st.metric("OTP moyen global", f"{df_monthly['otp_pct'].mean():.1f}%")
with col2:
    st.metric("Meilleur créneau",
              f"{int(best_hour)}h",
              delta=f"{hourly[best_hour]:.1f}%")
with col3:
    st.metric("Pire créneau",
              f"{int(worst_hour)}h",
              delta=f"-{hourly[best_hour]-hourly[worst_hour]:.1f}pts")
with col4:
    dow = df_seasonality.groupby('DAY_OF_WEEK')['otp_pct'].mean()
    st.metric("Meilleur jour", "Samedi", delta=f"{dow.max():.1f}%")

st.markdown("---")

# ─── Graphique 1 : Heatmap ───────────────────────────────────
st.markdown("### 🗓️ Heatmap OTP — Patterns mensuels sur 10 ans")

pivot = df_monthly.groupby(['YEAR','MONTH'])['otp_pct'].mean().reset_index()
pivot_matrix = pivot.pivot(index='YEAR', columns='MONTH', values='otp_pct')

mois_labels = ['Jan','Fév','Mar','Avr','Mai','Jun',
                'Jul','Aoû','Sep','Oct','Nov','Déc']
pivot_matrix.columns = mois_labels

fig1 = px.imshow(
    pivot_matrix,
    color_continuous_scale='RdYlGn',
    aspect='auto',
    title='OTP moyen par année et mois — Vert=Bon, Rouge=Mauvais',
    labels=dict(x='Mois', y='Année', color='OTP %'),
    zmin=pivot_matrix.values.min(),
    zmax=pivot_matrix.values.max()
)
fig1.update_layout(height=400)
st.plotly_chart(fig1, use_container_width=True)

st.info("""
**Lecture :** Vert = bon OTP, Rouge = mauvais OTP.
Janvier-Février (hiver) et Juin-Juillet (été) sont les mois difficiles.
Septembre-Novembre sont les meilleurs mois de l'année.
Le pattern se répète identiquement chaque année sur 10 ans.
""")

st.markdown("---")

# ─── Graphique 2 : OTP par heure ─────────────────────────────
st.markdown("### ⏰ OTP par heure de départ")

hourly_df = df_seasonality.groupby('dep_hour')['otp_pct'].mean().reset_index()
hourly_df = hourly_df.dropna().sort_values('dep_hour')
hourly_df = hourly_df[hourly_df['dep_hour'].between(0,23)]

fig2 = px.bar(
    hourly_df,
    x='dep_hour',
    y='otp_pct',
    title='OTP moyen par heure de départ (0h-23h)',
    labels={'dep_hour':'Heure de départ','otp_pct':'OTP %'},
    color='otp_pct',
    color_continuous_scale='RdYlGn',
    range_color=[hourly_df['otp_pct'].min(), hourly_df['otp_pct'].max()]
)
fig2.update_layout(height=400, coloraxis_showscale=False)
st.plotly_chart(fig2, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Meilleur créneau",
              f"{int(hourly_df.loc[hourly_df['otp_pct'].idxmax(),'dep_hour'])}h",
              delta=f"{hourly_df['otp_pct'].max():.1f}%")
with col2:
    st.metric("Pire créneau (hors 0-4h)",
              f"{int(hourly_df[hourly_df['dep_hour']>=5].loc[hourly_df[hourly_df['dep_hour']>=5]['otp_pct'].idxmin(),'dep_hour'])}h",
              delta=f"{hourly_df[hourly_df['dep_hour']>=5]['otp_pct'].min():.1f}%")
with col3:
    best = hourly_df[hourly_df['dep_hour']>=5]['otp_pct'].max()
    worst = hourly_df[hourly_df['dep_hour']>=5]['otp_pct'].min()
    st.metric("Écart meilleur/pire", f"{best-worst:.1f} pts")

st.markdown("---")

# ─── Graphique 3 : OTP par jour ──────────────────────────────
st.markdown("### 📆 OTP par jour de la semaine")

dow_map = {0:'Dim',1:'Lun',2:'Mar',3:'Mer',4:'Jeu',5:'Ven',6:'Sam'}
daily = df_seasonality.groupby('DAY_OF_WEEK')['otp_pct'].mean().reset_index()
daily['jour'] = daily['DAY_OF_WEEK'].map(dow_map)
daily = daily.dropna(subset=['jour'])

fig3 = px.bar(
    daily,
    x='jour',
    y='otp_pct',
    title='OTP moyen par jour de la semaine',
    labels={'jour':'Jour','otp_pct':'OTP %'},
    color='otp_pct',
    color_continuous_scale='RdYlGn',
    category_orders={'jour':['Dim','Lun','Mar','Mer','Jeu','Ven','Sam']},
    range_color=[daily['otp_pct'].min()-1, daily['otp_pct'].max()+1]
)
fig3.update_layout(height=400, coloraxis_showscale=False,
                   yaxis_range=[78,86])
st.plotly_chart(fig3, use_container_width=True)

st.info("""
**Lecture :** Le Samedi est le meilleur jour (~84%) car le trafic
business est absent. Le Jeudi et Vendredi sont les pires (~80%)
car le trafic business atteint son pic en fin de semaine.
""")

st.markdown("---")

# ─── Graphique 4 : Weather vs NAS ────────────────────────────
st.markdown("### 🌦️ Saisonnalité des causes — Weather vs NAS")

mois_map = {1:'Jan',2:'Fév',3:'Mar',4:'Avr',5:'Mai',6:'Jun',
            7:'Jul',8:'Aoû',9:'Sep',10:'Oct',11:'Nov',12:'Déc'}

causes = df_seasonality.groupby('MONTH')[['pct_weather','pct_nas']].mean().reset_index()
causes['mois_label'] = causes['MONTH'].map(mois_map)

fig4 = go.Figure()
fig4.add_bar(
    x=causes['mois_label'],
    y=causes['pct_nas'],
    name='NAS (saturation ATC)',
    marker_color='#FFD700'
)
fig4.add_bar(
    x=causes['mois_label'],
    y=causes['pct_weather'],
    name='Weather (météo extrême)',
    marker_color='#2196F3'
)

fig4.update_layout(
    barmode='group',
    title='Part des retards Weather vs NAS par mois',
    xaxis_title='Mois',
    yaxis_title='% du total retard',
    height=400,
    xaxis={'categoryorder':'array',
           'categoryarray':['Jan','Fév','Mar','Avr','Mai','Jun',
                            'Jul','Aoû','Sep','Oct','Nov','Déc']}
)
st.plotly_chart(fig4, use_container_width=True)

st.info("""
**Lecture :** Le NAS (jaune) domine toute l'année — la saturation ATC
est la première cause de retard. Le Weather (bleu) pic en Janvier-Février.
Le NAS atteint son maximum en Octobre (~25%).
""")

st.markdown("---")

# ─── Graphique 5 : Tendance long terme ───────────────────────
st.markdown("### 📈 Tendance long terme OTP sectoriel")

trend = df_monthly.groupby('YEAR')['otp_pct'].mean().reset_index()

z = np.polyfit(trend['YEAR'], trend['otp_pct'], 1)
p = np.poly1d(z)
trend['regression'] = p(trend['YEAR'])

fig5 = go.Figure()
fig5.add_scatter(
    x=trend['YEAR'], y=trend['otp_pct'],
    mode='lines+markers',
    name='OTP réel',
    line=dict(color='#1f77b4', width=2),
    marker=dict(size=8)
)
fig5.add_scatter(
    x=trend['YEAR'], y=trend['regression'],
    mode='lines',
    name='Tendance linéaire',
    line=dict(color='red', dash='dash', width=1.5)
)

contexte = {
    2009:'Récession',
    2012:'Pic sectoriel',
    2013:'Fusion AA+US',
    2014:'Saturation hubs'
}
for annee, label in contexte.items():
    otp_val = trend[trend['YEAR']==annee]['otp_pct'].values
    if len(otp_val) > 0:
        fig5.add_annotation(
            x=annee, y=otp_val[0],
            text=label,
            showarrow=True,
            arrowhead=2,
            ax=0, ay=-35,
            font=dict(size=10, color='gray')
        )

fig5.update_layout(
    title='Tendance long terme OTP sectoriel 2009-2018',
    xaxis_title='Année',
    yaxis_title='OTP %',
    height=450,
    yaxis_range=[78,86],
    hovermode='x unified'
)
st.plotly_chart(fig5, use_container_width=True)

st.info("""
**Lecture :** La droite rouge montre une légère tendance négative
(-0.1 pt/an). Le pic de 2012 (~84%) est le meilleur score de la décennie.
La saturation croissante des hubs compense les gains opérationnels.
""")