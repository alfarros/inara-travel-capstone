// src/pages/Contact.tsx
import { Button } from '@/components/ui/button';

export default function Contact() {
  return (
    <section className="py-20 px-4 bg-background">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-3xl md:text-5xl font-serif font-bold text-primary mb-6">
          Siap Menjawab Panggilan-Nya?
        </h1>
        <p className="text-lg text-muted-foreground mb-8">
          Raih maghfirah bersama Inara Travel — Umrah pertama yang berkesan, sesuai tuntunan Rasulullah SAW.
        </p>
        <Button asChild>
          <a
            href="https://wa.me/6281234567890"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-accent text-primary hover:scale-105"
          >
            Konsultasi Gratis via WhatsApp
          </a>
        </Button>
      </div>
    </section>
  );
}