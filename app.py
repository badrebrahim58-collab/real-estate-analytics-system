import streamlit as st
import pandas as pd
from io import BytesIO

# ================= إعداد الصفحة =================
st.set_page_config(page_title="Real Estate System", layout="wide")
st.title("🏠 Abanoub's Real Estate Pro")

# ================= رفع الملف =================
uploaded_file = st.file_uploader("📂 ارفع ملف البيانات (Excel/CSV)", type=["xlsx", "csv"])

if uploaded_file is None:
    st.info("⬆️ في انتظار رفع ملف البيانات للبدء في الفلترة...")
    st.stop()

# ================= تحميل البيانات =================
try:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    df.columns = df.columns.str.strip()
    # تحويل الأعمدة الرقمية لضمان عدم حدوث أخطاء
    for col in ["price_total", "area_sqm", "floor_number"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
except Exception as e:
    st.error(f"❌ خطأ في قراءة الملف: {e}")
    st.stop()

# ================= الفلاتر الجانبية (Sales View) =================
st.sidebar.header("🔎 محرك البحث السريع")
filtered_df = df.copy()

# --- 1. فلاتر الأرقام (Manual Input بدلاً من Slider) ---
st.sidebar.subheader("💰 الميزانية والمساحة")

# فلتر السعر
if "price_total" in df.columns:
    min_p = float(df["price_total"].min())
    max_p = float(df["price_total"].max())
    st.sidebar.write("**السعر الإجمالي**")
    col_p1, col_p2 = st.sidebar.columns(2)
    p_from = col_p1.number_input("من", value=min_p, step=50000.0, key="p_from")
    p_to = col_p2.number_input("إلى", value=max_p, step=50000.0, key="p_to")
    filtered_df = filtered_df[(filtered_df["price_total"] >= p_from) & (filtered_df["price_total"] <= p_to)]

# فلتر المساحة
if "area_sqm" in df.columns:
    min_a = float(df["area_sqm"].min())
    max_a = float(df["area_sqm"].max())
    st.sidebar.write("**المساحة (م²)**")
    col_a1, col_a2 = st.sidebar.columns(2)
    a_from = col_a1.number_input("من", value=min_a, step=5.0, key="a_from")
    a_to = col_a2.number_input("إلى", value=max_a, step=5.0, key="a_to")
    filtered_df = filtered_df[(filtered_df["area_sqm"] >= a_from) & (filtered_df["area_sqm"] <= a_to)]

# فلتر الأدوار
if "floor_number" in df.columns:
    st.sidebar.write("**رقم الدور**")
    col_f1, col_f2 = st.sidebar.columns(2)
    f_from = col_f1.number_input("من دور", value=int(df["floor_number"].min()), step=1, key="f_from")
    f_to = col_f2.number_input("إلى دور", value=int(df["floor_number"].max()), step=1, key="f_to")
    filtered_df = filtered_df[(filtered_df["floor_number"] >= f_from) & (filtered_df["floor_number"] <= f_to)]

st.sidebar.divider()

# --- 2. فلاتر الاختيار المتعدد (مع Select All) ---
def sales_multiselect(column, label):
    global filtered_df
    if column in df.columns:
        options = sorted([str(x) for x in df[column].dropna().unique().tolist()])
        if options:
            st.sidebar.write(f"**{label}**")
            select_all = st.sidebar.checkbox(f"الكل ({label})", value=True, key=f"all_{column}")
            default_vals = options if select_all else []
            selected = st.sidebar.multiselect(label, options, default=default_vals, key=f"ms_{column}", label_visibility="collapsed")
            filtered_df = filtered_df[filtered_df[column].astype(str).isin(selected)]

sales_multiselect("area", "المنطقة")
sales_multiselect("unit_type", "نوع الوحدة")
sales_multiselect("listing_type", "نوع العرض")
sales_multiselect("rooms", "الغرف")
sales_multiselect("bathrooms", "الحمامات")
sales_multiselect("unit_status", "الحالة")

# 3. المرافق
with st.sidebar.expander("➕ مرافق إضافية"):
    for util in ["electricity", "water", "gas", "elevator", "garage"]:
        sales_multiselect(util, util.capitalize())

# ================= البحث الذكي (Keyword Search) =================
st.markdown("### 🔍 ابحث عن كلمات مميزة (مثل: بحري، مرخصة، قسط، ناصية)")
search_query = st.text_input("ادخل الكلمات الدليلية هنا...", placeholder="مثلاً: جراج، عداد كهرباء، الترا سوبر لوكس")
if search_query:
    mask = pd.Series(False, index=filtered_df.index)
    for col in ["notes", "address"]:
        if col in filtered_df.columns:
            mask |= filtered_df[col].astype(str).str.contains(search_query, case=False, na=False)
    filtered_df = filtered_df[mask]

# ================= عرض النتائج =================
st.subheader(f"📈 وجدنا لك {len(filtered_df)} وحدة مطابقة لطلبك")
st.dataframe(filtered_df, use_container_width=True)

# ================= تصدير البيانات (Export) =================
if not filtered_df.empty:
    buffer = BytesIO()
    # استخدمنا openpyxl لسهولة التثبيت
    filtered_df.to_excel(buffer, index=False, engine='openpyxl')
    
    st.download_button(
        label="📥 تحميل الوحدات المختارة للعميل (Excel)",
        data=buffer.getvalue(),
        file_name="ابانوب_للعقارات_المفلترة.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
