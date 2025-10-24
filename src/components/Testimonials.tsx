import { Card, CardContent } from "@/components/ui/card";
import { Star, ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

const testimonials = [
  {
    id: 1,
    name: "Bunda Rina Wijaya",
    location: "Jakarta Selatan",
    rating: 5,
    text: "Pertama kali umrah, tapi terasa seperti bareng keluarga sendiri. Ustadznya sabar banget ngejelasin tata cara ibadah. Alhamdulillah pengalaman yang luar biasa!",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Rina",
  },
  {
    id: 2,
    name: "Pak Ahmad Fauzi",
    location: "Bandung",
    rating: 5,
    text: "Pelayanan ramah, hotel strategis dekat masjid, dan makanannya enak-enak. Semua berjalan lancar tanpa hambatan. Jazakumullah khairan!",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Ahmad",
  },
  {
    id: 3,
    name: "Ibu Siti Nurhaliza",
    location: "Surabaya",
    rating: 5,
    text: "Inara Travel benar-benar memperhatikan detail. Dari manasik sampai di tanah suci, semuanya terbimbing dengan baik. Recommended banget!",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Siti",
  },
];

const Testimonials = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const nextTestimonial = () => {
    setCurrentIndex((prev) => (prev + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  const currentTestimonial = testimonials[currentIndex];

  return (
    <section className="py-20 px-4 bg-background">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-16 animate-fade-in-up">
          <h2 className="text-3xl md:text-5xl font-serif font-bold text-primary mb-4">
            Testimoni Jamaah
          </h2>
          <p className="text-lg text-muted-foreground">
            Pengalaman berharga dari para jamaah yang telah beribadah bersama kami
          </p>
        </div>

        <div className="relative">
          <Card className="bg-muted/50 border-none shadow-medium overflow-hidden">
            <CardContent className="p-8 md:p-12">
              <div className="flex flex-col items-center text-center space-y-6 animate-fade-in">
                {/* Avatar */}
                <div className="w-20 h-20 rounded-full overflow-hidden bg-primary/10 ring-4 ring-accent/20">
                  <img
                    src={currentTestimonial.avatar}
                    alt={currentTestimonial.name}
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Rating */}
                <div className="flex gap-1">
                  {[...Array(currentTestimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 fill-accent text-accent" />
                  ))}
                </div>

                {/* Testimonial Text */}
                <blockquote className="text-lg md:text-xl text-foreground leading-relaxed italic max-w-2xl">
                  "{currentTestimonial.text}"
                </blockquote>

                {/* Author Info */}
                <div>
                  <div className="font-semibold text-primary text-lg">
                    {currentTestimonial.name}
                  </div>
                  <div className="text-muted-foreground text-sm">
                    {currentTestimonial.location}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Navigation Buttons */}
          <div className="flex justify-center gap-4 mt-8">
            <Button
              variant="outline"
              size="icon"
              onClick={prevTestimonial}
              className="rounded-full hover:bg-primary hover:text-primary-foreground transition-all"
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
            
            {/* Dots Indicator */}
            <div className="flex items-center gap-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentIndex(index)}
                  className={`w-2 h-2 rounded-full transition-all ${
                    index === currentIndex
                      ? "bg-primary w-8"
                      : "bg-muted-foreground/30"
                  }`}
                  aria-label={`Go to testimonial ${index + 1}`}
                />
              ))}
            </div>

            <Button
              variant="outline"
              size="icon"
              onClick={nextTestimonial}
              className="rounded-full hover:bg-primary hover:text-primary-foreground transition-all"
            >
              <ChevronRight className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
