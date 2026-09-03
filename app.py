import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ---------------------------------------------------------
# Page Configuration & Header
# ---------------------------------------------------------
st.set_page_config(
    page_title="Iodine Partition Coefficient Assistant",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Iodine Partition Coefficient ($K$) Assistant")
st.write("Determine the partition coefficient of Iodine between organic and aqueous phases using 4-bottle titration data.")

st.sidebar.header("⚙️ Experimental Parameters")

# Sidebar inputs for lab constants
N_thio = st.sidebar.number_input(
    "Normality of Na2S2O3 (N)", 
    min_value=0.001, max_value=1.0, value=0.01, step=0.001, format="%.3f"
)
V_aq_aliquot = st.sidebar.number_input(
    "Aqueous Aliquot Volume (mL)", 
    min_value=1.0, max_value=100.0, value=20.0, step=1.0
)
V_org_aliquot = st.sidebar.number_input(
    "Organic Aliquot Volume (mL)", 
    min_value=1.0, max_value=100.0, value=5.0, step=1.0
)

st.divider()

# ---------------------------------------------------------
# Student Data Input UI (4 Bottles)
# ---------------------------------------------------------
st.subheader("📋 Enter Burette Readings for 4 Bottles")
st.write("Enter the volume of Sodium Thiosulfate ($\text{Na}_2\text{S}_2\text{O}_3$) used in titration:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Aqueous Phase ($V_{\text{aq}}$ Titre)")
    b1_aq = st.number_input("Bottle 1 Aq Titre (mL)", value=1.5, step=0.1)
    b2_aq = st.number_input("Bottle 2 Aq Titre (mL)", value=3.0, step=0.1)
    b3_aq = st.number_input("Bottle 3 Aq Titre (mL)", value=4.5, step=0.1)
    b4_aq = st.number_input("Bottle 4 Aq Titre (mL)", value=6.0, step=0.1)

with col2:
    st.markdown("### Organic Phase ($V_{\text{org}}$ Titre)")
    b1_org = st.number_input("Bottle 1 Org Titre (mL)", value=5.2, step=0.1)
    b2_org = st.number_input("Bottle 2 Org Titre (mL)", value=10.5, step=0.1)
    b3_org = st.number_input("Bottle 3 Org Titre (mL)", value=15.8, step=0.1)
    b4_org = st.number_input("Bottle 4 Org Titre (mL)", value=21.0, step=0.1)

# Assemble arrays
v_aq_titre = np.array([b1_aq, b2_aq, b3_aq, b4_aq])
v_org_titre = np.array([b1_org, b2_org, b3_org, b4_org])

st.divider()

# ---------------------------------------------------------
# Calculations & Output Trigger
# ---------------------------------------------------------
if st.button("🚀 Calculate Partition Coefficient", type="primary"):
    
    # 1. Concentration Calculations: C = (N_thio * V_titre) / V_aliquot
    C_aq = (N_thio * v_aq_titre) / V_aq_aliquot
    C_org = (N_thio * v_org_titre) / V_org_aliquot
    K_individual = C_org / C_aq

    # 2. Linear Regression (Slope = K)
    slope, intercept, r_value, p_value, std_err = stats.linregress(C_aq, C_org)
    K_slope = slope
    log_P = np.log10(K_slope) if K_slope > 0 else 0

    # 3. Create DataFrame
    df = pd.DataFrame({
        'Bottle #': [1, 2, 3, 4],
        'V_aq Titre (mL)': v_aq_titre,
        'V_org Titre (mL)': v_org_titre,
        'C_aq (N)': np.round(C_aq, 6),
        'C_org (N)': np.round(C_org, 6),
        'K (C_org / C_aq)': np.round(K_individual, 2)
    })

    st.success("✅ Calculations executed successfully!")

    # Display Metrics Cards
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Partition Coefficient (K)", f"{K_slope:.4f}")
    m_col2.metric("Log P Value", f"{log_P:.4f}")
    m_col3.metric("Linearity (R²)", f"{r_value**2:.4f}")

    st.subheader("📊 Experimental Results Table")
    st.dataframe(df, use_container_width=True)

    # 4. Plotting Graph
    st.subheader("📈 Linear Regression Plot ($C_{\text{org}}$ vs $C_{\text{aq}}$)")
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(C_aq, C_org, color='purple', label='4 Bottle Data Points', s=90, zorder=3)

    x_fit = np.linspace(0, max(C_aq) * 1.1, 100)
    y_fit = slope * x_fit + intercept
    ax.plot(x_fit, y_fit, color='darkorange', linestyle='--', 
            label=f'Best Fit Line (Slope K = {K_slope:.2f})', linewidth=2)

    ax.set_title('Partition Coefficient (K) Determination of Iodine (I₂)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Aqueous Concentration C_aq (N)', fontsize=10)
    ax.set_ylabel('Organic Concentration C_org (N)', fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(fontsize=10)

    st.pyplot(fig)
