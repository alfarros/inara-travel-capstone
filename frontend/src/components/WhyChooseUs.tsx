import { useState } from "react";
import { Card } from "@/components/ui/card";
import { featuresData, Feature } from "@/data/features";
import ReactCardFlip from "react-card-flip";
import { cn } from "@/lib/utils";

const WhyChooseUs = () => {
  return (
    <section
      className="py-20 px-4 bg-background"
      aria-labelledby="features-heading"
    >
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16 animate-fade-in-up">
          <h2
            id="features-heading"
            className="text-3xl md:text-5xl font-serif font-bold text-primary mb-4"
          >
            Mengapa Memilih Inara Travel?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Kami berkomitmen memberikan pengalaman umrah terbaik dengan tiga
            pilar utama
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {featuresData.map((feature, index) => (
            <FlipCard key={feature.title} feature={feature} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
};

// Komponen Kartu Flip yang Jauh Lebih Simple
interface FlipCardProps {
  feature: Feature;
  index: number;
}

const FlipCard: React.FC<FlipCardProps> = ({ feature, index }) => {
  const [isFlipped, setIsFlipped] = useState(false);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const Icon = feature.icon;

 return (
    // 2. Gunakan komponen ReactCardFlip
    <ReactCardFlip isFlipped={isFlipped} flipDirection="vertical" flipSpeedFrontToBack={0.6} flipSpeedBackToFront={0.6}>
      {/* Sisi Depan Kartu */}
      <Card
        className={cn(
          "h-96 cursor-pointer p-8 border-none shadow-medium hover:shadow-large transition-all duration-300 animate-fade-in-up",
          feature.color,
          feature.textColor
        )}
        onClick={handleFlip}
        style={{ animationDelay: `${index * 0.2}s` }}
      >
        <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
          <div className="p-4 bg-card/20 rounded-full">
            <Icon className="w-12 h-12" />
          </div>
          <h3 className="text-2xl font-serif font-semibold">{feature.title}</h3>
          <p className="text-base leading-relaxed opacity-90">{feature.description}</p>
          <p className="text-sm opacity-75">Klik untuk melihat gambar</p>
        </div>
      </Card>

      {/* Sisi Belakang Kartu */}
      <Card
        className="h-96 cursor-pointer overflow-hidden border-none shadow-large"
        onClick={handleFlip}
      >
        <div className="relative w-full h-full">
          <img
            src={feature.image}
            alt={feature.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent flex items-end p-8">
            <div className="text-center text-white w-full">
              <h3 className="text-2xl font-serif font-bold">{feature.title}</h3>
              <p className="text-sm opacity-90 mt-2">Klik untuk kembali</p>
            </div>
          </div>
        </div>
      </Card>
      </ReactCardFlip>
  );
};

export default WhyChooseUs;

