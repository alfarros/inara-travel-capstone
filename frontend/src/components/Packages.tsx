// frontend/src/components/Packages.tsx
import { useState, useMemo } from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar, MapPin, Star } from "lucide-react";
import { Link } from "react-router-dom";
import { ApiPackage } from "@/lib/api"; // Impor tipe API

interface PackagesSectionProps {
  initialPackages: ApiPackage[]; // Terima data dari luar
  showLoadMore?: boolean;
  limit?: number;
  title?: string;
}

const PackagesSection: React.FC<PackagesSectionProps> = ({
  initialPackages,
  showLoadMore = false,
  limit = 3,
  title = "Paket Umrah Pilihan",
}) => {
  const [visibleCount, setVisibleCount] = useState(limit);

  const loadMore = () => {
    setVisibleCount((prev) => Math.min(prev + limit, initialPackages.length));
  };

  // useMemo untuk mencegah perhitungan ulang setiap render
  const displayedPackages = useMemo(() => {
    return showLoadMore
      ? initialPackages.slice(0, visibleCount)
      : initialPackages.slice(0, limit);
  }, [showLoadMore, visibleCount, limit, initialPackages]);

  // Kita re-definisikan PackageCard di sini agar sesuai dengan struktur ApiPackage (baru)
  interface PackageCardProps {
    pkg: ApiPackage;
    index: number;
  }

  const PackageCard: React.FC<PackageCardProps> = ({ pkg, index }) => {
    // Konversi harga dari number ke format string
    const formattedPrice = new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      maximumFractionDigits: 0,
    }).format(pkg.price);

    // Gunakan field dari ApiPackage (baru)
    const isFeatured = pkg.featured || false;
    const durationText = pkg.duration || "Durasi Tidak Ditentukan";
    const title = pkg.name;
    const features = pkg.features || [];

    return (
      <Card
        className={`overflow-hidden shadow-medium hover:shadow-large transition-all duration-300 hover:-translate-y-2 bg-card border-2 ${
          isFeatured ? "border-accent" : "border-border"
        } animate-scale-in`}
        style={{ animationDelay: `${index * 0.15}s` }}
      >
        {isFeatured && (
          <div className="bg-gradient-accent text-accent-foreground text-center py-2 font-semibold flex items-center justify-center gap-2">
            <Star className="w-4 h-4 fill-current" />
            Paling Populer
          </div>
        )}

        <div className="relative h-48 overflow-hidden">
          <img
            src={pkg.image_url || "/placeholder-image.jpg"} // Gunakan image_url dari API
            alt={title} // Gunakan title (dari pkg.name) untuk alt
            className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div className="absolute bottom-4 left-4 text-white">
            <h3 className="text-2xl font-serif font-bold">{title}</h3>{" "}
            {/* Gunakan title (dari pkg.name) */}
          </div>
        </div>

        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Calendar className="w-4 h-4" />
              <span className="text-sm">{durationText}</span>{" "}
              {/* Gunakan duration dari API */}
            </div>
            <div className="text-2xl font-bold text-primary">
              {formattedPrice}
            </div>{" "}
            {/* Gunakan harga dari API */}
          </div>
        </CardHeader>

        <CardContent>
          <ul className="space-y-3">
            {/* Iterasi melalui array features dari API */}
            {features.map((feature, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm">
                <MapPin className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />
                <span className="text-muted-foreground">{feature}</span>
              </li>
            ))}
            {/* Fallback jika features kosong */}
            {features.length === 0 && pkg.hotel_info && (
              <li className="flex items-start gap-2 text-sm">
                <MapPin className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />
                <span className="text-muted-foreground">{pkg.hotel_info}</span>
              </li>
            )}
          </ul>
        </CardContent>

        <CardFooter>
          {/* GANTI Button asChild DENGAN Link LANGSUNG */}
          {/* Kita gunakan Link dan beri styling tombol secara manual */}
          <Link
            to={`/packages/${pkg.package_id}`} // Gunakan package_id dari API
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground transition-all duration-300 text-center py-2 rounded-md block font-medium" // Styling meniru button
          >
            Lihat Detail
          </Link>
        </CardFooter>
      </Card>
    );
  };

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
            {title}
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Pilih paket yang sesuai dengan kebutuhan dan budget Anda
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {displayedPackages.map((pkg, index) => (
            <PackageCard key={pkg.package_id} pkg={pkg} index={index} /> // Gunakan package_id dari API
          ))}
        </div>

        {showLoadMore &&
          visibleCount < initialPackages.length && ( // Kondisi benar: tampilkan jika showLoadMore dan visibleCount < total
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

export default PackagesSection;
