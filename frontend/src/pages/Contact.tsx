// src/pages/Contact.tsx
import { Button } from "@/components/ui/button";
import { MessageCircle, Phone, Mail, MapPin } from "lucide-react";

export default function Contact() {
  const whatsappNumber = "6281234567890";
  const whatsappMessage = "Assalamualaikum, saya ingin konsultasi tentang paket umrah.";

  return (
    <>
      <main className="py-20 px-4 bg-background">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-3xl md:text-5xl font-serif font-bold text-primary mb-6">
            Siap Menjawab Panggilan-Nya?
          </h1>
          <p className="text-lg text-muted-foreground mb-8">
            Raih maghfirah bersama Inara Travel — Umrah pertama yang berkesan, sesuai tuntunan Rasulullah SAW.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button asChild size="lg" className="bg-accent text-primary hover:scale-105">
              <a
                href={`https://wa.me/${whatsappNumber}?text=${encodeURIComponent(whatsappMessage)}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                <MessageCircle className="mr-2 h-5 w-5" />
                Konsultasi via WhatsApp
              </a>
            </Button>
            
            {/* Anda bisa menambahkan opsi kontak lain di sini */}
            <Button variant="outline" size="lg" asChild>
              <a href="tel:+6281234567890">
                <Phone className="mr-2 h-5 w-5" />
                Hubungi Kami
              </a>
            </Button>
          </div>

          {/* Informasi kontak lengkap bisa ditambahkan di bawah */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
            <div className="flex flex-col items-center text-center">
              <MapPin className="h-8 w-8 text-primary mb-2" />
              <h3 className="font-semibold">Alamat</h3>
              <p className="text-sm text-muted-foreground">Jl. Tidak tahu menahu 404, Atlantis</p>
            </div>
            <div className="flex flex-col items-center text-center">
              <Phone className="h-8 w-8 text-primary mb-2" />
              <h3 className="font-semibold">Telepon</h3>
              <p className="text-sm text-muted-foreground">+62 822-8192-4357</p>
            </div>
            <div className="flex flex-col items-center text-center">
              <Mail className="h-8 w-8 text-primary mb-2" />
              <h3 className="font-semibold">Email</h3>
              <p className="text-sm text-muted-foreground">info@inaratravel.com</p>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}