# /module_4_lead_scoring/scripts/train_lead_scorer.py
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.preprocessing import OneHotEncoder
import shap
import joblib
import json
import os
from datetime import datetime, timedelta

print("Memulai proses training model Lead Scoring...")

# Path
DATA_PATH = "/dummy_data"
MODEL_STORE_PATH = "/app/model_store"

# Pastikan folder models_store ada
os.makedirs(MODEL_STORE_PATH, exist_ok=True)

# --- GENERATE DATA DUMMY JIKA TIDAK ADA ATAU TERLALU KECIL ---
leads_file = f"{DATA_PATH}/leads.csv"
REGENERATE = False

try:
    df_leads = pd.read_csv(leads_file)
    if len(df_leads) < 100:
        print(f"⚠ Data terlalu kecil ({len(df_leads)} rows). Generating new data...")
        REGENERATE = True
    else:
        print(f"✓ Data loaded: {len(df_leads)} rows")
except FileNotFoundError:
    print(f"⚠ File {leads_file} tidak ditemukan. Generating new data...")
    REGENERATE = True

if REGENERATE:
    print("\n--- Generating 1000 Dummy Leads ---")
    np.random.seed(42)
    N_SAMPLES = 1000
    
    data = {
        'lead_id': [f'L{str(i+1).zfill(4)}' for i in range(N_SAMPLES)],
        'timestamp': [(datetime(2025, 8, 1) + timedelta(hours=i*2)).strftime('%Y-%m-%d %H:%M:%S') 
                      for i in range(N_SAMPLES)],
    }
    
    # Lead sources
    data['lead_source'] = np.random.choice(
        ['Google', 'Facebook', 'Referral', 'WebsiteDirect', 'LinkedIn'],
        size=N_SAMPLES, p=[0.35, 0.25, 0.20, 0.15, 0.05]
    )
    
    # Pages viewed
    pages_viewed = np.clip(np.random.poisson(lam=8, size=N_SAMPLES), 1, 50)
    data['pages_viewed'] = pages_viewed
    
    # Time on site
    data['time_on_site_sec'] = (pages_viewed * np.random.uniform(30, 80, N_SAMPLES)).astype(int)
    
    # Visited pricing page
    pricing_prob = np.clip(pages_viewed / 30, 0.1, 0.8)
    data['visited_pricing_page'] = np.random.binomial(1, pricing_prob)
    
    # Form submissions
    data['form_submission_count'] = np.clip(np.random.poisson(lam=0.5, size=N_SAMPLES), 0, 5)
    
    # Email opened
    data['email_opened_count'] = np.clip(np.random.poisson(lam=1.5, size=N_SAMPLES), 0, 10)
    
    # Recency
    data['recency_visit_days'] = np.clip(np.random.exponential(scale=10, size=N_SAMPLES).astype(int), 0, 60)
    
    # Generate conversion
    conversion_score = (
        pages_viewed * 0.3 +
        (data['time_on_site_sec'] / 100) * 0.2 +
        data['visited_pricing_page'] * 5 +
        data['form_submission_count'] * 3 +
        data['email_opened_count'] * 0.5 -
        data['recency_visit_days'] * 0.15 +
        np.random.normal(0, 2, N_SAMPLES)
    )
    
    conversion_threshold = np.percentile(conversion_score, 70)
    data['is_converted'] = (conversion_score > conversion_threshold).astype(int)
    
    df_leads = pd.DataFrame(data)
    df_leads.to_csv(leads_file, index=False)
    print(f"✓ Generated and saved {len(df_leads)} leads to {leads_file}")

# --- VALIDASI DATA ---
print("\n--- Data Validation ---")
conversion_rate = df_leads['is_converted'].mean()
print(f"Conversion rate: {conversion_rate*100:.1f}%")

if conversion_rate < 0.05 or conversion_rate > 0.95:
    print("WARNING: Class imbalance sangat ekstrem. Model mungkin tidak optimal.")

# --- 1. Preprocessing & Feature Engineering ---
print("\n--- Preprocessing ---")

# Drop kolom yang tidak relevan untuk training
df_train = df_leads.drop(['lead_id', 'timestamp'], axis=1)

# Pisahkan Fitur (X) dan Target (y)
X = df_train.drop('is_converted', axis=1)
y = df_train['is_converted']

# Identifikasi kolom kategorikal
categorical_cols = X.select_dtypes(include='object').columns
print(f"Kolom kategorikal: {list(categorical_cols)}")

