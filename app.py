import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ── Konfigurasi halaman ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analisis Penjualan & Curah Hujan",
    page_icon="🌧️",
    layout="wide",
)

st.title("🌧️ Dashboard Analisis Penjualan & Curah Hujan")
st.markdown("---")

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("dataset.csv")
    hari_map = {0: "Minggu", 1: "Senin", 2: "Selasa",
                3: "Rabu",   4: "Kamis", 5: "Jumat", 6: "Sabtu"}
    df["Nama Hari"] = df["Hari"].map(hari_map)
    df["Status Kegiatan"] = df["Kegiatan"].map({0: "Libur", 1: "Aktif"})
    return df

df = load_data()

# ── Sidebar filter ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Filter Data")
    
    kegiatan_filter = st.multiselect(
        "Status Kegiatan",
        options=["Aktif", "Libur"],
        default=["Aktif", "Libur"],
    )
    
    hari_filter = st.multiselect(
        "Hari",
        options=["Minggu","Senin","Selasa","Rabu","Kamis","Jumat","Sabtu"],
        default=["Minggu","Senin","Selasa","Rabu","Kamis","Jumat","Sabtu"],
    )
    
    curah_range = st.slider(
        "Rentang Curah Hujan (mm)",
        float(df["Curah Hujan (mm)"].min()),
        float(df["Curah Hujan (mm)"].max()),
        (float(df["Curah Hujan (mm)"].min()), float(df["Curah Hujan (mm)"].max())),
    )

# Terapkan filter
mask = (
    df["Status Kegiatan"].isin(kegiatan_filter) &
    df["Nama Hari"].isin(hari_filter) &
    df["Curah Hujan (mm)"].between(curah_range[0], curah_range[1])
)
df_f = df[mask].copy()

# ── KPI cards ────────────────────────────────────────────────────────────────
st.subheader("📊 Ringkasan Statistik")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Data",        f"{len(df_f)} baris")
c2.metric("Total Penjualan",   f"{df_f['Penjualan (pcs)'].sum():,} pcs")
c3.metric("Rata-rata Penjualan", f"{df_f['Penjualan (pcs)'].mean():.1f} pcs")
c4.metric("Curah Hujan Maks",  f"{df_f['Curah Hujan (mm)'].max():.1f} mm")
c5.metric("Hari Aktif",        f"{(df_f['Kegiatan']==1).sum()} hari")

st.markdown("---")

# ── Baris 1: Scatter + Bar hari ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔵 Penjualan vs Curah Hujan")
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = df_f["Kegiatan"].map({0: "tomato", 1: "steelblue"})
    ax.scatter(df_f["Curah Hujan (mm)"], df_f["Penjualan (pcs)"],
               c=colors, alpha=0.7, edgecolors="white", linewidth=0.5)

    # Garis regresi
    if len(df_f) > 2:
        slope, intercept, r, p, _ = stats.linregress(
            df_f["Curah Hujan (mm)"], df_f["Penjualan (pcs)"])
        x_line = np.linspace(df_f["Curah Hujan (mm)"].min(),
                             df_f["Curah Hujan (mm)"].max(), 100)
        ax.plot(x_line, slope * x_line + intercept, "k--", lw=1.5,
                label=f"r={r:.2f}, p={p:.3f}")
        ax.legend(fontsize=9)

    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(color="steelblue", label="Aktif"),
        Patch(color="tomato",    label="Libur"),
    ], fontsize=9)
    ax.set_xlabel("Curah Hujan (mm)")
    ax.set_ylabel("Penjualan (pcs)")
    ax.set_title("Scatter: Curah Hujan vs Penjualan")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("📅 Rata-rata Penjualan per Hari")
    order = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
    avg_hari = (df_f.groupby("Nama Hari")["Penjualan (pcs)"]
                .mean().reindex([d for d in order if d in df_f["Nama Hari"].unique()]))
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    bars = ax2.bar(avg_hari.index, avg_hari.values,
                   color=sns.color_palette("Blues_d", len(avg_hari)))
    ax2.bar_label(bars, fmt="%.0f", fontsize=8, padding=2)
    ax2.set_xlabel("Hari")
    ax2.set_ylabel("Rata-rata Penjualan (pcs)")
    ax2.set_title("Rata-rata Penjualan per Hari dalam Seminggu")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

