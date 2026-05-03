"""
Minimal Streamlit dashboard to show prediction and plot from `src/model.py`.
Run with: `streamlit run src/app_streamlit.py`
"""
import streamlit as st
import pandas as pd
from src import model


st.title("Price Prediction Dashboard")

st.markdown("Predict the next average price from the latest cleaned dataset.")

pred, trained_model, X, y = model.predict_next_price(cleaned_dir="data/cleaned")

if pred is None:
    st.error("Prediction failed. Check data/cleaned for CSV files and column 'price' or 'price_excl_tax'.")
else:
    st.subheader("Prediction")
    st.write(f"Predicted next price: **{pred:.2f}**")

    # current mean
    current_mean = float(y.mean())
    st.write(f"Current mean price: **{current_mean:.2f}**")

    # trend direction (compare prediction to current mean)
    trend = "increasing" if pred > current_mean else "decreasing" if pred < current_mean else "stable"
    st.write(f"Trend: **{trend}**")

    # plot
    fig = model.plot_prediction(trained_model, X, y, pred)
    st.pyplot(fig)
