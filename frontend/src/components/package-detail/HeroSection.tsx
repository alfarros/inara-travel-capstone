// src/components/package-detail/HeroSection.tsx
import { Package } from "@/data/packages"; // Import interface Package
import { Button } from "@/components/ui/button";
import { MessageCircle } from "lucide-react";

interface Props {
  pkg: Package; // Gunakan interface Package
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
      <div className="relative z-10 container mx-auto h-full flex items-center justify-center text-center text-white">
        <div>
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
