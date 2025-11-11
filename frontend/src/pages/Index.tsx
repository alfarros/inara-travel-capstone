// frontend/src/pages/Index.tsx
import Hero from "@/components/Hero";
import WhyChooseUs from "@/components/WhyChooseUs";
import Testimonials from "@/components/Testimonials";
import About from "@/components/About";
import Partners from "@/components/Partners";
import FloatingChatWidget from "@/components/FloatingChatWidget";
import PackagesSection from "@/components/Packages";
import { useQuery } from "@tanstack/react-query";
import { fetchPackages } from "@/lib/api";

const Index = () => {
  // Gunakan useQuery untuk mengambil data di Index
  const {
    data :allPackages = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["packages"],
    queryFn: fetchPackages,
    staleTime: 5 * 60 * 1000, // Data dianggap fresh selama 5 menit
  });

  // Tentukan paket-paket yang akan ditampilkan di halaman utama (misalnya 3 pertama)
  const homepagePackages = allPackages.slice(0, 3);

  if (isLoading) {
    // Tampilkan loading state opsional
    console.log("Memuat paket untuk halaman utama..."); // Contoh sederhana
    // Anda bisa menampilkan UI loading yang lebih bagus di sini
  }

  if (isError) {
    // Tampilkan error state opsional
    console.error("Error fetching packages for Index:", error);
    // Anda bisa menampilkan UI error yang lebih bagus di sini
  }

  return (
    <>
      <div className="min-h-screen font-sans">
        <Hero />
        <WhyChooseUs />
        {/* Gunakan PackagesSection secara langsung di sini */}
        <PackagesSection
          initialPackages={homepagePackages} // Kirim hanya 3 paket pertama
          showLoadMore={false} // JANGAN tampilkan tombol load more di Index
          limit={3} // Limit bisa diabaikan karena kita sudah slice di atas
        />
        <Testimonials />
        <About />
        <Partners />
        <FloatingChatWidget />
      </div>
    </>
  );
};

export default Index;