# One-Hot Encoding
encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
X_encoded_cats = encoder.fit_transform(X[categorical_cols])

# Buat nama kolom baru hasil encoding
encoded_cols = encoder.get_feature_names_out(categorical_cols)
X_encoded_cats_df = pd.DataFrame(X_encoded_cats, columns=encoded_cols, index=X.index)

# Gabungkan kembali dengan kolom numerik
X_processed = pd.concat([X.drop(categorical_cols, axis=1), X_encoded_cats_df], axis=1)

# Simpan nama kolom TERAKHIR
FINAL_COLUMNS = X_processed.columns.tolist()
with open(f"{MODEL_STORE_PATH}/feature_columns.json", 'w') as f:
    json.dump(FINAL_COLUMNS, f)
print(f"✓ Preprocessing selesai. {len(FINAL_COLUMNS)} fitur digunakan.")

# --- 2. Train/Test Split ---
print("\n--- Train/Test Split ---")

# Adjust test size based on data size
if len(X_processed) < 100:
    test_size = 0.3
elif len(X_processed) < 500:
    test_size = 0.25
else:
    test_size = 0.2

X_train, X_test, y_train, y_test = train_test_split(
    X_processed, y, 
    test_size=test_size, 
    random_state=42, 
    stratify=y
)

print(f"Train set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples")

if len(X_test) < 10:
    print("WARNING: Test set terlalu kecil! Evaluasi mungkin tidak reliable.")

# --- 3. Handle Imbalance ---
neg_count = y_train.value_counts()[0]
pos_count = y_train.value_counts()[1]
scale_pos_weight = neg_count / pos_count
print(f"\nScale Pos Weight: {scale_pos_weight:.2f}")

# --- 4. Training Model XGBoost ---
print("\n--- Training XGBoost Model ---")
xgb_model = xgb.XGBClassifier(
    objective='binary:logistic',
    eval_metric='logloss',
    use_label_encoder=False,
    scale_pos_weight=scale_pos_weight,
    max_depth=3,
    learning_rate=0.1,
    n_estimators=100,
    random_state=42
)

xgb_model.fit(X_train, y_train)
print("✓ Model XGBoost berhasil dilatih.")

# --- 5. Evaluasi Model ---
print("\n--- Model Evaluation ---")
y_pred = xgb_model.predict(X_test)
y_pred_proba = xgb_model.predict_proba(X_test)[:, 1]

print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"TN: {cm[0,0]}, FP: {cm[0,1]}")
print(f"FN: {cm[1,0]}, TP: {cm[1,1]}")

roc_auc = roc_auc_score(y_test, y_pred_proba)
print(f"\nROC AUC Score: {roc_auc:.4f}")

if roc_auc < 0.6:
    print("⚠ WARNING: ROC AUC sangat rendah.")
elif roc_auc > 0.95:
    print("⚠ WARNING: ROC AUC terlalu tinggi. Kemungkinan overfitting.")

# --- 6. SHAP Explainer ---
print("\n--- Creating SHAP Explainer ---")
try:
    explainer = shap.TreeExplainer(xgb_model)
    print("✓ SHAP Explainer berhasil dibuat.")
    
    # Test SHAP
    shap_test_sample = X_train.sample(min(100, len(X_train)))
    shap_values = explainer.shap_values(shap_test_sample)
    print(f"✓ SHAP values tested on {len(shap_test_sample)} samples.")
    
except Exception as e:
    print(f"⚠ WARNING: Gagal membuat SHAP explainer: {e}")
    explainer = None

# --- 7. Simpan Artefak Model ---
print("\n--- Saving Model Artifacts ---")

xgb_model.save_model(f"{MODEL_STORE_PATH}/lead_scorer.json")
print("✓ Model saved")

joblib.dump(encoder, f"{MODEL_STORE_PATH}/one_hot_encoder.joblib")
print("✓ Encoder saved")

if explainer is not None:
    joblib.dump(explainer, f"{MODEL_STORE_PATH}/shap_explainer.joblib")
    print("✓ SHAP Explainer saved")

print("\n" + "="*50)
print("✓ TRAINING COMPLETE")
print("="*50)
print(f"\nModel Performance:")
print(f"- ROC AUC: {roc_auc:.4f}")
print(f"- Training samples: {len(X_train)}")
print(f"- Test samples: {len(X_test)}")
print(f"- Features: {len(FINAL_COLUMNS)}")