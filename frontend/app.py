
import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend
# If they are on the same Docker network, http://backend:7860 will work.
# Fallback: Let users dynamically input their Public Codespaces Backend URL if internal communication fails.
BACKEND_URL = "http://backend:7860"

# Page title
st.title("SuperKart System")
st.write(
    "Enter the product and store details below to predict the total sales."
)

# Sidebar fallback settings for easy debugging
st.sidebar.header("Network Settings")
use_public_url = st.sidebar.checkbox("Use Public Codespaces URL fallback", value=False)
if use_public_url:
    custom_backend_url = st.sidebar.text_input("Public Backend URL", "https://laughing-space-pancake-696r9pg75rjjc5jr6-7860.app.github.dev")
    BACKEND_URL = custom_backend_url.rstrip("/")
else:
    st.sidebar.info("Currently attempting internal Docker network connection to backend host: http://backend:7860")

# Input fields for product and store data
Product_Weight = st.number_input("Product Weight", min_value=0.0, value=12.66)
Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
Product_Allocated_Area = st.number_input("Product Allocated Area", min_value=0.0, value=0.027)
Product_MRP = st.number_input("Product MRP", min_value=0.0, value=117.08)
Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
Store_Type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Supermarket Type3", "Departmental Store", "Food Mart"])
Product_Id_char = st.selectbox("Product ID Character", ["FD", "DR", "NC"])
Store_Age_Years = st.number_input("Store Age (Years)", min_value=0, value=16)
Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

# Create JSON payload
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": Store_Age_Years,
    "Product_Type_Category": Product_Type_Category
}

# Single Prediction
if st.button("Predict", type='primary'):
    try:
        response = requests.post(
            f"{BACKEND_URL}/v1/predict",
            json=product_data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            predicted_sales = result["Sales"]
            st.success(f"Predicted Product Store Sales Total: ₹{predicted_sales:.2f}")
        else:
            st.error(f"Backend returned error status code: {response.status_code}. Response: {response.text}")
    except Exception as e:
        st.error(f"Unable to connect to the prediction API at {BACKEND_URL}. Error: {e}")

# Batch Prediction
st.subheader("Batch Prediction")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    if st.button("Predict for Batch", type='primary'):
        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": uploaded_file},
                timeout=30
            )

            if response.status_code == 200:
                results = response.json()
                st.success("Predictions completed successfully!")

                try:
                    if isinstance(results, list):
                        df = pd.DataFrame(results)
                    elif isinstance(results, dict):
                        if all(not isinstance(v, (list, dict)) for v in results.values()):
                            df = pd.DataFrame([results])
                        else:
                            df = pd.DataFrame(results)
                    else:
                        df = pd.DataFrame({"Result": [results]})

                    st.dataframe(df, use_container_width=True)
                except Exception as ex:
                    st.error(f"Unable to display results as a table: {ex}")
                    st.json(results)
            else:
                st.error(f"Backend returned error status code: {response.status_code}. Response: {response.text}")
        except Exception as e:
            st.error(f"Unable to connect to the prediction API at {BACKEND_URL}. Error: {e}")
