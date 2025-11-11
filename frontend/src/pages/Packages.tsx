// frontend/src/pages/Packages.tsx
import { useQuery } from "@tanstack/react-query";
import { fetchPackages } from "@/lib/api"; // Impor fungsi fetch
import PackagesSection from "@/components/Packages"; // Impor komponen

export default function Packages() {
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

  if (isLoading)
    return <div className="py-12 text-center">Memuat paket...</div>;
  if (isError)
    return (
      <div className="py-12 text-center text-destructive">
        Error: {error.message}
      </div>
    );

  // Teruskan data packages ke komponen PackagesSection
  return (
    <div className="py-12">
      <PackagesSection
        initialPackages={packages}
        showLoadMore={true}
        limit={3}
      />
    </div>
  );
}
