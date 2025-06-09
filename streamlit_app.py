import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

st.set_page_config(layout="wide")
st.title("Gram Staining Reveals Patterns in Effectiveness of Antibiotics")
st.subheader("Penicillin is narrow-spectrum for Gram-positive, Streptomycin is variable for both, Neomycin is more broadly effective.")
st.markdown("""
This visualization displays effectiveness of different antibiotics at inhibiting bacterial growth.
Lower MIC (Minimum Inhibitory Concentration) demonstrates a more effective antibiotic in that case.
**In the following visualization:**
- Color represents the antibiotic.
- Shape represents Gram staining (positive or negative).
- X-axis shows MIC values on a log scale (log since values span multiple maginitudes, from 0.001 to 870).
""")

# Load the JSON dataset
data = pd.read_json("burtin.json")

# Reshape to long format
df_long = data.melt(
    id_vars=["Bacteria", "Gram_Staining", "Genus"],
    value_vars=["Penicillin", "Streptomycin", "Neomycin"],
    var_name="Antibiotic",
    value_name="MIC"
)

# Handle log scale, there are different orders of magnitude in our MIC values
df_long["MIC"] = df_long["MIC"].replace(0, np.nan)  #So we don't get log(0)
df_long["log_MIC"] = np.log10(df_long["MIC"])

# Sidebar
with st.sidebar:
    st.header("Filters")
    antibiotics = st.multiselect(
        "Antibiotic(s):",
        options=df_long["Antibiotic"].unique(),
        default=list(df_long["Antibiotic"].unique())
    )

    gram_types = st.multiselect(
        "Gram Staining:",
        options=df_long["Gram_Staining"].unique(),
        default=list(df_long["Gram_Staining"].unique())
    )

# Filter
filtered = df_long[
    (df_long["Antibiotic"].isin(antibiotics)) &
    (df_long["Gram_Staining"].isin(gram_types))
]

# The dot plot
dotplot = alt.Chart(filtered).mark_point(size=100).encode(
    x=alt.X("log_MIC", title="Log(MIC) Lower is More Effective", scale=alt.Scale(type="linear")),
    y=alt.Y("Bacteria:N", title="Type of Bacteria", sort=alt.EncodingSortField("MIC", op="mean", order="descending")),
    color=alt.Color("Antibiotic", title="Antibiotic"),
    shape=alt.Shape("Gram_Staining", title="Gram Staining"),
    tooltip=["Bacteria", "Antibiotic", "MIC", "Gram_Staining", "Genus"]
).properties(
    width=850,
    height=700,
    title="Comparative Effectiveness of Antibiotics by Bacteria"
)

st.altair_chart(dotplot, use_container_width=True)

with st.expander("Insight and Exploration Regarding Antibiotic Effectiveness", expanded=True):
    if len(antibiotics) == 0:
        st.markdown("""
        **NO ANTIBIOTICS SELECTED**
        Please select one or more from the sidebar to explore their effectiveness against different bacteria.
        """)
    elif len(antibiotics) == 1:
        ab = antibiotics[0]
        if ab == "Penicillin":
            st.markdown("""
            Penicillin is highly effective against Gram-positive bacteria, showing very low MIC values (as low as 0.001).  
            It is largely ineffective against Gram-negative bacteria like E. coli, Klebsiella, and Pseudomonas, demonstrated by MIC >100.
            """)
        elif ab == "Streptomycin":
            st.markdown("""
            Streptomycin performs moderately well across both Gram-positive and Gram-negative bacteria, showing variability.  
            It is effective against some Gram-negative strains like E. coli and Salmonella, but seems to be less effective against 
            Gram-positive species such as Streptococcus hemolyticus.
            """)
        elif ab == "Neomycin":
            st.markdown("""
            Neomycin shows consistent low MICs across both Gram-positive and Gram-negative bacteria, and is especially effective against Staphylococcus aureus and Proteus vulgaris.  
            It is definitely the most balanced/universally effective of the three drugs in this dataset.
            """)
    else:
        st.markdown("""
        You are currently viewing multiple antibiotics at once.  
        To explore more tailored insights, try filtering by one antibiotic at a time in the sidebar to see patterns of individual antibiotics, or stay on this screen to compare or view antibiotics as a whole.
        """)