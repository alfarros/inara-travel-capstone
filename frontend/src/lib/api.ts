// frontend/src/lib/api.ts

// --- BASE URLS ---
// Pisahkan base URL untuk modul yang berbeda
const CHAT_API_BASE_URL = "http://localhost:8008"; // Sesuaikan dengan port backend chatbot Anda
const PACKAGES_API_BASE_URL = "http://localhost:8009"; // Sesuaikan dengan port backend packages/ulasan Anda

// --- ENDPOINTS ---
export const chatEndpoint = `${CHAT_API_BASE_URL}/chat`;
// Tidak perlu mendefinisikan endpoint untuk packages/reviews di sini jika sudah dihandle di fungsi masing-masing

// --- INTERFACES / TYPES ---

// Interfaces untuk Packages & Reviews (Sesuaikan dengan schema dari backend packages_reviews)
export interface ApiPackage {
  package_id: number;
  name: string; // Berubah dari 'title'
  description: string | null;
  price: number; // Harga dalam bentuk angka
  duration_days: number | null; // Berubah dari 'duration'
  hotel_info: string | null;
  image_url: string | null; // Berubah dari 'image'
  destination: string | null;
  category: string | null;
  // Tidak ada 'featured', 'airline', 'departureCity', 'features' di schema backend sebelumnya
  // Jika Anda ingin menambahkannya ke DB/API, sesuaikan interface ini
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

// Interfaces untuk Testimonials (Jika ingin dipindah dari data statis ke API nanti)
// export interface Testimonial { ... } // Tidak dibuat sekarang

// --- API FUNCTIONS ---

// Fungsi untuk mengambil semua paket
export const fetchPackages = async (): Promise<ApiPackage[]> => {
  console.log(
    "Mengambil data paket dari:",
    `${PACKAGES_API_BASE_URL}/packages`
  );
  try {
    const response = await fetch(`${PACKAGES_API_BASE_URL}/packages`);
    console.log("Status Response:", response.status);
    if (!response.ok) {
      throw new Error(`Gagal mengambil paket: ${response.statusText}`);
    }
    const data = await response.json();
    console.log("Data Paket:", data); // Log data yang diterima
    return data.packages;
  } catch (error) {
    console.error("Error di fetchPackages:", error);
    throw error;
  }
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

// Fungsi untuk mengirim pesan chat (digunakan oleh useChat)
// Ini bisa didefinisikan di sini atau langsung di useChat.ts, tergantung preferensi.
// Karena useChat.ts sudah mengimpor chatEndpoint, ini cukup sebagai definisi endpoint dan tipe.
// Fungsi pengiriman utama tetap di useChat.ts
// export const sendChatMessage = async (chatData: ChatRequest): Promise<ChatResponse> => {
//   const response = await fetch(chatEndpoint, {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify(chatData),
//   });
//   if (!response.ok) throw new Error(`Gagal mengirim pesan: ${response.statusText}`);
//   return response.json(); // Ini akan mengembalikan ChatResponse
// };

// Fungsi lain untuk API lainnya bisa ditambahkan di sini
