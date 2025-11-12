-- /db_schema.sql (Versi Diperbarui 2 - Menyesuaikan frontend/data/packages.ts dan tambahan reviewer_name di reviews)

-- Tabel 1: Packages (Menyesuaikan interface Package frontend)
CREATE TABLE IF NOT EXISTS packages (
    package_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,             -- Sesuai: title -> name
    duration VARCHAR(100),                  -- Tambahkan: durasi dalam bentuk string seperti "9 Hari"
    price BIGINT NOT NULL,                  -- Sesuai: Tapi sebaiknya harga dalam angka, bukan string
    -- price VARCHAR(255),                 -- Alternatif jika ingin menyimpan format string seperti "Rp 28.000.000"
    features TEXT[],                        -- Tambahkan: Array string untuk features (PostgreSQL array type)
    image_url VARCHAR(500),                 -- Sesuai: image -> image_url
    featured BOOLEAN DEFAULT FALSE,         -- Tambahkan: featured (default false)
    description TEXT,                       -- Sesuai
    airline VARCHAR(255),                   -- Tambahkan
    departure_city VARCHAR(255),            -- Tambahkan: departureCity -> departure_city (snake_case)
    -- Kolom lama yang bisa dipertahankan atau dihapus jika tidak relevan
    duration_days INT,                      -- Bisa dipertahankan untuk perhitungan, atau hapus jika cukup pakai 'duration'
    hotel_info VARCHAR(500),                -- Bisa dipertahankan
    destination VARCHAR(255),               -- Bisa dipertahankan
    category VARCHAR(100)                   -- Bisa dipertahankan
);

-- Tabel 2: Reviews (Diperbarui: ganti user_id dengan reviewer_name)
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    -- user_id INT,                       -- Hapus kolom ini
    reviewer_name VARCHAR(255) DEFAULT 'Anonim', -- Tambahkan kolom ini
    package_id INT REFERENCES packages(package_id) ON DELETE SET NULL,
    review_text TEXT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Data Dummy: Menyesuaikan dengan data frontend
INSERT INTO packages (
    name, duration, price, features, image_url, featured, description, airline, departure_city,
    duration_days, hotel_info, destination, category
) VALUES
(
    'Paket Premium',                        -- name
    '9 Hari',                               -- duration
    28000000,                               -- price (angka)
    ARRAY[                                 -- features (array of text)
        'Hotel Bintang 5 (100m dari Masjidil Haram)',
        'Penerbangan Langsung',
        'Full Board Meals',
        'Ziarah Lengkap'
    ],
    'http://localhost:8080/assets/jamaah-group.jpg', -- image_url (akan dijelaskan nanti)
    FALSE,                                  -- featured
    'Nikmati kemewahan dan kenyamanan pelayanan tertinggi dengan hotel berbintang 5 yang berlokasi sangat dekat dengan Masjidil Haram.',
    'Garuda Indonesia',                     -- airline
    'Jakarta',                            -- departure_city
    9,                                      -- duration_days
    'Hotel Bintang 5 (100m dari Masjidil Haram)', -- hotel_info
    'Makkah, Madinah',                    -- destination
    'Umrah Premium'                       -- category
),
(
    'Paket Silver',
    '12 Hari',
    24000000,
    ARRAY[
        'Hotel Bintang 4 (300m dari Masjidil Haram)',
        'Penerbangan Transit 1x',
        'Breakfast & Dinner',
        'Ziarah Lengkap'
    ],
    'http://localhost:8080/assets/jamaah-group.jpg',
    TRUE,                                   -- featured
    'Pilihan seimbang antara harga dan fasilitas. Nikmati perjalanan ibadah yang nyaman dengan hotel bintang 4.',
    'Saudi Arabian Airlines',
    'Jakarta',
    12,
    'Hotel Bintang 4 (300m dari Masjidil Haram)',
    'Makkah, Madinah',
    'Umrah Reguler'
),
(
    'Paket Bronze',
    '15 Hari',
    20000000,
    ARRAY[
        'Hotel Bintang 3 (500m dari Masjidil Haram)',
        'Penerbangan Transit 1x',
        'Breakfast Only',
        'Ziarah Utama'
    ],
    'http://localhost:8080/assets/jamaah-group.jpg',
    FALSE,
    'Pilihan ekonomis untuk menjalankan ibadah umrah dengan pelayanan yang tetap fokus pada kenyamanan dan kelancaran ibadah.',
    'Batik Air',
    'Surabaya',
    15,
    'Hotel Bintang 3 (500m dari Masjidil Haram)',
    'Makkah, Madinah',
    'Umrah Ekonomis'
),
(
    'Paket Hemat',
    '10 Hari',
    18500000,
    ARRAY[
        'Hotel Bintang 3',
        'Penerbangan Transit 1x',
        'Breakfast Only',
        'Ziarah Utama'
    ],
    'http://localhost:8080/assets/jamaah-group.jpg',
    FALSE,
    'Pilihan paling ekonomis tanpa mengabaikan kenyamanan ibadah utama.',
    'Lion Air',
    'Medan',
    10,
    'Hotel Bintang 3',
    'Makkah, Madinah',
    'Umrah Hemat'
),
(
    'Paket Keluarga',
    '12 Hari',
    95000000,
    ARRAY[
        'Hotel Apartemen (1 Kamar Tidur)',
        'Penerbangan Langsung',
        'Full Board Meals',
        'Ziarah Lengkap',
        'Tour Guide Khusus'
    ],
    'http://localhost:8080/assets/jamaah-group.jpg',
    FALSE,
    'Paket khusus untuk keluarga dengan fasilitas hotel yang lebih luas dan makanan sesuai selera.',
    'Emirates',
    'Jakarta',
    12,
    'Hotel Apartemen (1 Kamar Tidur)',
    'Makkah, Madinah',
    'Umrah Keluarga'
);

-- Data Dummy untuk Reviews (Diperbarui: gunakan reviewer_name)
INSERT INTO reviews (reviewer_name, package_id, review_text, rating) VALUES
('Bapak Rina Wijaya', 1, 'Hotelnya bagus dan dekat dengan masjid.', 5),
('Ibu Ahmad Fauzi', 2, 'Makanannya enak dan pemandunya ramah.', 4),
('Anonim', 1, 'Pelayanannya sangat memuaskan.', 5); -- Contoh ulasan anonim
