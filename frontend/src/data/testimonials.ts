// src/data/testimonials.ts
export interface Testimonial {
  id: number;
  name: string;
  location: string;
  rating: number;
  text: string;
  avatar: string;
}

export const testimonialsData: Testimonial[] = [
  {
    id: 1,
    name: "Bunda Rina Wijaya",
    location: "Jakarta Selatan",
    rating: 5,
    text: "Pertama kali umrah, tapi terasa seperti bareng keluarga sendiri. Ustadznya sabar banget ngejelasin tata cara ibadah. Alhamdulillah pengalaman yang luar biasa!",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Rina",
  },
  {
    id: 2,
    name: "Pak Ahmad Fauzi",
    location: "Bandung",
    rating: 5,
    text: "Pelayanan ramah, hotel strategis dekat masjid, dan makanannya enak-enak. Semua berjalan lancar tanpa hambatan. Jazakumullah khairan!",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Ahmad",
  },
  {
    id: 3,
    name: "Ibu Siti Nurhaliza",
    location: "Surabaya",
    rating: 5,
    text: "Inara Travel benar-benar memperhatikan detail. Dari manasik sampai di tanah suci, semuanya terbimbing dengan baik. Recommended banget!",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Siti",
  },
];
