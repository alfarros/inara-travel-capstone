// src/components/package-detail/PriceAndBooking.tsx
import { Package } from "@/data/packages"; // Import interface Package
import { Button } from "@/components/ui/button";
import { MessageCircle } from "lucide-react";

interface Props {
  pkg: Package; // Terima seluruh object `pkg`
}

export const PriceAndBooking: React.FC<Props> = ({ pkg }) => {
  const handleBuyViaWhatsApp = () => {
    const phoneNumber = "6281234567890";

    const message = `
Assalamualaikum,

Saya tertarik untuk memesan paket umrah berikut:

*Paket:* ${pkg.title}
*Durasi:* ${pkg.duration}
*Harga:* ${pkg.price}
*Berangkat dari:* ${pkg.departureCity}

Mohon informasi lebih lanjut mengenai ketersediaan kursi dan jadwal keberangkatan.
    `.trim();

    const encodedMessage = encodeURIComponent(message);
    window.open(
      `https://wa.me/${phoneNumber}?text=${encodedMessage}`,
      "_blank"
    );
  };

  return (
    <section className="bg-muted/30 py-12 rounded-lg text-center">
      <h2 className="text-3xl font-bold mb-4">Investasi Ibadah Anda</h2>
      <p className="text-5xl font-bold text-primary mb-4">{pkg.price}</p>
      <p className="text-muted-foreground mb-8">
        *Harga dapat berubah sewaktu-waktu, hubungi kami untuk info terbaru.
      </p>

      <Button
        size="lg"
        onClick={handleBuyViaWhatsApp}
        className="bg-green-600 hover:bg-green-700 text-white"
      >
        <MessageCircle className="mr-2 h-5 w-5" />
        Beli Paket via WhatsApp
      </Button>

      <p className="text-sm text-muted-foreground mt-4">
        Tim kami akan segera menghubungi Anda melalui WhatsApp untuk melanjutkan
        proses pemesanan.
      </p>
    </section>
  );
};
