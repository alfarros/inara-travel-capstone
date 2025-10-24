import Hero from "@/components/Hero";
import WhyChooseUs from "@/components/WhyChooseUs";
import Packages from "@/components/Packages";
import Testimonials from "@/components/Testimonials";
import About from "@/components/About";
import Partners from "@/components/Partners";
import Footer from "@/components/Footer";
import FloatingWhatsApp from "@/components/FloatingWhatsApp";

const Index = () => {
  return (
    <div className="min-h-screen font-sans">
      <Hero />
      <WhyChooseUs />
      <Packages />
      <Testimonials />
      <About />
      <Partners />
      <Footer />
      <FloatingWhatsApp />
    </div>
  );
};

export default Index;
