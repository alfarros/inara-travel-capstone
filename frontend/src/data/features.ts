import { LucideIcon } from "lucide-react";
import { Heart, Users, BookOpen } from "lucide-react";
import nyamanImage from "/public/assets/feature-nyaman.jpg";
import terbimbingImage from "/public/assets/feature-terbimbing.jpg";
import sunnahImage from "/public/assets/feature-sunnah.jpg";
export interface Feature {
    icon: LucideIcon;
    title: string;
    description: string;    
    color: string;
    textColor: string;    
    image : string;
}


export const featuresData: Feature[] = [
  {
    icon: Heart,
    title: "Nyaman",
    description:
      "Hotel dekat masjid, maskapai pilihan, makanan halal terjamin. Perjalanan ibadah Anda dijamin nyaman dan menenangkan.",
    color: "bg-green-light",
    textColor: "text-foreground",
    image: nyamanImage,
  },
  {
    icon: Users,
    title: "Terbimbing",
    description:
      "Ustadz pendamping berpengalaman, manasik offline & online. Kami memastikan Anda siap dan paham setiap rukun ibadah.",
    color: "bg-secondary",
    textColor: "text-secondary-foreground",
    image: terbimbingImage,
  },
  {
    icon: BookOpen,
    title: "Sunnah",
    description:
      "Ibadah sesuai tuntunan, kajian harian, suasana khusyu. Mengikuti jejak Rasulullah SAW dalam setiap langkah.",
    color: "bg-green-olive",
    textColor: "text-primary-foreground",
    image: sunnahImage,
  },
];
