// frontend/src/lib/api.ts

// --- BASE URLS ---
const CHAT_API_BASE_URL = "http://localhost:8008"; // Sesuaikan dengan port backend chatbot Anda
const PACKAGES_API_BASE_URL = "http://localhost:8009"; // Sesuaikan dengan port backend packages/ulasan Anda

// --- ENDPOINTS ---
export const chatEndpoint = `${CHAT_API_BASE_URL}/chat`;

// --- INTERFACES / TYPES ---

// Interfaces untuk Packages & Reviews (Sesuaikan dengan schema dari backend packages_reviews dan db_schema.sql)
// Pastikan schema Pydantic dan model SQLAlchemy di backend juga mencerminkan perubahan ini.
export interface ApiPackage {
  package_id: number;
  name: string; // Berubah dari 'title'
  duration: string | null; // Kolom baru: durasi dalam bentuk string seperti "9 Hari"
  price: number; // Harga dalam bentuk angka
  features: string[] | null; // Kolom baru: Array string untuk features
  image_url: string | null; // Berubah dari 'image'
  featured: boolean | null; // Kolom baru: boolean untuk featured
  description: string | null;
  airline: string | null; // Kolom baru
  departure_city: string | null; // Kolom baru: departureCity -> departure_city (snake_case)

  // Kolom lama dari skema awal (bisa tetap ada jika ingin dipertahankan di DB dan API)
  duration_days: number | null; // Bisa dipertahankan untuk perhitungan
  hotel_info: string | null; // Bisa dipertahankan
  destination: string | null; // Bisa dipertahankan
  category: string | null; // Bisa dipertahankan
}

export interface ApiReview {
  review_id: number;
  user_id: number | null;
  package_id: number;
  review_text: string;
  rating: number;
  created_at: string; // ISO date string
}

export interface ApiPackageWithReviews extends ApiPackage {
  reviews: ApiReview[];
}

// Interfaces untuk Chat (Sesuaikan dengan schema dari backend chatbot)
export interface ChatMessage {
  sender: "user" | "bot";
  text: string;
}

export interface ChatRequest {
  user_id: string;
  message: string;
  user_email?: string;
}

export interface ChatResponse {
  user_id: string;
  response_text: string; // Berubah dari 'text' di frontend lama
  source: string;
  escalated: boolean;
  escalation_reason?: string;
}

// --- API FUNCTIONS ---

// Fungsi untuk mengambil semua paket
export const fetchPackages = async (): Promise<ApiPackage[]> => {
  const response = await fetch(`${PACKAGES_API_BASE_URL}/packages`);
  if (!response.ok) {
    throw new Error(`Gagal mengambil paket: ${response.statusText}`);
  }
  const data = await response.json();
  // Pastikan struktur respons sesuai { packages: [...] }
  if (!data || !Array.isArray(data.packages)) {
    throw new Error("Respons API paket tidak valid.");
  }
  return data.packages;
};

// Fungsi untuk mengambil detail paket
export const fetchPackageDetail = async (
  id: number
): Promise<ApiPackageWithReviews> => {
  const response = await fetch(`${PACKAGES_API_BASE_URL}/packages/${id}`);
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Paket tidak ditemukan.");
    }
    throw new Error(`Gagal mengambil detail paket: ${response.statusText}`);
  }
  const data = await response.json();
  // Respons langsung berupa objek paket lengkap dengan reviews
  return data;
};

// Fungsi untuk membuat review baru
export const createReview = async (
  reviewData: Omit<ApiReview, "review_id" | "created_at">
): Promise<ApiReview> => {
  const response = await fetch(`${PACKAGES_API_BASE_URL}/reviews`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(reviewData),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Paket untuk review ini tidak ditemukan.");
    }
    throw new Error(`Gagal membuat review: ${response.statusText}`);
  }
  const data = await response.json();
  return data;
};

// Fungsi lain untuk API lainnya bisa ditambahkan di sini
