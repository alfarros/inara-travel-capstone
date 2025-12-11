// frontend/src/pages/PackageDetail.tsx
import { useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query"; // Tambahkan useQueryClient
import {
  fetchPackageDetail,
  ApiPackageWithReviews,
  createReview as apiCreateReview,
  ApiReview,
} from "@/lib/api"; // Impor apiCreateReview dan ApiReview
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, ArrowLeft, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import ReviewForm from "@/components/ReviewForm"; // Impor komponen baru

export const PackageDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const packageId = Number(id);
  const queryClient = useQueryClient(); // Dapatkan instance query client

  const {
    data: pkg,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["packageDetail", packageId],
    queryFn: () => fetchPackageDetail(packageId),
    enabled: !isNaN(packageId),
    staleTime: 5 * 60 * 1000,
  });

  // Fungsi untuk menangani penambahan review baru
  const handleReviewAdded = (newReview: ApiReview) => {
    if (pkg) {
      // Update cache query 'packageDetail' secara manual
      queryClient.setQueryData<ApiPackageWithReviews>(
        ["packageDetail", packageId],
        (oldData) => {
          if (!oldData) return oldData; // Jika data lama tidak ada, kembalikan null

          // Buat salinan data lama dan tambahkan review baru ke array reviews
          return {
            ...oldData,
            reviews: [...oldData.reviews, newReview], // Tambahkan review baru
          };
        }
      );
    }
  };

  if (isLoading)
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        Memuat detail paket...
      </div>
    );
  if (isError) {
    if (error.message === "Paket tidak ditemukan.") {
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
      <div className="container mx-auto px-4 py-8 text-center text-destructive">
        Error: {error.message}
      </div>
    );
  }

  if (!pkg) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <Alert variant="destructive" className="max-w-md mx-auto">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Data Tidak Valid</AlertTitle>
          <AlertDescription>Data paket tidak valid.</AlertDescription>
        </Alert>
      </div>
    );
  }

  const formattedPrice = new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(pkg.price);

  const durationText = pkg.duration_days
    ? `${pkg.duration_days} Hari`
    : "Durasi Tidak Ditentukan";

  return (
    <main>
      {/* Hero Section Penuh Lebar - Disederhanakan */}
      <section className="relative h-96 overflow-hidden">
        <img
          src={pkg.image_url || "/placeholder-image.jpg"}
          alt={pkg.name}
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/50" />
        <div className="relative z-10 h-full flex flex-col justify-center text-white">
          <div className="container mx-auto px-4 pt-4">
            <Button
              variant="ghost"
              asChild
              className="text-white hover:bg-white/20"
            >
              <Link to="/packages">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Kembali
              </Link>
            </Button>
          </div>
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-4">{pkg.name}</h1>
            <p className="text-xl mb-6">
              {durationText} | Tujuan: {pkg.destination || "Belum Ditentukan"}
            </p>
            <p className="text-2xl font-bold text-primary mb-4">
              {formattedPrice}
            </p>
            <Button
              asChild
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              <a
                href={`https://wa.me/6281234567890?text=${encodeURIComponent(
                  `Assalamualaikum, saya tertarik dengan paket ${pkg.name}. Mohon info lebih lanjut.`
                )}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                Konsultasi via WhatsApp
              </a>
            </Button>
          </div>
        </div>
      </section>

      {/* Konten Utama */}
      <div className="container mx-auto max-w-6xl px-4 py-12">
        <div className="grid md:grid-cols-3 gap-8 lg:gap-12">
          {/* Kolom Kiri: Deskripsi dan Ulasan */}
          <div className="md:col-span-2">
            {/* Info Produk */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="text-2xl">Tentang Paket Ini</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <p className="text-muted-foreground leading-relaxed">
                    {pkg.description}
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-3">Rincian Perjalanan</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Durasi:</span>
                      <p className="text-muted-foreground">{durationText}</p>
                    </div>
                    <div>
                      <span className="font-medium">Kategori:</span>
                      <p className="text-muted-foreground">
                        {pkg.category || "Umum"}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium">Berangkat dari:</span>
                      <p className="text-muted-foreground">
                        {pkg.departure_city || "Belum Ditentukan"}</p>
                    </div>
                    <div>
                      <span className="font-medium">Harga Mulai:</span>
                      <p className="text-primary font-bold">{formattedPrice}</p>
                    </div>
                    <div>
                      <span className="font-medium">Hotel:</span>
                      <p className="text-muted-foreground">
                        {pkg.hotel_info || "Informasi belum tersedia"}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium">Tujuan:</span>
                      <p className="text-muted-foreground">
                        {pkg.destination || "Informasi belum tersedia"}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Ulasan */}
            <Card>
              <CardHeader>
                <CardTitle className="text-2xl">Ulasan Pelanggan</CardTitle>
              </CardHeader>
              <CardContent>
                {pkg.reviews.length > 0 ? (
                  <div className="space-y-4">
                    {pkg.reviews.map((review) => (
                      <div
                        key={review.review_id}
                        className="border-b pb-4 last:border-b-0"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          {/* Gunakan reviewer_name dari API */}
                          <span className="font-semibold">
                            {review.reviewer_name || "Anonim"}
                          </span>
                          <div className="flex">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                className={`w-4 h-4 ${
                                  i < review.rating
                                    ? "fill-yellow-400 text-yellow-400"
                                    : "text-gray-300"
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {review.review_text}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(review.created_at).toLocaleDateString(
                            "id-ID"
                          )}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground italic">
                    Belum ada ulasan untuk paket ini.
                  </p>
                )}
                {/* Tambahkan ReviewForm di sini */}
                <ReviewForm
                  packageId={pkg.package_id}
                  onReviewAdded={handleReviewAdded}
                />
              </CardContent>
            </Card>
          </div>

          {/* Kolom Kanan: Harga dan CTA */}
          <div className="md:col-span-1">
            <div className="sticky top-24 space-y-6">
              <Card className="bg-muted/30 py-6 text-center">
                <CardContent>
                  <h2 className="text-xl font-bold mb-2">Harga</h2>
                  <p className="text-3xl font-bold text-primary mb-4">
                    {formattedPrice}
                  </p>
                  <p className="text-sm text-muted-foreground mb-4">
                    *Harga dapat berubah sewaktu-waktu.
                  </p>
                  <Button
                    asChild
                    className="w-full bg-green-600 hover:bg-green-700 text-white"
                  >
                    <a
                      href={`https://wa.me/6281234567890?text=${encodeURIComponent(
                        `Assalamualaikum, saya tertarik dengan paket ${pkg.name}. Mohon info lebih lanjut.`
                      )}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Konsultasi via WhatsApp
                    </a>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
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
