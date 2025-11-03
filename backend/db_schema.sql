-- /db_schema.sql (Versi Pangkas - 2 Tabel)

-- Tabel 1: Packages (Untuk Knowledge Base AI)
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

-- Tabel 2: Reviews (Untuk Knowledge Base AI)
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    user_id INT,
    package_id INT REFERENCES packages(package_id) ON DELETE SET NULL,
    review_text TEXT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    -- Kita hapus semua kolom Modul 3
);

-- Data Dummy
INSERT INTO packages (name, description, price, duration_days, hotel_info, destination, category) VALUES
('Umrah Reguler 9 Hari', 'Paket umrah reguler 9 hari.', 19500000, 9, 'Hotel Bintang 4', 'Makkah, Madinah', 'Umrah Reguler'),
('Umrah Plus Turki 12 Hari', 'Paket umrah 12 hari plus wisata ke Istanbul.', 29000000, 12, 'Hotel Bintang 5', 'Makkah, Madinah, Istanbul', 'Umrah Plus');

INSERT INTO reviews (user_id, package_id, review_text, rating) VALUES
(1, 1, 'Hotelnya bagus dan dekat dengan masjid.', 5),
(2, 2, 'Makanannya enak dan pemandunya ramah.', 4);