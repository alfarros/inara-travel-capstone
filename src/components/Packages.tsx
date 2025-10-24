import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar, MapPin, Star } from "lucide-react";
import jamaahImage from "@/assets/jamaah-group.jpg";

const packages = [
  {
    id: 1,
    title: "Paket Premium",
    duration: "9 Hari",
    price: "Rp 28.000.000",
    features: [
      "Hotel Bintang 5 (100m dari Masjidil Haram)",
      "Penerbangan Langsung",
      "Full Board Meals",
      "Ziarah Lengkap",
    ],
    image: jamaahImage,
  },
  {
    id: 2,
    title: "Paket Silver",
    duration: "12 Hari",
    price: "Rp 24.000.000",
    features: [
      "Hotel Bintang 4 (300m dari Masjidil Haram)",
      "Penerbangan Transit 1x",
      "Breakfast & Dinner",
      "Ziarah Lengkap",
    ],
    image: jamaahImage,
    featured: true,
  },
  {
    id: 3,
    title: "Paket Bronze",
    duration: "15 Hari",
    price: "Rp 20.000.000",
    features: [
      "Hotel Bintang 3 (500m dari Masjidil Haram)",
      "Penerbangan Transit 1x",
      "Breakfast Only",
      "Ziarah Utama",
    ],
    image: jamaahImage,
  },
];

const Packages = () => {
  const handleWhatsAppClick = (packageTitle: string) => {
    const message = `Assalamualaikum, saya tertarik dengan ${packageTitle}. Mohon info lebih lanjut.`;
    window.open(`https://wa.me/6281234567890?text=${encodeURIComponent(message)}`, "_blank");
  };

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
          {packages.map((pkg, index) => (
            <Card
              key={pkg.id}
              className={`overflow-hidden shadow-medium hover:shadow-large transition-all duration-300 hover:-translate-y-2 bg-card border-2 ${
                pkg.featured ? "border-accent" : "border-border"
              } animate-scale-in`}
              style={{ animationDelay: `${index * 0.15}s` }}
            >
              {pkg.featured && (
                <div className="bg-gradient-accent text-accent-foreground text-center py-2 font-semibold flex items-center justify-center gap-2">
                  <Star className="w-4 h-4 fill-current" />
                  Paling Populer
                </div>
              )}
              
              <div className="relative h-48 overflow-hidden">
                <img
                  src={pkg.image}
                  alt={pkg.title}
                  className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <div className="absolute bottom-4 left-4 text-white">
                  <h3 className="text-2xl font-serif font-bold">{pkg.title}</h3>
                </div>
              </div>

              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Calendar className="w-4 h-4" />
                    <span className="text-sm">{pkg.duration}</span>
                  </div>
                  <div className="text-2xl font-bold text-primary">
                    {pkg.price}
                  </div>
                </div>
              </CardHeader>

              <CardContent>
                <ul className="space-y-3">
                  {pkg.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm">
                      <MapPin className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" />
                      <span className="text-muted-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>

              <CardFooter>
                <Button
                  onClick={() => handleWhatsAppClick(pkg.title)}
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground transition-all duration-300"
                >
                  Lihat Detail
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        <div className="text-center mt-12 text-sm text-muted-foreground">
          <p>* Harga dapat berubah sewaktu-waktu. Hubungi kami untuk penawaran terbaru.</p>
        </div>
      </div>
    </section>
  );
};

export default Packages;
