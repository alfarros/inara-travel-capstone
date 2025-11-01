// src/data/packages.ts
export interface Package {
  id: number;
  title: string;
  duration: string;
  price: string;
  features: string[];
  image: string; // Akan diisi dengan import gambar
  featured?: boolean;
}

// Import gambar di sini agar tidak membebani komponen
import jamaahImage from "@/assets/jamaah-group.jpg";

export const packagesData: Package[] = [
  {
    id: 1,
    title: "Paket Premium",
    duration: "9 Hari",
    price: "Rp 28.000.000",
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
    title: "Paket Bronze",
    duration: "15 Hari",
    price: "Rp 20.000.000",
    features: [
      "Hotel Bintang 3 (500m dari Masjidil Haram)",
      "Penerbangan Transit 1x",
      "Breakfast Only",
      "Ziarah Utama",
    ],
    image: jamaahImage,
  },
  {
    id: 5,
    title: "Paket Bronze",
    duration: "15 Hari",
    price: "Rp 20.000.000",
    features: [
      "Hotel Bintang 3 (500m dari Masjidil Haram)",
      "Penerbangan Transit 1x",
      "Breakfast Only",
      "Ziarah Utama",
    ],
    image: jamaahImage,
  },
  // ... tambahkan paket lainnya jika perlu, pastikan tidak duplikat
];
