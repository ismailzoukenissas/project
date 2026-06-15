import streamlit as st

st.set_page_config(
    page_title="Performance Aériennes USA 2009-2018",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("✈️ Performance Opérationnelle des Compagnies Aériennes Américaines")
st.markdown("**Période analysée :** 2009-2018 | **Volume :** ~65 millions de vols domestiques")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total vols analysés", value="65M+")
with col2:
    st.metric(label="Période", value="2009-2018")
with col3:
    st.metric(label="Compagnies", value="23 carriers")

st.markdown("---")

st.markdown("""
### Navigation
Utilisez le menu de gauche pour naviguer entre les axes :
- **AX3** — Impact des Fusions et Consolidation Sectorielle
- **AX4** — Saisonnalité, Cycles et Patterns Temporels
""")