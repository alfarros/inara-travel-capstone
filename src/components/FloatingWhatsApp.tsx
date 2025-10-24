import { MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";

const FloatingWhatsApp = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const toggleVisibility = () => {
      if (window.pageYOffset > 300) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener("scroll", toggleVisibility);
    return () => window.removeEventListener("scroll", toggleVisibility);
  }, []);

  const handleClick = () => {
    window.open(
      "https://wa.me/6281234567890?text=Assalamualaikum, saya ingin konsultasi tentang paket umrah",
      "_blank"
    );
  };

  return (
    <Button
      onClick={handleClick}
      size="lg"
      className={`fixed bottom-8 right-8 z-50 rounded-full w-16 h-16 shadow-large bg-accent hover:bg-accent/90 text-accent-foreground transition-all duration-300 ${
        isVisible ? "translate-y-0 opacity-100" : "translate-y-20 opacity-0"
      } hover:scale-110 animate-pulse`}
      aria-label="Chat on WhatsApp"
    >
      <MessageCircle className="w-8 h-8" />
    </Button>
  );
};

export default FloatingWhatsApp;
