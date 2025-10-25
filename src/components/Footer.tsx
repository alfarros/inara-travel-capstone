import { Mail, Instagram, Youtube, MapPin, Phone } from "lucide-react";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-primary text-primary-foreground">
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div className="space-y-4">
            <h3 className="text-2xl font-serif font-bold">Inara Travel</h3>
            <p className="text-primary-foreground/80 text-sm leading-relaxed">
              Melayani ummat dengan sepenuh hati. Umrah dan haji yang nyaman, terbimbing, dan sesuai sunnah.
            </p>
          </div>

          {/* Contact */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold">Hubungi Kami</h4>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-2">
                <MapPin className="w-4 h-4 mt-1 flex-shrink-0" />
                <span className="text-primary-foreground/80">
                  Jl. Tidak tahu menahu 404, Atlantis, Indonesia
                </span>
              </li>
              <li className="flex items-center gap-2">
                <Phone className="w-4 h-4 flex-shrink-0" />
                <a 
                  href="tel:+6282281924357" 
                  className="text-primary-foreground/80 hover:text-accent transition-colors"
                >
                  +62 822-8192-4357
                </a>
              </li>
              <li className="flex items-center gap-2">
                <Mail className="w-4 h-4 flex-shrink-0" />
                <a 
                  href="mailto:info@inaratravel.com" 
                  className="text-primary-foreground/80 hover:text-accent transition-colors"
                >
                  info@inaratravel.com
                </a>
              </li>
            </ul>
          </div>

          {/* Social Media */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold">Ikuti Kami</h4>
            <div className="flex gap-4">
              <a
                href="https://instagram.com/inaratravel"
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-primary-foreground/10 hover:bg-accent rounded-full transition-all duration-300 hover:scale-110"
                aria-label="Instagram"
              >
                <Instagram className="w-5 h-5" />
              </a>
              <a
                href="https://youtube.com/@inaratravel"
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-primary-foreground/10 hover:bg-accent rounded-full transition-all duration-300 hover:scale-110"
                aria-label="YouTube"
              >
                <Youtube className="w-5 h-5" />
              </a>
            </div>
            <p className="text-sm text-primary-foreground/80 mt-4">
              Dapatkan update paket terbaru, tips ibadah, dan inspirasi spiritual dari kami.
            </p>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-primary-foreground/20 pt-8 text-center">
          <p className="text-sm text-primary-foreground/70">
            &copy; {currentYear} Inara Travel. All rights reserved.
          </p>
          <p className="text-xs text-primary-foreground/60 mt-2">
            Sedang dalam proses pengurusan izin resmi Kementerian Agama RI
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
