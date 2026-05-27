import streamlit as st
import pandas as pd
import numpy as np
import pickle

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="House Price Predictor",
    page_icon="🏠",
    layout="wide",
)

# ── Load model & columns ───────────────────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    with open("house_price_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("model_columns.pkl", "rb") as f:
        columns = pickle.load(f)
    return model, list(columns)

model, model_columns = load_artifacts()

# ── Label-encoding maps (alphabetical order = sklearn LabelEncoder default) ────
NEIGHBORHOOD_MAP = {
    "Blmngtn":0,"Blueste":1,"BrDale":2,"BrkSide":3,"ClearCr":4,
    "CollgCr":5,"Crawfor":6,"Edwards":7,"Gilbert":8,"IDOTRR":9,
    "MeadowV":10,"Mitchel":11,"NAmes":12,"NPkVill":13,"NWAmes":14,
    "NoRidge":15,"NridgHt":16,"OldTown":17,"SWISU":18,"Sawyer":19,
    "SawyerW":20,"Somerst":21,"StoneBr":22,"Timber":23,"Veenker":24,
}
MSZONING_MAP     = {"C (all)":0,"FV":1,"RH":2,"RL":3,"RM":4}
SALECOND_MAP     = {"Abnorml":0,"AdjLand":1,"Alloca":2,"Family":3,"Normal":4,"Partial":5}
QUALITY_MAP      = {"Ex":0,"Fa":1,"Gd":2,"TA":3}

# ── Styled header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style='background: linear-gradient(135deg,#1a1a2e,#16213e);
            padding:2rem 2.5rem; border-radius:12px; margin-bottom:1.5rem;'>
  <h1 style='color:#e0e0e0; margin:0; font-size:2.2rem;'>🏠 House Price Predictor</h1>
  <p style='color:#9e9e9e; margin:.5rem 0 0;'>
    Fill in the property details below and click <b>Predict Sale Price</b>.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Input form ─────────────────────────────────────────────────────────────────
with st.form("prediction_form"):

    # ─ 1. Location & Sale ─────────────────────────────────────────────────────
    st.subheader("📍 Location & Sale")
    c1, c2, c3 = st.columns(3)
    with c1:
        Neighborhood  = st.selectbox("Neighborhood",    list(NEIGHBORHOOD_MAP), index=12)
    with c2:
        MSZoning      = st.selectbox("MS Zoning",       list(MSZONING_MAP),     index=3)
    with c3:
        SaleCondition = st.selectbox("Sale Condition",  list(SALECOND_MAP),     index=4)

    c4, c5 = st.columns(2)
    with c4:
        MoSold = st.slider("Month Sold", 1, 12, 6, help="1 = Jan … 12 = Dec")
    with c5:
        MiscVal = st.number_input("Misc Feature Value ($)", 0, 15500, 0)

    st.divider()

    # ─ 2. Lot ──────────────────────────────────────────────────────────────────
    st.subheader("🌿 Lot")
    c1, c2 = st.columns(2)
    with c1:
        LotFrontage = st.number_input("Lot Frontage (ft)",  0,  400,    70)
    with c2:
        LotArea     = st.number_input("Lot Area (sq ft)", 1000, 220000, 10000)

    st.divider()

    # ─ 3. Overall & Year ───────────────────────────────────────────────────────
    st.subheader("⭐ Overall Quality & Year")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        OverallQual  = st.slider("Overall Quality (1–10)", 1, 10, 6)
    with c2:
        YearBuilt    = st.number_input("Year Built",       1872, 2010, 1980)
    with c3:
        YearRemodAdd = st.number_input("Year Remodelled",  1950, 2010, 1990)
    with c4:
        GarageYrBlt  = st.number_input("Garage Year Built",1900, 2010, 1980)

    st.divider()

    # ─ 4. Exterior & Interior Quality ─────────────────────────────────────────
    st.subheader("🏠 Exterior & Interior Quality")
    c1, c2, c3 = st.columns(3)
    with c1:
        ExterQual   = st.selectbox("Exterior Quality",
                                    list(QUALITY_MAP),
                                    index=2,
                                    help="Ex=Excellent  Gd=Good  TA=Average  Fa=Fair")
    with c2:
        KitchenQual = st.selectbox("Kitchen Quality",
                                    list(QUALITY_MAP),
                                    index=2,
                                    help="Ex=Excellent  Gd=Good  TA=Average  Fa=Fair")
    with c3:
        MasVnrArea  = st.number_input("Masonry Veneer Area (sq ft)", 0, 1600, 0)

    st.divider()

    # ─ 5. Above-Ground Living ─────────────────────────────────────────────────
    st.subheader("🏗️ Above-Ground Living")
    c1, c2, c3 = st.columns(3)
    with c1:
        GrLivArea    = st.number_input("Gr Living Area (sq ft)", 300,  6000, 1500)
        TotRmsAbvGrd = st.number_input("Total Rooms Abv Grade",  2,    14,   7)
    with c2:
        FirstFlrSF   = st.number_input("1st Floor (sq ft)",      300,  5000, 1000)
        SecondFlrSF  = st.number_input("2nd Floor (sq ft)",      0,    2100, 0)
    with c3:
        FullBath     = st.number_input("Full Bathrooms",          0,    4,    2)
        HalfBath     = st.number_input("Half Bathrooms",          0,    3,    0)
        BedroomAbvGr = st.number_input("Bedrooms Above Grade",    0,    9,    3)

    st.divider()

    # ─ 6. Basement ────────────────────────────────────────────────────────────
    st.subheader("🏚️ Basement")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        TotalBsmtSF  = st.number_input("Total Basement (sq ft)", 0, 6200, 1000)
        BsmtFinSF1   = st.number_input("Bsmt Finished SF 1",     0, 5700, 400)
    with c2:
        BsmtFinSF2   = st.number_input("Bsmt Finished SF 2",     0, 1500, 0)
        BsmtUnfSF    = st.number_input("Bsmt Unfinished SF",      0, 2400, 300)
    with c3:
        BsmtFullBath = st.number_input("Bsmt Full Baths",         0, 3,    0)
    with c4:
        BsmtHalfBath = st.number_input("Bsmt Half Baths",         0, 2,    0)

    st.divider()

    # ─ 7. Garage ──────────────────────────────────────────────────────────────
    st.subheader("🚗 Garage")
    c1, c2 = st.columns(2)
    with c1:
        GarageCars = st.number_input("Garage Capacity (cars)", 0, 5, 2)
    with c2:
        GarageArea = st.number_input("Garage Area (sq ft)",    0, 1500, 450)

    st.divider()

    # ─ 8. Porches, Pool & Extras ──────────────────────────────────────────────
    st.subheader("🌳 Porches, Pool & Extras")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        WoodDeckSF   = st.number_input("Wood Deck (sq ft)",      0, 900, 0)
        OpenPorchSF  = st.number_input("Open Porch (sq ft)",     0, 550, 0)
    with c2:
        ScreenPorch  = st.number_input("Screen Porch (sq ft)",   0, 500, 0)
        ThreeSsnPorch= st.number_input("3-Season Porch (sq ft)", 0, 510, 0)
    with c3:
        PoolArea     = st.number_input("Pool Area (sq ft)",       0, 750, 0)
    with c4:
        Fireplaces   = st.number_input("Fireplaces",              0, 4,   0)

    # ─ Submit ─────────────────────────────────────────────────────────────────
    st.divider()
    submitted = st.form_submit_button(
        "🔮 Predict Sale Price",
        use_container_width=True,
        type="primary",
    )

