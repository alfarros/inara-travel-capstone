import { Card } from "@/components/ui/card";
import { Shield, Heart, Award } from "lucide-react";
import founderPhoto from "/public/assets/founder-photo.jpg";

const About = () => {
  return (
    <section className="py-20 px-4 bg-muted/30">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16 animate-fade-in-up">
          <h2 className="text-3xl md:text-5xl font-serif font-bold text-primary mb-4">
            Tentang Inara Travel
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Memulai dengan niat tulus untuk melayani ummat
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left: Story */}
          <div className="space-y-6 animate-fade-in-up">
            <div className="prose prose-lg">
              <p className="text-foreground leading-relaxed">
                <strong className="text-primary">Inara Travel</strong> didirikan
                pada tahun 2025 dengan niat tulus untuk membantu umat Muslim
                menjalankan ibadah umrah dan haji dengan nyaman, aman, dan
                sesuai tuntunan Rasulullah SAW.
              </p>
              <p className="text-muted-foreground leading-relaxed">
                Meskipun kami adalah perusahaan yang baru memulai, tim kami
                terdiri dari profesional berpengalaman di bidang travel ibadah
                yang memiliki dedikasi tinggi dalam memberikan pelayanan
                terbaik.
              </p>
            </div>

            {/* Values */}
            <div className="grid grid-cols-1 gap-4 pt-4">
              {[
                { icon: Heart, text: "Pelayanan dengan hati dan keikhlasan" },
                {
                  icon: Shield,
                  text: "Sedang proses pengurusan izin resmi Kemenag",
                },
                {
                  icon: Award,
                  text: "Komitmen untuk terus berkembang melayani ummat",
                },
              ].map((item, index) => {
                const Icon = item.icon;
                return (
                  <div key={index} className="flex items-center gap-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <Icon className="w-5 h-5 text-primary" />
                    </div>
                    <span className="text-foreground">{item.text}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right: Founder Profile */}
          <div className="animate-scale-in">
            <Card className="overflow-hidden shadow-large border-none">
              <div className="relative">
                <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-primary" />
                <div className="relative pt-12 pb-8 px-8 text-center">
                  <div className="w-32 h-32 mx-auto mb-6 rounded-full overflow-hidden ring-4 ring-card shadow-medium">
                    <img
                      src={founderPhoto}
                      alt="H. Abdullah Rahman"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <h3 className="text-2xl font-serif font-bold text-primary mb-2">
                    H. Abdullah Rahman
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    Founder & CEO Inara Travel
                  </p>
                  <blockquote className="text-sm italic text-foreground/80 leading-relaxed border-l-4 border-accent pl-4 text-left">
                    "Kami memulai dengan sederhana, tapi dengan tekad kuat untuk
                    memberikan pengalaman umrah terbaik bagi setiap jamaah.
                    InsyaAllah, dengan izin Allah dan dukungan Anda, kami akan
                    terus berkembang melayani ummat."
                  </blockquote>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-12 text-center">
          <Card className="bg-accent/10 border-accent/30 p-6 inline-block">
            <p className="text-sm text-foreground">
              <strong>Catatan:</strong> Inara Travel sedang dalam proses
              pengurusan izin resmi dari Kementerian Agama RI. Kami berkomitmen
              untuk segera menyelesaikan seluruh persyaratan administrasi demi
              kenyamanan dan kepercayaan Anda.
            </p>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default About;
