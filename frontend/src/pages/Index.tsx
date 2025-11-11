// src/pages/Index.tsx
import Hero from "@/components/Hero";
import WhyChooseUs from "@/components/WhyChooseUs";
import Packages from "@/pages/Packages";
import Testimonials from "@/components/Testimonials";
import About from "@/components/About";
import Partners from "@/components/Partners";
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
