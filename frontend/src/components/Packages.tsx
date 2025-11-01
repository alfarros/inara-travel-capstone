// src/components/Packages.tsx
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar, MapPin, Star } from "lucide-react";
import { useState, useCallback, useMemo } from "react";
import { packagesData, Package } from "@/data/packages"; // Import dari file data

interface PackagesProps {
  showLoadMore?: boolean;
  limit?: number;
}

const Packages = ({ showLoadMore = false, limit = 3 }: PackagesProps) => {
  const [visibleCount, setVisibleCount] = useState(limit);

  const loadMore = () => {
    setVisibleCount((prev) => Math.min(prev + limit, packagesData.length));
  };

  // useMemo untuk mencegah perhitungan ulang setiap render
  const displayedPackages = useMemo(() => {
    return showLoadMore
      ? packagesData.slice(0, visibleCount)
      : packagesData.slice(0, limit);
  }, [showLoadMore, visibleCount, limit]);

  // useCallback untuk mencegah pembuatan ulang fungsi
  const handleWhatsAppClick = useCallback((packageTitle: string) => {
    const message = `Assalamualaikum, saya tertarik dengan ${packageTitle}. Mohon info lebih lanjut.`;
    window.open(
      `https://wa.me/6281234567890?text=${encodeURIComponent(message)}`,
      "_blank"
    );
  }, []);

  return (
    <section
      className="py-20 px-4 bg-muted/30"
      aria-labelledby="packages-heading"
    >
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16 animate-fade-in-up">
          <h2
            id="packages-heading"
            className="text-3xl md:text-5xl font-serif font-bold text-primary mb-4"
          >
            Paket Umrah Pilihan
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Pilih paket yang sesuai dengan kebutuhan dan budget Anda
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {displayedPackages.map((pkg, index) => (
            <PackageCard
              key={pkg.id}
              pkg={pkg}
              index={index}
              onWhatsAppClick={handleWhatsAppClick}
            />
          ))}
        </div>

        {showLoadMore && visibleCount < packagesData.length && (
          <div className="text-center mt-8">
            <Button onClick={loadMore} variant="outline" size="lg">
              Muat Lebih Banyak
            </Button>
          </div>
        )}

        <div className="text-center mt-12 text-sm text-muted-foreground">
          <p>
            * Harga dapat berubah sewaktu-waktu. Hubungi kami untuk penawaran
            terbaru.
          </p>
        </div>
      </div>
    </section>
  );
};

// Pisahkan kartu paket menjadi komponen terpisah untuk kemudahan membaca dan pemeliharaan
interface PackageCardProps {
  pkg: Package;
  index: number;
  onWhatsAppClick: (title: string) => void;
}

const PackageCard: React.FC<PackageCardProps> = ({
  pkg,
  index,
  onWhatsAppClick,
}) => {
  return (
    <Card
      className={`overflow-hidden shadow-medium hover:shadow-large transition-all duration-300 hover:-translate-y-2 bg-card border-2 ${
        pkg.featured ? "border-accent" : "border-border"
      } animate-scale-in`}
      style={{ animationDelay: `${index * 0.15}s` }}
    >
      {pkg.featured && (
        <div className="bg-gradient-accent text-accent-foreground text-center py-2 font-semibold flex items-center justify-center gap-2">
          <Star className="w-4 h-4 fill-current" />
          Paling Populer
        </div>
      )}

      <div className="relative h-48 overflow-hidden">
        <img
          src={pkg.image}
          alt={pkg.title}
          className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        <div className="absolute bottom-4 left-4 text-white">
          <h3 className="text-2xl font-serif font-bold">{pkg.title}</h3>
        </div>
      </div>

      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Calendar className="w-4 h-4" />
            <span className="text-sm">{pkg.duration}</span>
          </div>
          <div className="text-2xl font-bold text-primary">{pkg.price}</div>
        </div>
      </CardHeader>

      <CardContent>
        <ul className="space-y-3">
          {pkg.features.map((feature, idx) => (
            <li key={idx} className="flex items-start gap-2 text-sm">
              <MapPin className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />
              <span className="text-muted-foreground">{feature}</span>
            </li>
          ))}
        </ul>
      </CardContent>

      <CardFooter>
        <Button
          onClick={() => onWhatsAppClick(pkg.title)}
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground transition-all duration-300"
        >
          Lihat Detail
        </Button>
      </CardFooter>
    </Card>
  );
};

export default Packages;