# ── Baris 2: Box + Heatmap ──────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("📦 Distribusi Penjualan: Aktif vs Libur")
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    data_box = [
        df_f[df_f["Kegiatan"]==1]["Penjualan (pcs)"].values,
        df_f[df_f["Kegiatan"]==0]["Penjualan (pcs)"].values,
    ]
    bp = ax3.boxplot(data_box, labels=["Aktif","Libur"],
                     patch_artist=True, notch=False)
    bp["boxes"][0].set_facecolor("steelblue")
    bp["boxes"][1].set_facecolor("tomato")
    ax3.set_ylabel("Penjualan (pcs)")
    ax3.set_title("Boxplot Penjualan berdasarkan Status Kegiatan")
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

with col4:
    st.subheader("🔥 Heatmap Korelasi")
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    corr = df_f[["Curah Hujan (mm)", "Penjualan (pcs)", "Kegiatan"]].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                square=True, linewidths=0.5, ax=ax4)
    ax4.set_title("Matriks Korelasi")
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close()

# ── Baris 3: Histogram penjualan ────────────────────────────────────────────
st.markdown("---")
st.subheader("📈 Distribusi Frekuensi Penjualan")
fig5, ax5 = plt.subplots(figsize=(12, 3.5))
ax5.hist(df_f["Penjualan (pcs)"], bins=30, color="steelblue",
         edgecolor="white", alpha=0.85)
ax5.axvline(df_f["Penjualan (pcs)"].mean(),   color="red",    ls="--", lw=1.5, label="Mean")
ax5.axvline(df_f["Penjualan (pcs)"].median(), color="orange", ls=":",  lw=1.5, label="Median")
ax5.set_xlabel("Penjualan (pcs)")
ax5.set_ylabel("Frekuensi")
ax5.set_title("Histogram Penjualan")
ax5.legend()
plt.tight_layout()
st.pyplot(fig5)
plt.close()

# ── Statistik deskriptif & uji korelasi ─────────────────────────────────────
st.markdown("---")
col5, col6 = st.columns(2)

with col5:
    st.subheader("📋 Statistik Deskriptif")
    st.dataframe(
        df_f[["Curah Hujan (mm)", "Penjualan (pcs)"]].describe().round(2),
        use_container_width=True,
    )

with col6:
    st.subheader("🔬 Uji Korelasi Pearson")
    r, p = stats.pearsonr(df_f["Curah Hujan (mm)"], df_f["Penjualan (pcs)"])
    st.markdown(f"""
    | Parameter | Nilai |
    |-----------|-------|
    | Koefisien Korelasi (r) | **{r:.4f}** |
    | p-value | **{p:.4f}** |
    | Interpretasi | {"Signifikan (p < 0.05)" if p < 0.05 else "Tidak Signifikan (p ≥ 0.05)"} |
    | Arah Hubungan | {"Positif ➕" if r > 0 else "Negatif ➖"} |
    | Kekuatan | {"Kuat" if abs(r)>0.6 else "Sedang" if abs(r)>0.3 else "Lemah"} |
    """)

# ── Tabel data ───────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📂 Lihat Data Lengkap"):
    st.dataframe(
        df_f[["Nama Hari","Tanggal","Status Kegiatan",
              "Curah Hujan (mm)","Penjualan (pcs)"]].reset_index(drop=True),
        use_container_width=True,
    )

st.caption("Dashboard dibuat dengan Streamlit · Data: Dataset Penjualan & Curah Hujan")
