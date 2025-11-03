// src/pages/PackageDetailPage.tsx
import { usePackageDetail } from "@/hooks/use-package-detail";
import { Loader2, AlertCircle, ArrowLeft } from "lucide-react"; // 2. Import ArrowLeft
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom"; // 3. Import Link

// Impor komponen bagian
import { HeroSection } from "@/components/package-detail/HeroSection";
import { ItinerarySection } from "@/components/package-detail/ItinerarySection";
import { FacilitiesSection } from "@/components/package-detail/FacilitiesSection";
import { PriceAndBooking } from "@/components/package-detail/PriceAndBooking";

export const PackageDetailPage = () => {
  const { packageDetail, isLoading } = usePackageDetail();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!packageDetail) {
    return (
      <Alert variant="destructive" className="m-4">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Paket Tidak Ditemukan</AlertTitle>
        <AlertDescription>
          Maaf, paket yang Anda cari tidak tersedia.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <>
      {/* 5. Gunakan tag <main> dan tambahkan tombol kembali */}
      <main>
        {/* Tombol Kembali */}
        <div className="container mx-auto px-4 pt-8">
          <Button asChild variant="ghost" className="mb-4">
            <Link to="/packages">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Kembali ke Paket
            </Link>
          </Button>
        </div>

        {/* Konten Utama */}
        <HeroSection pkg={packageDetail} />
        <div className="container mx-auto max-w-6xl px-4 py-12 space-y-16">
          <ItinerarySection />
          <FacilitiesSection pkg={packageDetail} />
          <PriceAndBooking pkg={packageDetail} />
        </div>
      </main>
    </>
  );
};
