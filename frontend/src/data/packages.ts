// src/data/packages.ts
export interface Package {
  id: number;
  title: string;
  duration: string;
  price: string;
  features: string[];
  image: string;
  featured?: boolean;
  // Tambahkan beberapa field baru agar detail halaman lebih kaya
  description: string;
  airline: string;
  departureCity: string;
}


// Import gambar
import jamaahImage from "@/assets/jamaah-group.jpg";

export const packagesData: Package[] = [
  {
    id: 1,
    title: "Paket Premium",
    duration: "9 Hari",
    price: "Rp 28.000.000",
    description:
      "Nikmati kemewahan dan kenyamanan pelayanan tertinggi dengan hotel berbintang 5 yang berlokasi sangat dekat dengan Masjidil Haram.",
    airline: "Garuda Indonesia",
    departureCity: "Jakarta",
    features: [
      "Hotel Bintang 5 (100m dari Masjidil Haram)",
      "Penerbangan Langsung",
      "Full Board Meals",
      "Ziarah Lengkap",
    ],
    image: jamaahImage,
  },
  {
    id: 2,
    title: "Paket Silver",
    duration: "12 Hari",
    price: "Rp 24.000.000",
    description:
      "Pilihan seimbang antara harga dan fasilitas. Nikmati perjalanan ibadah yang nyaman dengan hotel bintang 4.",
    airline: "Saudi Arabian Airlines",
    departureCity: "Jakarta",
    features: [
      "Hotel Bintang 4 (300m dari Masjidil Haram)",
      "Penerbangan Transit 1x",
      "Breakfast & Dinner",
      "Ziarah Lengkap",
    ],
    image: jamaahImage,
    featured: true,
  },
  {
    id: 3,
    title: "Paket Bronze",
    duration: "15 Hari",
    price: "Rp 20.000.000",
    description:
      "Pilihan ekonomis untuk menjalankan ibadah umrah dengan pelayanan yang tetap fokus pada kenyamanan dan kelancaran ibadah.",
    airline: "Batik Air",
    departureCity: "Surabaya",
    features: [
      "Hotel Bintang 3 (500m dari Masjidil Haram)",
      "Penerbangan Transit 1x",
      "Breakfast Only",
      "Ziarah Utama",
    ],
    image: jamaahImage,
  },
  {
    id: 4,
    title: "Paket Hemat",
    duration: "10 Hari",
    price: "Rp 18.500.000",
    description:
      "Pilihan paling ekonomis tanpa mengabaikan kenyamanan ibadah utama.",
    airline: "Lion Air",
    departureCity: "Medan",
    features: [
      "Hotel Bintang 3",
      "Penerbangan Transit 1x",
      "Breakfast Only",
      "Ziarah Utama",
    ],
    image: jamaahImage,
  },
  {
    id: 5,
    title: "Paket Keluarga",
    duration: "12 Hari",
    price: "Rp 95.000.000",
    description:
      "Paket khusus untuk keluarga dengan fasilitas hotel yang lebih luas dan makanan sesuai selera.",
    airline: "Emirates",
    departureCity: "Jakarta",
    features: [
      "Hotel Apartemen (1 Kamar Tidur)",
      "Penerbangan Langsung",
      "Full Board Meals",
      "Ziarah Lengkap",
      "Tour Guide Khusus",
    ],
    image: jamaahImage,
  },
  // Hapus duplikat dan tambahkan paket lain jika perlu
];
