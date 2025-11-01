// src/components/Testimonials.tsx
import { Card, CardContent } from "@/components/ui/card";
import { Star, ChevronLeft, ChevronRight } from "lucide-react";
import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { testimonialsData, Testimonial } from "@/data/testimonials";

const Testimonials = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const goToTestimonial = useCallback((index: number) => {
    setCurrentIndex(index);
  }, []);

  const nextTestimonial = useCallback(() => {
    setCurrentIndex((prev) => (prev + 1) % testimonialsData.length);
  }, []);

  const prevTestimonial = useCallback(() => {
    setCurrentIndex(
      (prev) => (prev - 1 + testimonialsData.length) % testimonialsData.length
    );
  }, []);

  const currentTestimonial = testimonialsData[currentIndex];

  return (
    <section
      className="py-20 px-4 bg-background"
      aria-labelledby="testimonials-heading"
    >
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-16 animate-fade-in-up">
          <h2
            id="testimonials-heading"
            className="text-3xl md:text-5xl font-serif font-bold text-primary mb-4"
          >
            Testimoni Jamaah
          </h2>
          <p className="text-lg text-muted-foreground">
            Pengalaman berharga dari para jamaah yang telah beribadah bersama
            kami
          </p>
        </div>

        <TestimonialCarousel
          testimonial={currentTestimonial}
          onNext={nextTestimonial}
          onPrev={prevTestimonial}
          onDotClick={goToTestimonial}
          currentIndex={currentIndex}
          totalTestimonials={testimonialsData.length}
        />
      </div>
    </section>
  );
};

interface TestimonialCarouselProps {
  testimonial: Testimonial;
  onNext: () => void;
  onPrev: () => void;
  onDotClick: (index: number) => void;
  currentIndex: number;
  totalTestimonials: number;
}

const TestimonialCarousel: React.FC<TestimonialCarouselProps> = ({
  testimonial,
  onNext,
  onPrev,
  onDotClick,
  currentIndex,
  totalTestimonials,
}) => {
  return (
    <div className="relative">
      <Card className="bg-muted/50 border-none shadow-medium overflow-hidden">
        <CardContent className="p-8 md:p-12">
          <div className="flex flex-col items-center text-center space-y-6 animate-fade-in">
            <div className="w-20 h-20 rounded-full overflow-hidden bg-primary/10 ring-4 ring-accent/20">
              <img
                src={testimonial.avatar}
                alt={testimonial.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex gap-1">
              {[...Array(testimonial.rating)].map((_, i) => (
                <Star key={i} className="w-5 h-5 fill-accent text-accent" />
              ))}
            </div>
            <blockquote className="text-lg md:text-xl text-foreground leading-relaxed italic max-w-2xl">
              "{testimonial.text}"
            </blockquote>
            <div>
              <div className="font-semibold text-primary text-lg">
                {testimonial.name}
              </div>
              <div className="text-muted-foreground text-sm">
                {testimonial.location}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center items-center gap-4 mt-8">
        <Button
          variant="outline"
          size="icon"
          onClick={onPrev}
          className="rounded-full"
        >
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <div className="flex items-center gap-2">
          {[...Array(totalTestimonials)].map((_, index) => (
            <button
              key={index}
              onClick={() => onDotClick(index)}
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
          onClick={onNext}
          className="rounded-full"
        >
          <ChevronRight className="h-5 w-5" />
        </Button>
      </div>
    </div>
  );
};

export default Testimonials;
