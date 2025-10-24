const partners = [
  { name: "Bank Syariah Indonesia", logo: "BSI" },
  { name: "Garuda Indonesia", logo: "GA" },
  { name: "Saudi Airlines", logo: "SV" },
  { name: "Bank Muamalat", logo: "BMI" },
  { name: "Mandiri Syariah", logo: "MS" },
  { name: "Hotel Partner", logo: "HP" },
];

const Partners = () => {
  return (
    <section className="py-20 px-4 bg-background">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16 animate-fade-in-up">
          <h2 className="text-3xl md:text-5xl font-serif font-bold text-primary mb-4">
            Mitra Terpercaya
          </h2>
          <p className="text-lg text-muted-foreground">
            Bekerja sama dengan institusi terpercaya untuk memberikan layanan terbaik
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">
          {partners.map((partner, index) => (
            <div
              key={index}
              className="flex items-center justify-center p-6 bg-card rounded-lg shadow-soft hover:shadow-medium transition-all duration-300 hover:-translate-y-1 animate-scale-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-3 bg-gradient-primary rounded-full flex items-center justify-center">
                  <span className="text-primary-foreground font-bold text-sm">
                    {partner.logo}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground font-medium">
                  {partner.name}
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-12 text-sm text-muted-foreground">
          <p>Dan masih banyak mitra lainnya yang siap melayani kebutuhan ibadah Anda</p>
        </div>
      </div>
    </section>
  );
};

export default Partners;
