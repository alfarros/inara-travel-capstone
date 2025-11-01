import { Button } from "@/components/ui/button";
import { MessageCircle } from "lucide-react";
import heroImage from "@/assets/hero-mosque.jpg";
import { useCallback } from "react";

const Hero = () => {
  const handleWhatsAppClick = useCallback(() => {
    const message = encodeURIComponent(
      "Assalamualaikum, saya ingin konsultasi tentang paket umrah"
    );
    window.open(`https://wa.me/6281234567890?text=${message}`, "_blank");
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `url(${heroImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >
        <div className="absolute inset-0 bg-gradient-primary opacity-80" />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in-up">
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-serif font-bold text-primary-foreground leading-tight">
            Nyaman, Terbimbing, Sunnah
          </h1>

          <p className="text-lg md:text-xl lg:text-2xl text-primary-foreground/90 font-light max-w-3xl mx-auto leading-relaxed">
            Raih maghfirah bersama Inara Travel — Umrah pertama yang berkesan,
            sesuai tuntunan Rasulullah SAW.
          </p>

          <div className="pt-8">
            <Button
              size="lg"
              onClick={handleWhatsAppClick}
              className="bg-accent hover:bg-accent/90 text-accent-foreground font-semibold px-8 py-6 text-lg rounded-full shadow-large transition-all duration-300 hover:scale-105"
            >
              <MessageCircle className="mr-2 h-5 w-5" />
              Konsultasi Gratis via WhatsApp
            </Button>
          </div>
        </div>
      </div>

      {/* Decorative Bottom Wave */}
      <div className="absolute bottom-0 left-0 right-0 z-10" aria-hidden="true">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 1440 120"
          className="w-full"
        >
          <path
            fill="hsl(var(--background))"
            d="M0,64L80,69.3C160,75,320,85,480,80C640,75,800,53,960,48C1120,43,1280,53,1360,58.7L1440,64L1440,120L1360,120C1280,120,1120,120,960,120C800,120,640,120,480,120C320,120,160,120,80,120L0,120Z"
          />
        </svg>
      </div>
    </section>
  );
};

export default Hero;
