
import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
file_path = "KOMPILASI DATA PUBLIKASI DOSEN ITBH.xlsx"
df = pd.read_excel(file_path, sheet_name="ITBH")

# Bersihkan nama kolom (hapus spasi ekstra, samakan huruf)
df.columns = df.columns.str.strip().str.replace("\s+", " ", regex=True)

# Map kolom agar aman (tanpa peduli huruf besar kecil)
col_map = {col.lower(): col for col in df.columns}

def get_col(name):
    return col_map.get(name.lower())

# Pastikan kolom yang dipakai ada
scopus_col = get_col("Scopus H-Index")
gs_col = get_col("GS H-Index")
sinta_col = get_col("SINTA SCORE")
prodi_col = get_col("FAKULTAS/ PRODI")
nama_col = get_col("NAMA")

st.set_page_config(page_title="Dashboard Publikasi ITBH", layout="wide")
st.title("📊 Dashboard Publikasi Dosen ITBH")

# Sidebar Filters
prodi_options = ["Semua"] + sorted(df[prodi_col].dropna().unique().tolist())
selected_prodi = st.sidebar.selectbox("Pilih Prodi", prodi_options)

min_h = int(df[scopus_col].min())
max_h = int(df[scopus_col].max())
h_index_range = st.sidebar.slider("Scopus H-Index Range", min_h, max_h, (min_h, max_h))

min_sinta = int(df[sinta_col].min())
max_sinta = int(df[sinta_col].max())
sinta_range = st.sidebar.slider("SINTA Score Range", min_sinta, max_sinta, (min_sinta, max_sinta))

# Filter Data
filtered_df = df.copy()
if selected_prodi != "Semua":
    filtered_df = filtered_df[filtered_df[prodi_col] == selected_prodi]

filtered_df = filtered_df[
    (filtered_df[scopus_col].between(h_index_range[0], h_index_range[1])) &
    (filtered_df[sinta_col].between(sinta_range[0], sinta_range[1]))
]

# Metrics
col1, col2 = st.columns(2)
col1.metric("Jumlah Dosen", len(filtered_df))
col2.metric("Rata-rata SINTA", round(filtered_df[sinta_col].mean(), 2))

# Chart 1: Rata-rata SINTA Score per Prodi
avg_by_prodi = filtered_df.groupby(prodi_col)[sinta_col].mean().reset_index()
fig1 = px.bar(avg_by_prodi, x=prodi_col, y=sinta_col, title="Rata-rata SINTA Score per Prodi")
st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Top 10 Dosen berdasarkan SINTA Score
top_sinta = filtered_df.nlargest(10, sinta_col)
fig2 = px.bar(top_sinta, x=sinta_col, y=nama_col, orientation="h", title="Top 10 Dosen - SINTA Score")
st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Scatter Plot H-Index vs SINTA
fig3 = px.scatter(filtered_df, x=scopus_col, y=sinta_col,
                  hover_data=[nama_col, prodi_col], title="Scopus H-Index vs SINTA Score")
st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Scatter Plot Scopus vs GS H-Index
fig4 = px.scatter(filtered_df, x=scopus_col, y=gs_col,
                  hover_data=[nama_col, prodi_col], title="Scopus H-Index vs Google Scholar H-Index")
st.plotly_chart(fig4, use_container_width=True)

# Show table
st.subheader("📄 Data Terfilter")
st.dataframe(filtered_df)

# Download filtered data
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(label="Download CSV", data=csv, file_name="filtered_data_itbh.csv", mime="text/csv")
