// src/components/package-detail/HeroSection.tsx
import { Package } from "@/data/packages";
import { Button } from "@/components/ui/button";
import { MessageCircle, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

interface Props {
  pkg: Package;
}

export const HeroSection: React.FC<Props> = ({ pkg }) => {
  const handleWhatsAppClick = () => {
    const message = `Assalamualaikum, saya tertarik dengan paket ${pkg.title}. Mohon info lebih lanjut.`;
    window.open(
      `https://wa.me/6281234567890?text=${encodeURIComponent(message)}`,
      "_blank"
    );
  };

  return (
    <section className="relative h-96 overflow-hidden">
      <img
        src={pkg.image}
        alt={pkg.title}
        className="absolute inset-0 w-full h-full object-cover"
      />
      <div className="absolute inset-0 bg-black/50" />

      {/* 
        Ganti div 'container' dengan div yang menggunakan flexbox.
        Ini memungkinkan kita meletakkan item di pojok.
      */}
      <div className="relative z-10 h-full flex flex-col justify-center text-white">
        {/* Tombol Kembali di Pojok Kiri Atas */}
        <div className="container mx-auto px-4 pt-4">
          <Button
            variant="ghost"
            asChild
            className="text-white hover:bg-white/20"
          >
            <Link to="/packages">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Kembali
            </Link>
          </Button>
        </div>

        {/* Konten Utama Hero (Tetap di Tengah) */}
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-4">{pkg.title}</h1>
          <p className="text-xl mb-6">
            {pkg.duration} | Berangkat dari {pkg.departureCity}
          </p>
          <Button size="lg" onClick={handleWhatsAppClick}>
            <MessageCircle className="mr-2 h-5 w-5" />
            Konsultasi via WhatsApp
          </Button>
        </div>
      </div>
    </section>
  );
};
