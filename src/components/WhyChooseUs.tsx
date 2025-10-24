import { Heart, Users, BookOpen } from "lucide-react";
import { Card } from "@/components/ui/card";

const features = [
  {
    icon: Heart,
    title: "Nyaman",
    description: "Hotel dekat masjid, maskapai pilihan, makanan halal terjamin. Perjalanan ibadah Anda dijamin nyaman dan menenangkan.",
    color: "bg-green-light",
    textColor: "text-foreground",
  },
  {
    icon: Users,
    title: "Terbimbing",
    description: "Ustadz pendamping berpengalaman, manasik offline & online. Kami memastikan Anda siap dan paham setiap rukun ibadah.",
    color: "bg-secondary",
    textColor: "text-secondary-foreground",
  },
  {
    icon: BookOpen,
    title: "Sunnah",
    description: "Ibadah sesuai tuntunan, kajian harian, suasana khusyu. Mengikuti jejak Rasulullah SAW dalam setiap langkah.",
    color: "bg-green-olive",
    textColor: "text-primary-foreground",
  },
];

const WhyChooseUs = () => {
  return (
    <section className="py-20 px-4 bg-background">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16 animate-fade-in-up">
          <h2 className="text-3xl md:text-5xl font-serif font-bold text-primary mb-4">
            Mengapa Memilih Inara Travel?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Kami berkomitmen memberikan pengalaman umrah terbaik dengan tiga pilar utama
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card
                key={index}
                className={`${feature.color} ${feature.textColor} p-8 border-none shadow-medium hover:shadow-large transition-all duration-300 hover:-translate-y-2 animate-fade-in-up`}
                style={{ animationDelay: `${index * 0.2}s` }}
              >
                <div className="flex flex-col items-center text-center space-y-4">
                  <div className="p-4 bg-card/20 rounded-full">
                    <Icon className="w-12 h-12" />
                  </div>
                  <h3 className="text-2xl font-serif font-semibold">
                    {feature.title}
                  </h3>
                  <p className="text-base leading-relaxed opacity-90">
                    {feature.description}
                  </p>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default WhyChooseUs;
