# /module_2_recommender/scripts/train_recommender.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, Reader
import pickle
import os

print("Memulai proses training model rekomendasi...")

# Path
DATA_PATH = "/dummy_data"
MODEL_STORE_PATH = "/app/models_store" # Di dalam container

# Pastikan folder models_store ada
os.makedirs(MODEL_STORE_PATH, exist_ok=True)

# --- 1. Model Content-Based (CB) ---
print("Melatih Model Content-Based (TF-IDF)...")
try:
    df_packages = pd.read_csv(f"{DATA_PATH}/packages.csv")
    
    # Gabungkan fitur teks untuk TF-IDF
    df_packages['content_text'] = df_packages['name'] + ' ' + df_packages['description'] + ' ' + df_packages['category']
    
    # Buat model TF-IDF
    tfidf = TfidfVectorizer(stop_words=None) # Kita pakai semua kata (dummy data)
    tfidf_matrix = tfidf.fit_transform(df_packages['content_text'])
    
    # Hitung cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Simpan model dan data
    pickle.dump(cosine_sim, open(f"{MODEL_STORE_PATH}/cb_cosine_sim.pkl", "wb"))
    pickle.dump(tfidf, open(f"{MODEL_STORE_PATH}/cb_tfidf_vectorizer.pkl", "wb"))
    df_packages.to_pickle(f"{MODEL_STORE_PATH}/cb_packages_df.pkl")
    
    print("Model Content-Based berhasil disimpan.")

except FileNotFoundError:
    print(f"ERROR: Gagal memuat {DATA_PATH}/packages.csv. Pastikan file ada.")
    exit(1)
except Exception as e:
    print(f"Error saat melatih model CB: {e}")
    exit(1)


# --- 2. Model Collaborative Filtering (CF) ---
print("Melatih Model Collaborative Filtering (SVD)...")
try:
    df_interactions = pd.read_csv(f"{DATA_PATH}/interactions.csv")
    
    # Buat 'rating' dummy: view=1, book=5
    df_interactions['rating'] = df_interactions['event_type'].apply(lambda x: 5 if x == 'book' else 1)
    
    # Setup Surprise Reader
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df_interactions[['user_id', 'package_id', 'rating']], reader)
    
    # Train SVD
    trainset = data.build_full_trainset()
    model_svd = SVD(n_factors=50, n_epochs=20, random_state=42)
    model_svd.fit(trainset)
    
    # Simpan model
    pickle.dump(model_svd, open(f"{MODEL_STORE_PATH}/cf_svd_model.pkl", "wb"))
    # Simpan data untuk mapping
    df_interactions.to_pickle(f"{MODEL_STORE_PATH}/cf_interactions_df.pkl")

    print("Model Collaborative Filtering (SVD) berhasil disimpan.")

except FileNotFoundError:
    print(f"ERROR: Gagal memuat {DATA_PATH}/interactions.csv. Pastikan file ada.")
    exit(1)
except Exception as e:
    print(f"Error saat melatih model CF: {e}")
    exit(1)

print("\n--- Proses Training Selesai ---")
print(f"Artefak model disimpan di {MODEL_STORE_PATH}")