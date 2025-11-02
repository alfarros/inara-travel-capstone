-- /db_schema.sql
-- Ini adalah "Cetak Biru" (Source of Truth) untuk SELURUH database Anda
-- VERSI FINAL DENGAN FIX MODUL PAYMENTS

-- PENTING: Urutan pembuatan tabel sudah diatur untuk Foreign Keys

-- Tabel untuk Modul 1 & 2: Users (Akun)
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabel untuk Modul 1: Web Users (untuk notifikasi chat)
CREATE TABLE IF NOT EXISTS web_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    notification_enabled BOOLEAN DEFAULT TRUE
);

-- Tabel untuk Modul 2: Packages (Sesuai diagram terbaru Anda)
CREATE TABLE IF NOT EXISTS packages (
    package_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price BIGINT NOT NULL,
    duration_days INT,
    hotel_info VARCHAR(500),
    image_url VARCHAR(500),
    destination VARCHAR(255),
    category VARCHAR(100)
);

-- Tabel untuk Modul 2: Bookings
CREATE TABLE IF NOT EXISTS bookings (
    booking_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE SET NULL,
    package_id INT REFERENCES packages(package_id) ON DELETE SET NULL,
    order_id VARCHAR(255) UNIQUE NOT NULL,
    total_amount BIGINT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    
    -- [FIX] Menambahkan kolom yang hilang untuk Modul Payments
    midtrans_redirect_url TEXT, 
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabel untuk Modul 2: Interactions (Data training)
CREATE TABLE IF NOT EXISTS interactions (
    interaction_id SERIAL PRIMARY KEY,
    user_id INT, -- Bisa jadi user anonim, jadi tidak perlu REFERENCES
    package_id INT REFERENCES packages(package_id) ON DELETE SET NULL,
    event_type VARCHAR(50), -- 'view', 'book', 'review'
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_duration_sec INT,
    pages_viewed INT
);

-- Tabel untuk Modul 3: Reviews (Skema lengkap)
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    user_id INT, -- Bisa jadi user anonim
    package_id INT REFERENCES packages(package_id) ON DELETE SET NULL,
    review_text TEXT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    sentiment VARCHAR(50),
    sentiment_score FLOAT,
    aspect VARCHAR(255),
    priority VARCHAR(50),
    source VARCHAR(50), -- 'web', 'whatsapp', 'google'
    sentiment_status VARCHAR(50) DEFAULT 'pending', 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabel untuk Modul 1: Admin Messages (Eskalasi)
CREATE TABLE IF NOT EXISTS admin_messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    channel VARCHAR(50) NOT NULL, -- "web" atau "whatsapp"
    user_message TEXT NOT NULL,
    ai_response TEXT,
    escalation_reason VARCHAR(500),
    user_contact VARCHAR(255), -- Email atau nomor WA
    status VARCHAR(50) DEFAULT 'pending', -- "pending" atau "resolved"
    admin_reply TEXT,
    admin_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Tabel untuk Modul 5: Price History (Monitoring)
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    competitor_name VARCHAR(255) NOT NULL,
    package_name_scraped TEXT,
    price NUMERIC(12, 2) NOT NULL,
    scrape_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_url TEXT,
    notes TEXT
);

-- === CONTOH DATA DUMMY ===
-- (Dijalankan hanya saat database pertama kali dibuat)

-- Data dummy untuk 'packages' (untuk Modul 2)
INSERT INTO packages (name, description, price, duration_days, hotel_info, destination, category) VALUES
('Umrah Reguler 9 Hari', 'Paket umrah reguler 9 hari keberangkatan setiap bulan.', 19500000, 9, 'Hotel Bintang 4 (Dekat Masjidil Haram)', 'Makkah, Madinah', 'Umrah Reguler'),
('Umrah Plus Turki 12 Hari', 'Paket umrah 12 hari plus wisata ke Istanbul dan Bursa.', 29000000, 12, 'Hotel Bintang 5', 'Makkah, Madinah, Istanbul, Bursa', 'Umrah Plus'),
('Haji Plus Cepat', 'Paket haji plus dengan antrian cepat 5-7 tahun.', 150000000, 25, 'Hotel Bintang 5 Eksklusif', 'Makkah, Madinah, Mina, Arafah', 'Haji Plus')
ON CONFLICT (package_id) DO NOTHING;

-- Data dummy untuk 'reviews' (untuk Modul 3)
INSERT INTO reviews (user_id, package_id, review_text, rating, source, sentiment_status) VALUES
(1, 1, 'Hotelnya kotor dan AC tidak dingin, sangat kecewa dengan penginapan.', 1, 'web', 'pending'),
(2, 2, 'Makanannya kurang variatif, menunya itu-itu saja selama 5 hari.', 3, 'whatsapp', 'pending'),
(3, 2, 'Pemandu (muthawif) sangat sabar dan jelas menerangkan, luar biasa!', 5, 'web', 'pending')
ON CONFLICT (review_id) DO NOTHING;

-- === INDEXING ===
-- (Untuk mempercepat query)
CREATE INDEX IF NOT EXISTS idx_reviews_status ON reviews(sentiment_status);
CREATE INDEX IF NOT EXISTS idx_admin_messages_status ON admin_messages(status);
CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_package ON bookings(package_id);