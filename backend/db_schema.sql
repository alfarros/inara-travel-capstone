-- /module_5_pricing_monitor/db_schema.sql (VERSI LENGKAP & DIPERBAIKI)

-- Tabel untuk Modul 5: Competitor Price Monitor
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    competitor_name VARCHAR(255) NOT NULL,
    package_name_scraped TEXT,
    price NUMERIC(12, 2) NOT NULL,
    scrape_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_url TEXT,
    notes TEXT
);

-- Tabel untuk Modul 3: Sentiment & Review Intelligence
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    package_id INT,
    review_text TEXT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    sentiment VARCHAR(50),
    sentiment_score FLOAT,
    aspect VARCHAR(255),
    priority VARCHAR(50),
    source VARCHAR(50), -- 'web', 'whatsapp', 'google'
    
    -- [PERBAIKAN 1] Tambahkan kolom 'sentiment_status'
    -- Ini adalah kolom yang menyebabkan error 'does not exist'
    sentiment_status VARCHAR(50) DEFAULT 'pending',

    -- [PERBAIKAN 2] Kembalikan nama 'timestamp' menjadi 'created_at'
    -- agar sesuai dengan dashboard.py
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Contoh data dummy untuk Modul 3 (akan diproses oleh scheduler)
-- Kita set 'sentiment_status' sebagai 'pending'
INSERT INTO reviews (user_id, review_text, rating, source, sentiment_status) VALUES
('user001', 'Hotelnya kotor dan AC tidak dingin, sangat kecewa dengan penginapan.', 1, 'web', 'pending'),
('user002', 'Makanannya kurang variatif, menunya itu-itu saja selama 5 hari.', 3, 'whatsapp', 'pending');

-- Indexing untuk mempercepat query
CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(scrape_timestamp);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment);

-- [PERBAIKAN 3] Tambahkan index untuk kolom status
CREATE INDEX IF NOT EXISTS idx_reviews_status ON reviews(sentiment_status);