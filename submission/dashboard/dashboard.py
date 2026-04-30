import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime as dt

# Set page configuration
st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")

# Custom CSS for UI
st.markdown("""
<style>
    .main-title {
        font-size: 36px;
        font-weight: 600;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 30px;
    }
    .sub-title {
        font-size: 24px;
        font-weight: 500;
        color: #424242;
        margin-top: 20px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🛒 E-Commerce Public Dataset Dashboard</div>', unsafe_allow_html=True)

# 1. Load Data
@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '../dashboard/main_data.csv')
    all_df = pd.read_csv(data_path)
    return all_df

try:
    all_df = load_data()
except FileNotFoundError as e:
    st.error(f"Data tidak ditemukan! Error path: {e}")
    st.stop()

# 2. Clean Data
@st.cache_data
def clean_data(df):
    # Konversi kolom tanggal
    date_cols = [
        'order_purchase_timestamp', 'order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
            
    # Hapus missing values pada tanggal pengiriman
    df = df.dropna(subset=['order_delivered_customer_date'])
    
    # Tangani outlier payment_value dengan IQR menggunakan subset yang tidak duplikat untuk payment
    # Karena data terdenormalisasi, kita cari unique payments dulu
    unique_payments = df.drop_duplicates(subset=['order_id', 'payment_sequential'])
    Q1 = unique_payments['payment_value'].quantile(0.25)
    Q3 = unique_payments['payment_value'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Filter dataset utama berdasarkan batas IQR
    # Hati-hati: ada payment yang NaN jika left join
    df = df[(df['payment_value'].isna()) | ((df['payment_value'] >= lower_bound) & (df['payment_value'] <= upper_bound))]
    
    # Hitung shipping time
    df['shipping_time'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days

    return df

all_df_clean = clean_data(all_df)

# Sidebar untuk filter waktu
min_date = all_df_clean['order_purchase_timestamp'].min().date()
max_date = all_df_clean['order_purchase_timestamp'].max().date()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=200)
    st.header("Filter Data")
    
    start_date, end_date = st.date_input(
        label="Pilih Rentang Waktu",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Terapkan filter tanggal
all_df_filtered = all_df_clean[
    (all_df_clean['order_purchase_timestamp'].dt.date >= start_date) & 
    (all_df_clean['order_purchase_timestamp'].dt.date <= end_date)
]

st.markdown("---")

# Metrics
# Karena data tergabung, kita harus hati-hati dengan order_id yang duplikat
unique_orders = all_df_filtered.drop_duplicates(subset=['order_id'])
unique_payments = all_df_filtered.drop_duplicates(subset=['order_id', 'payment_sequential'])

col1, col2, col3 = st.columns(3)
with col1:
    total_orders = unique_orders.shape[0]
    st.metric("Total Pesanan (Filtered)", f"{total_orders:,}")
with col2:
    total_revenue = unique_payments['payment_value'].sum()
    st.metric("Total Pendapatan (BRL)", f"R$ {total_revenue:,.2f}")
with col3:
    avg_shipping = unique_orders['shipping_time'].mean()
    st.metric("Rata-rata Pengiriman", f"{avg_shipping:.1f} Hari")

st.markdown("---")

# =========================================================
# Pertanyaan 1: Analisis Metode Pembayaran
# =========================================================
st.markdown('<div class="sub-title">1. Analisis Metode Pembayaran</div>', unsafe_allow_html=True)
st.write("Bagaimana perbedaan rata-rata nilai pembayaran berdasarkan metode pembayaran, dan metode mana yang paling dominan?")

payment_summary = (
    unique_payments.groupby('payment_type')
    .agg(
        avg_payment=('payment_value', 'mean'),
        total_transactions=('order_id', 'count')
    )
    .sort_values('avg_payment', ascending=False)
    .reset_index()
)

fig1, axes1 = plt.subplots(1, 2, figsize=(14, 5))
sns.set_style("whitegrid")

# Plot 1
colors1 = ['#1976D2' if i == 0 else '#90CAF9' for i in range(len(payment_summary))]
axes1[0].bar(payment_summary['payment_type'], payment_summary['avg_payment'], color=colors1, edgecolor='white')
axes1[0].set_title('Rata-rata Nilai Transaksi per Metode Pembayaran')
axes1[0].set_ylabel('Rata-rata Nilai (BRL)')
for i, v in enumerate(payment_summary['avg_payment']):
    axes1[0].text(i, v + 1, f'{v:.1f}', ha='center', va='bottom', fontweight='bold')

# Plot 2
colors2 = ['#FF6F00' if i == 0 else '#FFCC80' for i in range(len(payment_summary))]
axes1[1].bar(payment_summary['payment_type'], payment_summary['total_transactions'], color=colors2, edgecolor='white')
axes1[1].set_title('Jumlah Transaksi per Metode Pembayaran')
axes1[1].set_ylabel('Jumlah Transaksi')
for i, v in enumerate(payment_summary['total_transactions']):
    axes1[1].text(i, v + 100, f'{int(v):,}', ha='center', va='bottom', fontweight='bold', fontsize=9)

plt.tight_layout()
st.pyplot(fig1)

with st.expander("Lihat Insight Pembayaran"):
    st.write("""
    - **Metode pembayaran credit card** mendominasi baik dari sisi rata-rata nilai transaksi maupun jumlah transaksi. 
    - Hal ini menjadikannya metode yang paling difavoritkan pelanggan untuk bertransaksi di E-Commerce.
    - Voucher memiliki rata-rata transaksi paling rendah, kemungkinan banyak digunakan sebagai potongan harga atau pembelian barang-barang murah.
    """)

st.markdown("---")

# =========================================================
# Pertanyaan 2: Performa Waktu Pengiriman
# =========================================================
st.markdown('<div class="sub-title">2. Performa Waktu Pengiriman per State Seller</div>', unsafe_allow_html=True)
st.write("Apakah lokasi seller mempengaruhi rata-rata waktu pengiriman pesanan?")

# Kita gunakan relasi unik order-seller agar tidak terduplikasi oleh multiple items dari seller yang sama dalam satu order
unique_order_sellers = all_df_filtered.dropna(subset=['seller_state']).drop_duplicates(subset=['order_id', 'seller_id'])

shipping_summary = (
    unique_order_sellers.groupby('seller_state')
    .agg(
        avg_shipping=('shipping_time', 'mean'),
        total_orders=('order_id', 'nunique')
    )
    .sort_values('avg_shipping')
    .round(2)
)

# Filter minimal 50 order
shipping_rep = shipping_summary[shipping_summary['total_orders'] >= 50].copy()

fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))

state_colors = ['#2E7D32' if v == shipping_rep['avg_shipping'].min() 
                else '#C62828' if v == shipping_rep['avg_shipping'].max() 
                else '#90A4AE' for v in shipping_rep['avg_shipping']]

# Plot 1
axes2[0].barh(shipping_rep.index, shipping_rep['avg_shipping'], color=state_colors)
axes2[0].set_title('Rata-rata Waktu Pengiriman per State (min. 50 order)')
axes2[0].set_xlabel('Waktu Pengiriman (hari)')
axes2[0].axvline(shipping_rep['avg_shipping'].mean(), color='navy', linestyle='--', label='Rata-rata Keseluruhan')
axes2[0].legend()

# Plot 2
scatter = axes2[1].scatter(
    shipping_summary['total_orders'], shipping_summary['avg_shipping'],
    c=shipping_summary['avg_shipping'], cmap='RdYlGn_r', s=80, alpha=0.8, edgecolors='gray'
)
plt.colorbar(scatter, ax=axes2[1], label='Avg Shipping Time (hari)')
axes2[1].set_title('Jumlah Order vs Rata-rata Waktu Pengiriman')
axes2[1].set_xlabel('Total Order (log scale)')
axes2[1].set_ylabel('Rata-rata Waktu Pengiriman (hari)')
axes2[1].set_xscale('log')

plt.tight_layout()
st.pyplot(fig2)

with st.expander("Lihat Insight Pengiriman"):
    st.write("""
    - **Terdapat perbedaan signifikan** waktu pengiriman antar state.
    - State di pulau utama atau pusat bisnis seperti **SP (São Paulo)** cenderung memiliki pengiriman yang sangat cepat dan didukung oleh volume order yang tinggi.
    - State terpencil membutuhkan waktu yang jauh lebih lama, menunjukkan kendala logistik.
    """)

st.markdown("---")

# =========================================================
# RFM Analysis
# =========================================================
st.markdown('<div class="sub-title">3. RFM Analysis (Segmentasi Pelanggan)</div>', unsafe_allow_html=True)

# Batasi penggunaan data
snapshot_date = all_df_filtered['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

# Agregasi untuk RFM
# Masing-masing customer hitung Recency, Frequency (berdasarkan order_id unik), Monetary (berdasarkan unik payments)

rfm_recency_freq = all_df_filtered.drop_duplicates(subset=['order_id']).groupby('customer_unique_id').agg(
    Recency=('order_purchase_timestamp', lambda x: (snapshot_date - x.max()).days),
    Frequency=('order_id', 'nunique')
).reset_index()

rfm_monetary = unique_payments.groupby('customer_unique_id').agg(
    Monetary=('payment_value', 'sum')
).reset_index()

rfm_df = rfm_recency_freq.merge(rfm_monetary, on='customer_unique_id')

rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], q=5, labels=[5,4,3,2,1])
rfm_df['F_Score'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5])
rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'], q=5, labels=[1,2,3,4,5])

def segment_customer(row):
    r, f = int(row['R_Score']), int(row['F_Score'])
    if r >= 4 and f >= 4: return 'Champions'
    elif r >= 3 and f >= 3: return 'Loyal Customers'
    elif r >= 4 and f <= 2: return 'New Customers'
    elif r <= 2 and f >= 3: return 'At Risk'
    elif r <= 2 and f <= 2: return 'Lost Customers'
    else: return 'Potential Loyalists'

rfm_df['Segment'] = rfm_df.apply(segment_customer, axis=1)
segment_counts = rfm_df['Segment'].value_counts()

fig3, axes3 = plt.subplots(1, 2, figsize=(14, 5))
palette_rfm = ['#1565C0', '#388E3C', '#FBC02D', '#E64A19', '#6A1B9A', '#00838F']

# Pie chart
axes3[0].pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%', colors=palette_rfm, startangle=140)
axes3[0].set_title('Proporsi Segmen Pelanggan')

# Bar chart
seg_monetary = rfm_df.groupby('Segment')['Monetary'].mean().sort_values(ascending=False)
axes3[1].bar(seg_monetary.index, seg_monetary.values, color=palette_rfm)
axes3[1].set_title('Rata-rata Total Belanja per Segmen')
axes3[1].tick_params(axis='x', rotation=30)

plt.tight_layout()
st.pyplot(fig3)

st.caption("Dashboard Created by Michelle Angelique Nataputra")
