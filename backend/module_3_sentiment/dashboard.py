# /module_3_sentiment/dashboard.py
# --- VERSI FINAL (Menggunakan 'timestamp' dan 'review_text') ---

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
import plotly.express as px
import time

# --- DB Setup (Tetap sama) ---
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "adminpass")
DB_NAME = os.getenv("POSTGRES_DB", "haji_umrah_db")
DB_HOST = "postgres-db"
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

@st.cache_resource
def get_db_connection():
    engine = create_engine(DATABASE_URL)
    return engine

@st.cache_data(ttl=60)
def load_data():
    try:
        engine = get_db_connection()
        # [FIX] Menggunakan 'timestamp' untuk pengurutan
        query = "SELECT * FROM reviews WHERE sentiment_status = 'processed' ORDER BY timestamp DESC"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data dari database: {e}")
        return pd.DataFrame()

# --- Konfigurasi Halaman (Tetap sama) ---
st.set_page_config(layout="wide", page_title="Dasbor Sentimen Ulasan")
st.title("📊 Dasbor Intelijen Ulasan & Analisis Sentimen")
st.markdown("Memantau umpan balik pelanggan secara *real-time*.")

# --- Load Data ---
df = load_data()

if df.empty:
    st.warning("Menunggu data ulasan dianalisis oleh scheduler...")
    st.button("Coba Muat Ulang")
else:
    # --- Ringkasan KPI (Tetap sama) ---
    st.header("Ringkasan")
    total_reviews = len(df)
    negative_reviews = len(df[df['sentiment'] == 'NEGATIVE'])
    critical_priority = len(df[df['priority'] == 'Kritis'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Ulasan Dianalisis", total_reviews)
    col2.metric("Total Ulasan Negatif", negative_reviews)
    col3.metric("Prioritas Kritis ⚠️", critical_priority)
    
    st.divider()

    # --- Visualisasi (Tetap sama) ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribusi Sentimen")
        if 'sentiment' in df:
            sentiment_counts = df['sentiment'].value_counts()
            fig_pie = px.pie(sentiment_counts, values=sentiment_counts.values, 
                             names=sentiment_counts.index, color=sentiment_counts.index,
                             color_discrete_map={'POSITIVE':'green', 'NEGATIVE':'red', 'NEUTRAL':'orange'})
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with col2:
        st.subheader("Ulasan Berdasarkan Aspek")
        if 'aspect' in df:
            aspect_df = df['aspect'].str.split(', ').explode().value_counts()
            fig_bar = px.bar(aspect_df, x=aspect_df.index, y=aspect_df.values,
                             labels={'y': 'Jumlah Ulasan', 'index': 'Aspek'})
            st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    
    # --- Tabel Keluhan Kritis ---
    st.header("🚨 Tabel Keluhan Kritis & Negatif")
    st.info("Fokus pada ulasan dengan sentimen 'NEGATIVE' untuk ditindaklanjuti.")
    
    critical_df = df[df['sentiment'] == 'NEGATIVE'].sort_values('priority')
    
    # [FIX] Tampilkan 'timestamp' dan 'review_text'
    st.dataframe(critical_df[['timestamp', 'package_id', 'review_text', 'aspect', 'priority']], use_container_width=True)