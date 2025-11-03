// src/components/package-detail/FacilitiesSection.tsx
import { Package } from "@/data/packages"; // Import interface Package
import { Check } from "lucide-react";

interface Props {
  pkg: Package; // Terima seluruh object `pkg`
}

export const FacilitiesSection: React.FC<Props> = ({ pkg }) => {
  return (
    <section>
      <h2 className="text-3xl font-bold text-center mb-8">
        Fasilitas yang Anda Dapatkan
      </h2>
      <div className="grid md:grid-cols-2 gap-4">
        {pkg.features.map((facility, index) => (
          <div key={index} className="flex items-start gap-3">
            <Check className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
            <p>{facility}</p>
          </div>
        ))}
      </div>
    </section>
  );
};
