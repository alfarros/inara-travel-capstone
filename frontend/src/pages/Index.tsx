// src/pages/Index.tsx
import Hero from "@/components/Hero";
import WhyChooseUs from "@/components/WhyChooseUs";
import Packages from "@/components/Packages";
import Testimonials from "@/components/Testimonials";
import About from "@/components/About";
import Partners from "@/components/Partners";
import FloatingWhatsApp from "@/components/FloatingChatWidget";
import FloatingChatWidget from "@/components/FloatingChatWidget";

const Index = () => {
  return (
    <>
      <div className="min-h-screen font-sans">
        <Hero />
        <WhyChooseUs />
        <Packages />
        <Testimonials />
        <About />
        <Partners />
        <FloatingChatWidget />
      </div>
    </>
  );
};

export default Index;
