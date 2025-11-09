// src/pages/PackageDetailPage.tsx
import { useParams } from "react-router-dom";
import { packagesData } from "@/data/packages";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, ArrowLeft, Link } from "lucide-react";

// Impor komponen yang diperlukan
import { HeroSection } from "@/components/package-detail/HeroSection";
import { ProductInfoTabs } from "@/components/package-detail/ProductInfoTabs";
import { PriceAndBooking } from "@/components/package-detail/PriceAndBooking";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export const PackageDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const packageDetail = packagesData.find((pkg) => pkg.id === Number(id));

  if (!packageDetail) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <Alert variant="destructive" className="max-w-md mx-auto">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Paket Tidak Ditemukan</AlertTitle>
          <AlertDescription>
            Maaf, paket yang Anda cari tidak ada.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <main>
      {/* Hero Section Penuh Lebar */}
      <HeroSection pkg={packageDetail} />

      {/* Konten Utama dengan Layout 2 Kolom */}
      <div className="container mx-auto max-w-6xl px-4 py-12">
        <div className="grid md:grid-cols-3 gap-8 lg:gap-12">
          {/* Kolom Kiri: Deskripsi dan Fasilitas (2/3 lebar) */}
          <div className="md:col-span-2">
            <ProductInfoTabs pkg={packageDetail} />
          </div>

          {/* Kolom Kanan: Harga dan CTA (1/3 lebar) */}
          <div className="md:col-span-1">
            <div className="sticky top-24 space-y-6">
              <PriceAndBooking pkg={packageDetail} />
              {/* Anda bisa menambahkan info lain di sini, misal: "Penting untuk Diketahui" */}
              <Card>
                <CardContent className="pt-6">
                  <h4 className="font-semibold mb-2">
                    Penting untuk Diketahui
                  </h4>
                  <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                    <li>Harga dapat berubah sewaktu-waktu.</li>
                    <li>Keberangkatan tergantung ketersediaan kursi.</li>
                    <li>Proses pembayaran DP untuk mengamankan kursi.</li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
        {/* Tombol Kembali */}
        <div className="container mx-auto px-4 pt-8">
          <Button asChild variant="ghost" className="mb-4">
            <Link to="/packages">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Kembali ke Paket
            </Link>
          </Button>
        </div>
      </div>
    </main>
  );
};