# ── Prediction ─────────────────────────────────────────────────────────────────
if submitted:
    input_dict = {
        "BsmtFullBath":  BsmtFullBath,
        "BsmtUnfSF":     BsmtUnfSF,
        "BedroomAbvGr":  BedroomAbvGr,
        "ScreenPorch":   ScreenPorch,
        "PoolArea":      PoolArea,
        "MoSold":        MoSold,
        "3SsnPorch":     ThreeSsnPorch,
        "BsmtFinSF2":    BsmtFinSF2,
        "BsmtHalfBath":  BsmtHalfBath,
        "MiscVal":       MiscVal,
        "BsmtFinSF1":    BsmtFinSF1,
        "LotFrontage":   LotFrontage,
        "WoodDeckSF":    WoodDeckSF,
        "2ndFlrSF":      SecondFlrSF,
        "OpenPorchSF":   OpenPorchSF,
        "HalfBath":      HalfBath,
        "LotArea":       LotArea,
        "OverallQual":   OverallQual,
        "GrLivArea":     GrLivArea,
        "GarageCars":    GarageCars,
        "GarageArea":    GarageArea,
        "TotalBsmtSF":   TotalBsmtSF,
        "1stFlrSF":      FirstFlrSF,
        "FullBath":      FullBath,
        "TotRmsAbvGrd":  TotRmsAbvGrd,
        "YearBuilt":     YearBuilt,
        "YearRemodAdd":  YearRemodAdd,
        "GarageYrBlt":   GarageYrBlt,
        "MasVnrArea":    MasVnrArea,
        "Fireplaces":    Fireplaces,
        # Encode categoricals with the same label-encoding used at training time
        "Neighborhood":  NEIGHBORHOOD_MAP[Neighborhood],
        "MSZoning":      MSZONING_MAP[MSZoning],
        "SaleCondition": SALECOND_MAP[SaleCondition],
        "KitchenQual":   QUALITY_MAP[KitchenQual],
        "ExterQual":     QUALITY_MAP[ExterQual],
    }

    # Build input array in the exact column order the model expects
    X = np.array([[input_dict[col] for col in model_columns]], dtype=float)

    try:
        prediction = model.predict(X)[0]

        st.success("### 💰 Predicted Sale Price")
        col_pred, col_gap = st.columns([1, 2])
        with col_pred:
            st.metric(label="Estimated Price", value=f"${prediction:,.0f}")

        with st.expander("📋 Full input summary"):
            summary = {
                "Feature": list(input_dict.keys()),
                "Raw value": list(input_dict.values()),
            }
            st.dataframe(
                pd.DataFrame(summary),
                use_container_width=True,
                hide_index=True,
            )

    except Exception as e:
        st.error(f"Prediction failed: {e}")
