// src/components/package-detail/ProductInfoTabs.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, Plane, Hotel, Utensils } from "lucide-react";
import { Package } from "@/data/packages";

interface ProductInfoTabsProps {
  pkg: Package;
}

export const ProductInfoTabs: React.FC<ProductInfoTabsProps> = ({ pkg }) => {
  // Icon mapping untuk kemudahan
  const getIcon = (feature: string) => {
    if (feature.toLowerCase().includes("hotel"))
      return <Hotel className="w-5 h-5" />;
    if (feature.toLowerCase().includes("penerbangan"))
      return <Plane className="w-5 h-5" />;
    if (
      feature.toLowerCase().includes("meals") ||
      feature.toLowerCase().includes("breakfast")
    )
      return <Utensils className="w-5 h-5" />;
    return <CheckCircle className="w-5 h-5" />;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl">Tentang Paket Ini</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Deskripsi Utama */}
        <div>
          <p className="text-muted-foreground leading-relaxed">
            {pkg.description}
          </p>
        </div>

        {/* Rincian Perjalanan */}
        <div>
          <h4 className="font-semibold mb-3">Rincian Perjalanan</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Durasi:</span>
              <p className="text-muted-foreground">{pkg.duration}</p>
            </div>
            <div>
              <span className="font-medium">Maskapai:</span>
              <p className="text-muted-foreground">{pkg.airline}</p>
            </div>
            <div>
              <span className="font-medium">Berangkat dari:</span>
              <p className="text-muted-foreground">{pkg.departureCity}</p>
            </div>
            <div>
              <span className="font-medium">Harga Mulai:</span>
              <p className="text-primary font-bold">{pkg.price}</p>
            </div>
          </div>
        </div>

        {/* Fasilitas */}
        <div>
          <h4 className="font-semibold mb-3">Fasilitas yang Anda Dapatkan</h4>
          <ul className="space-y-3">
            {pkg.features.map((feature, index) => (
              <li key={index} className="flex items-start gap-3">
                <div className="text-primary flex-shrink-0 mt-0.5">
                  {getIcon(feature)}
                </div>
                <span className="text-sm text-muted-foreground">{feature}</span>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};
