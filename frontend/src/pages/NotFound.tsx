// src/pages/NotFound.tsx
import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Home, Search } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <>
      <main className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <div className="text-center p-8">
          <div className="flex justify-center mb-4">
            <Search className="h-16 w-16 text-muted-foreground" />
          </div>
          <h1 className="mb-4 text-6xl font-bold text-primary">404</h1>
          <p className="mb-4 text-xl text-muted-foreground">
            Oops! Halaman yang Anda cari tidak ditemukan.
          </p>
          <p className="mb-8 text-sm text-muted-foreground max-w-md mx-auto">
            Mungkin halaman tersebut telah dipindahkan, dihapus, atau Anda salah
            mengetikkan alamat URL.
          </p>
          <Button asChild>
            <Link to="/">
              <Home className="mr-2 h-4 w-4" />
              Kembali ke Halaman Utama
            </Link>
          </Button>
        </div>
      </main>
    </>
  );
};

export default NotFound;
