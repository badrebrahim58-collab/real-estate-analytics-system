import streamlit as st
import pandas as pd
from io import BytesIO

# ================= إعداد الصفحة =================
st.set_page_config(page_title="Real Estate System", layout="wide")
st.title("Abanoub side")

# ================= رفع الملف =================
uploaded_file = st.file_uploader(" upload file ", type=["xlsx", "csv"])

if uploaded_file is None:
    st.info("⬆️")
    st.stop()

# ================= تحميل البيانات =================
try:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # تنظيف أسماء الأعمدة من المسافات
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error(f"❌ خطأ في قراءة الملف: {e}")
    st.stop()

# ================= الفلاتر في الجانب =================
st.sidebar.header("🔎 خيارات الفلترة")
filtered_df = df.copy()

# --- دالة للسلايدر (أرقام) مع حماية من الأخطاء ---
def safe_num_filter(column, label):
    global filtered_df
    if column in df.columns:
        nums = pd.to_numeric(df[column], errors='coerce').dropna()
        if not nums.empty:
            min_v, max_v = float(nums.min()), float(nums.max())
            if min_v < max_v:
                val = st.sidebar.slider(label, min_v, max_v, (min_v, max_v), key=f"s_{column}")
                filtered_df = filtered_df[filtered_df[column].between(val[0], val[1])]
            else:
                st.sidebar.info(f"{label}: {min_v}")

# --- دالة الاختيار المتعدد مع Select All ---
def safe_multiselect(column, label):
    global filtered_df
    if column in df.columns:
        options = sorted([str(x) for x in df[column].dropna().unique().tolist()])
        if options:
            st.sidebar.write(f"**{label}**")
            # زر اختيار الكل
            select_all = st.sidebar.checkbox(f"تحديد الكل", value=True, key=f"all_{column}")
            default_vals = options if select_all else []
            
            selected = st.sidebar.multiselect(label, options, default=default_vals, key=f"ms_{column}", label_visibility="collapsed")
            filtered_df = filtered_df[filtered_df[column].astype(str).isin(selected)]

# 1. فلاتر الأرقام
safe_num_filter("price_total", "السعر الإجمالي")
safe_num_filter("area_sqm", "المساحة (متر مربع)")
safe_num_filter("floor_number", "رقم الدور")

st.sidebar.divider()

# 2. فلاتر القوائم (تم إضافة Select All لكل واحدة)
safe_multiselect("area", "المنطقة")
safe_multiselect("unit_type", "نوع الوحدة")
safe_multiselect("listing_type", "نوع العرض (بيع/إيجار)")
safe_multiselect("rooms", "عدد الغرف")
safe_multiselect("bathrooms", "عدد الحمامات")
safe_multiselect("unit_status", "حالة الوحدة")

# 3. فلاتر المرافق (في قائمة قابلة للطي)
with st.sidebar.expander("المرافق والخدمات"):
    for util in ["electricity", "water", "gas", "elevator", "garage"]:
        safe_multiselect(util, util.capitalize())

# ================= البحث النصي =================
search_query = st.text_input("🔍 ابحث في الملاحظات أو العنوان (مثلاً: بحري، مرخصة، جراج)")
if search_query:
    mask = pd.Series(False, index=filtered_df.index)
    for col in ["notes", "address"]:
        if col in filtered_df.columns:
            mask |= filtered_df[col].astype(str).str.contains(search_query, case=False, na=False)
    filtered_df = filtered_df[mask]

# ================= عرض النتائج =================
st.subheader(f"📊 النتائج المتاحة: {len(filtered_df)} وحدة")
st.dataframe(filtered_df, use_container_width=True)

# ================= زر التحميل =================
if not filtered_df.empty:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False)
    
    st.download_button(
        label="⬇️ تحميل النتائج المفلترة (Excel)",
        data=output.getvalue(),
        file_name="filtered_properties.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
