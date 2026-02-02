import streamlit as st
import pandas as pd
from io import BytesIO

# ================= Page Setup =================
st.set_page_config(page_title="Real Estate System", layout="wide")
st.title("🏠 Real Estate Filtering System")

# ================= Upload File =================
uploaded_file = st.file_uploader(
    "📂 Upload Excel file",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("⬆️ Please upload Excel file to start filtering")
    st.stop()

# ================= Load Data =================
try:
    df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"❌ Error reading Excel file: {e}")
    st.stop()

if df.empty:
    st.warning("⚠️ Excel file is empty")
    st.stop()

# ================= Sidebar Filters =================
st.sidebar.header("🔎 Filters")
filtered_df = df.copy()

# ===== Price Filter =====
if "price_total" in df.columns and df["price_total"].notna().sum() > 1:
    min_price = int(df["price_total"].min())
    max_price = int(df["price_total"].max())
    price_range = st.sidebar.slider("Price Range", min_price, max_price, (min_price, max_price))
    filtered_df = filtered_df[filtered_df["price_total"].between(price_range[0], price_range[1])]

# ===== Area Filter =====
if "area" in df.columns:
    areas_list = df["area"].dropna().unique().tolist()
    if areas_list:
        areas = st.sidebar.multiselect("Area", options=areas_list, default=areas_list)
        filtered_df = filtered_df[filtered_df["area"].isin(areas)]

# ===== Unit Type =====
if "unit_type" in df.columns:
    types_list = df["unit_type"].dropna().unique().tolist()
    if types_list:
        types = st.sidebar.multiselect("Unit Type", options=types_list, default=types_list)
        filtered_df = filtered_df[filtered_df["unit_type"].isin(types)]

# ===== Listing Type =====
if "listing_type" in df.columns:
    listing_list = df["listing_type"].dropna().unique().tolist()
    if listing_list:
        listing = st.sidebar.multiselect("Listing Type", options=listing_list, default=listing_list)
        filtered_df = filtered_df[filtered_df["listing_type"].isin(listing)]

# ===== Payment Type =====
if "payment_type" in df.columns:
    payment_list = df["payment_type"].dropna().unique().tolist()
    if payment_list:
        payment = st.sidebar.multiselect("Payment Type", options=payment_list, default=payment_list)
        filtered_df = filtered_df[filtered_df["payment_type"].isin(payment)]

# ===== Floor Filter =====
if "floor_number" in df.columns and df["floor_number"].notna().sum() > 1:
    min_floor = int(df["floor_number"].min())
    max_floor = int(df["floor_number"].max())
    floor_range = st.sidebar.slider("Floor Number", min_floor, max_floor, (min_floor, max_floor))
    filtered_df = filtered_df[filtered_df["floor_number"].between(floor_range[0], floor_range[1])]

# ===== Rooms Filter =====
if "rooms" in df.columns:
    rooms_list = sorted(df["rooms"].dropna().unique())
    if rooms_list:
        rooms = st.sidebar.multiselect("Rooms", options=rooms_list, default=rooms_list)
        filtered_df = filtered_df[filtered_df["rooms"].isin(rooms)]

# ===== Bathrooms Filter =====
if "bathrooms" in df.columns:
    bath_list = sorted(df["bathrooms"].dropna().unique())
    if bath_list:
        baths = st.sidebar.multiselect("Bathrooms", options=bath_list, default=bath_list)
        filtered_df = filtered_df[filtered_df["bathrooms"].isin(baths)]

# ===== Unit Status =====
if "unit_status" in df.columns:
    status_list = df["unit_status"].dropna().unique().tolist()
    if status_list:
        status = st.sidebar.multiselect("Unit Status", options=status_list, default=status_list)
        filtered_df = filtered_df[filtered_df["unit_status"].isin(status)]

# ===== Furnished =====
if "furnished" in df.columns:
    furnished_list = df["furnished"].dropna().unique().tolist()
    if furnished_list:
        furnished_sel = st.sidebar.multiselect("Furnished", options=furnished_list, default=furnished_list)
        filtered_df = filtered_df[filtered_df["furnished"].isin(furnished_sel)]

# ===== Utilities =====
for util in ["electricity", "water", "gas", "elevator", "garage"]:
    if util in df.columns:
        util_list = df[util].dropna().unique().tolist()
        if util_list:
            util_sel = st.sidebar.multiselect(util.capitalize(), options=util_list, default=util_list)
            filtered_df = filtered_df[filtered_df[util].isin(util_sel)]

# ===== Area in sqm Filter =====
if "area_sqm" in df.columns and df["area_sqm"].notna().sum() > 1:
    min_area = float(df["area_sqm"].min())
    max_area = float(df["area_sqm"].max())
    area_range = st.sidebar.slider("Area (sqm)", float(min_area), float(max_area), (float(min_area), float(max_area)))
    filtered_df = filtered_df[filtered_df["area_sqm"].between(area_range[0], area_range[1])]

# # ===== Date Added Filter =====
# if "date_added" in df.columns:
#     try:
#         df["date_added"] = pd.to_datetime(df["date_added"], errors='coerce')
#         min_date = df["date_added"].min()
#         max_date = df["date_added"].max()
#         date_range = st.sidebar.date_input("Date Added", [min_date, max_date])
#         if len(date_range) == 2:
#             start_date, end_date = date_range
#             filtered_df = filtered_df[
#                 (filtered_df["date_added"] >= pd.to_datetime(start_date)) &
#                 (filtered_df["date_added"] <= pd.to_datetime(end_date))
#             ]
#     except Exception as e:
#         st.sidebar.warning(f"⚠️ Could not filter by date: {e}")

# ===== Search =====
search_text = st.text_input("🔍 Search in notes / address")
if search_text:
    mask = pd.Series(False, index=filtered_df.index)
    if "notes" in filtered_df.columns:
        mask = mask | filtered_df["notes"].astype(str).str.contains(search_text, case=False, na=False, regex=False)
    if "address" in filtered_df.columns:
        mask = mask | filtered_df["address"].astype(str).str.contains(search_text, case=False, na=False, regex=False)
    filtered_df = filtered_df[mask]

# ================= Output =================
st.subheader(f"📊 Results: {len(filtered_df)} units")
st.dataframe(filtered_df, use_container_width=True, height=600)

# ================= Download =================
if filtered_df.empty:
    st.info("ℹ️ No units match your filters, nothing to download")
else:
    buffer = BytesIO()
    filtered_df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        "⬇️ Download Filtered Data",
        buffer,
        file_name="filtered_units.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
