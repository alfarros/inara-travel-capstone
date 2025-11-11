// frontend/src/pages/Packages.tsx
import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchPackages, ApiPackage } from "@/lib/api"; // Pastikan fetchPackages dan ApiPackage sudah di definisikan di api.ts
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar, MapPin, Star } from "lucide-react";
import { Link } from "react-router-dom";

interface PackagesProps {
  showLoadMore?: boolean;
  limit?: number;
}

const PackagesPageContent = ({
  showLoadMore = false,
  limit = 3,
}: PackagesProps) => {
  const {
    data: packages = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["packages"],
    queryFn: fetchPackages,
    staleTime: 5 * 60 * 1000, // Data dianggap fresh selama 5 menit
  });

  const [visibleCount, setVisibleCount] = useState(limit);

  const loadMore = () => {
    setVisibleCount((prev) => Math.min(prev + limit, packages.length));
  };

  const displayedPackages = useMemo(() => {
    return showLoadMore
      ? packages.slice(0, visibleCount)
      : packages.slice(0, limit);
  }, [showLoadMore, visibleCount, limit, packages]);

  if (isLoading)
    return <div className="py-12 text-center">Memuat paket...</div>;
  if (isError)
    return (
      <div className="py-12 text-center text-destructive">
        Error: {error.message}
      </div>
    );

  return (
    <section className="py-20 px-4 bg-muted/30">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16 animate-fade-in-up">
          <h2 className="text-3xl md:text-5xl font-serif font-bold text-primary mb-4">
            Paket Umrah Pilihan
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Pilih paket yang sesuai dengan kebutuhan dan budget Anda
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {displayedPackages.map((pkg, index) => (
            <PackageCard key={pkg.package_id} pkg={pkg} index={index} /> // <-- Gunakan package_id dari API
          ))}
        </div>

        {showLoadMore && visibleCount < packages.length && (
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

// Komponen PackageCard yang diadaptasi untuk data API
interface PackageCardProps {
  pkg: ApiPackage; // <-- Gunakan tipe dari API
  index: number;
}

const PackageCard: React.FC<PackageCardProps> = ({ pkg, index }) => {
  // Konversi harga dari API (number) ke format string yang diharapkan
  const formattedPrice = new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(pkg.price);

  // Konversi durasi dari API (number) ke string
  const durationText = pkg.duration_days
    ? `${pkg.duration_days} Hari`
    : "Durasi Tidak Ditentukan";

  // Periksa apakah paket ini 'featured' (misalnya dari API, tambahkan field 'featured' ke schema/model nanti jika perlu)
  // Untuk sekarang, asumsikan tidak ada field 'featured' di API, jadi selalu false
  const isFeatured = false; // Atau pkg.featured jika field itu ditambahkan ke API

  return (
    <Card
      className={`overflow-hidden shadow-medium hover:shadow-large transition-all duration-300 hover:-translate-y-2 bg-card border-2 ${
        isFeatured ? "border-accent" : "border-border"
      } animate-scale-in`}
      style={{ animationDelay: `${index * 0.15}s` }}
    >
      {isFeatured && ( // <-- Hanya tampilkan jika featured
        <div className="bg-gradient-accent text-accent-foreground text-center py-2 font-semibold flex items-center justify-center gap-2">
          <Star className="w-4 h-4 fill-current" />
          Paling Populer
        </div>
      )}

      <div className="relative h-48 overflow-hidden">
        <img
          src={pkg.image_url || "/placeholder-image.jpg"} // <-- Gunakan image_url dari API
          alt={pkg.name} // <-- Gunakan name dari API
          className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        <div className="absolute bottom-4 left-4 text-white">
          <h3 className="text-2xl font-serif font-bold">{pkg.name}</h3>{" "}
          {/* <-- Gunakan name dari API */}
        </div>
      </div>

      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Calendar className="w-4 h-4" />
            <span className="text-sm">{durationText}</span>{" "}
            {/* <-- Gunakan durasi dari API */}
          </div>
          <div className="text-2xl font-bold text-primary">
            {formattedPrice}
          </div>{" "}
          {/* <-- Gunakan harga dari API */}
        </div>
      </CardHeader>

      <CardContent>
        <ul className="space-y-3">
          {/* Features mungkin tidak langsung ada di schema API packages saat ini.
              Jika features ingin ditampilkan, perlu ditambahkan ke schema dan model API. */}
          {/* <li key={idx} className="flex items-start gap-2 text-sm">
            <MapPin className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />
            <span className="text-muted-foreground">{feature}</span>
          </li> */}
          {/* Sebagai ganti, tampilkan deskripsi singkat */}
          <li className="text-sm text-muted-foreground line-clamp-2">
            {pkg.description}
          </li>
        </ul>
      </CardContent>

      <CardFooter>
        {/* Ganti Button asChild dengan Button biasa */}
        <Button
          onClick={() => (window.location.href = `/packages/${pkg.package_id}`)} // Ganti dengan navigasi router jika perlu
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground transition-all duration-300"
        >
          Lihat Detail
        </Button>
      </CardFooter>
    </Card>
  );
};

export default PackagesPageContent;
